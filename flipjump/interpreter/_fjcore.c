/*
 * _fjcore - the native FlipJump interpreter engine.
 *
 * Implements a Memory object (segment-aware, lazily-allocated paged memory) and a run()
 * method executing the FlipJump fetch-flip-jump loop in C. The semantics exactly mirror
 * the pure-Python fast loop in fjm_run.py (which mirrors the featured loop):
 *   - per-op order: read flip-word, output-check, input-check, flip, read jump-word,
 *     looping/null-ip termination checks, jump.
 *   - reads of in-segment untouched words are 0; reads outside any segment either
 *     terminate the run (garbage_stop) or read 0 (continue).
 *   - IO is routed through the Python io_device's read_bit/write_bit callbacks.
 *
 * Only the run-loop lives in C; the .fjm parsing, devices and debugger stay in Python.
 */

#define PY_SSIZE_T_CLEAN
/* the stable ABI (abi3): one wheel per platform/arch covers every CPython >= 3.10 */
#ifndef Py_LIMITED_API
#define Py_LIMITED_API 0x030A0000
#endif
#include <Python.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#endif

/* a monotonic wall clock in seconds - matches the python reference pause-timer, which uses
   wall time around blocking IO reads (C clock() is process-CPU time on POSIX: ~0 while
   blocked on input, which would under-report the paused time there). */
static double monotonic_seconds(void)
{
#ifdef _WIN32
    LARGE_INTEGER frequency, counter;
    QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)frequency.QuadPart;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
#endif
}

#define PAGE_BITS 14
#define PAGE_WORDS (1ull << PAGE_BITS) /* 16K words, 128KB per page */
#define PAGE_MASK (PAGE_WORDS - 1)

/* how often to check for signals (Ctrl+C): every 2^18 ops */
#define SIGNAL_CHECK_MASK 0x3FFFFull

/* flat-storage mode: programs whose segments all end below a word-count limit (and with
   w<=32, so bit 63 is free to mark out-of-segment words) use one dense array instead of
   the page table - removing the page lookup from the serial jump-address chain.
   the limit is the Memory(flat_max_words=...) parameter, else the FLIPJUMP_FLAT_MAX_WORDS
   environment variable, else this default. raising it trades startup time + footprint
   (the array is sentinel-filled: RSS = 8 bytes x span, fill ~0.1s/GB) for flat-path speed;
   the per-op cost is unaffected by the limit's value. */
#define FLAT_MAX_WORDS_DEFAULT (1ull << 23) /* 8M words, 64MB */
#define GARBAGE_SENTINEL (1ull << 63)

/* termination causes (mapped to TerminationCause in fjm_run.py) */
#define TERM_LOOPING 0
#define TERM_EOF 1
#define TERM_NULL_IP 2
#define TERM_MEMORY_ERROR 3

typedef struct {
    uint64_t* words;       /* PAGE_WORDS lazily-calloc'd words (masked to w bits) */
    uint64_t valid_start;  /* page-local fast-path valid range [valid_start, valid_end) */
    uint64_t valid_end;
} Page;

typedef struct {
    uint64_t key_plus1; /* page_index + 1; 0 marks an empty slot */
    Page* page;
} Slot;

typedef struct {
    uint64_t start; /* word address */
    uint64_t end;   /* word address (exclusive) */
} SegmentRange;

typedef struct {
    PyObject_HEAD

    int w;             /* memory width (8/16/32/64) */
    int ww;            /* log2(w) */
    uint64_t word_mask;
    int garbage_stop;  /* 1: out-of-segment access terminates; 0: reads 0 and continues */

    Slot* slots;       /* open-addressing page table */
    uint64_t slot_count; /* power of two */
    uint64_t slots_used;

    /* direct-mapped page cache (keyed by the page-index low bits): the ip/jump page and
       the wandering flip-target pages coexist instead of evicting each other. */
    uint64_t page_cache_key_plus1[16];
    Page* page_cache_page[16];

    SegmentRange* segments; /* sorted, merged */
    Py_ssize_t segment_count;
    Py_ssize_t segment_capacity;
    int segments_sorted;

    /* flat-storage mode (built at the first run when eligible; NULL = paged mode) */
    uint64_t* flat;
    uint64_t flat_count;
    uint64_t flat_max_words; /* constructor override; 0 = use the env var / default */
    int storage_decided;

    int mem_error;            /* set when garbage_stop fired */
    uint64_t error_bit_address;

    unsigned long long last_run_op_count; /* op count of the last run (also on exceptions) */
    double last_run_paused_seconds;       /* IO-paused seconds of the last run (also on exceptions) */
} MemoryObject;

/* ---------------------------------------------------------------- pages */

static int mem_grow_slots(MemoryObject* m)
{
    uint64_t new_count = m->slot_count ? m->slot_count * 2 : 64;
    Slot* new_slots = (Slot*)calloc((size_t)new_count, sizeof(Slot));
    if (!new_slots) {
        PyErr_NoMemory();
        return -1;
    }
    for (uint64_t i = 0; i < m->slot_count; i++) {
        if (m->slots[i].key_plus1) {
            uint64_t h = (m->slots[i].key_plus1 * 0x9E3779B97F4A7C15ull) & (new_count - 1);
            while (new_slots[h].key_plus1) {
                h = (h + 1) & (new_count - 1);
            }
            new_slots[h] = m->slots[i];
        }
    }
    free(m->slots);
    m->slots = new_slots;
    m->slot_count = new_count;
    return 0;
}

static int segment_compare(const void* a, const void* b)
{
    const SegmentRange* sa = (const SegmentRange*)a;
    const SegmentRange* sb = (const SegmentRange*)b;
    if (sa->start < sb->start) return -1;
    if (sa->start > sb->start) return 1;
    return 0;
}

static void mem_ensure_segments_sorted(MemoryObject* m)
{
    if (!m->segments_sorted) {
        qsort(m->segments, (size_t)m->segment_count, sizeof(SegmentRange), segment_compare);
        m->segments_sorted = 1;
    }
}

/* is the word-address inside any segment? (binary search) */
static int word_is_valid(MemoryObject* m, uint64_t word_address)
{
    Py_ssize_t lo = 0, hi = m->segment_count - 1;
    mem_ensure_segments_sorted(m);
    while (lo <= hi) {
        Py_ssize_t mid = (lo + hi) / 2;
        if (word_address < m->segments[mid].start) {
            hi = mid - 1;
        } else if (word_address >= m->segments[mid].end) {
            lo = mid + 1;
        } else {
            return 1;
        }
    }
    return 0;
}

/* compute the page's fast-path valid range: the first segment-intersection with the page */
static void page_compute_validity(MemoryObject* m, uint64_t page_index, Page* page)
{
    uint64_t page_start = page_index << PAGE_BITS;
    uint64_t page_end = page_start + PAGE_WORDS;
    page->valid_start = 0;
    page->valid_end = 0;
    mem_ensure_segments_sorted(m);
    for (Py_ssize_t i = 0; i < m->segment_count; i++) {
        uint64_t s = m->segments[i].start, e = m->segments[i].end;
        if (e <= page_start || s >= page_end) {
            continue;
        }
        page->valid_start = (s > page_start) ? (s - page_start) : 0;
        page->valid_end = (e < page_end) ? (e - page_start) : PAGE_WORDS;
        return; /* additional intersections are handled by the slow word_is_valid path */
    }
}

static Page* mem_get_page(MemoryObject* m, uint64_t page_index)
{
    uint64_t key = page_index + 1;
    uint64_t cache_slot = page_index & 15;
    uint64_t h;
    if (key == m->page_cache_key_plus1[cache_slot]) {
        return m->page_cache_page[cache_slot];
    }
    if (m->slots_used * 2 >= m->slot_count) {
        if (mem_grow_slots(m) < 0) {
            return NULL;
        }
    }
    h = (key * 0x9E3779B97F4A7C15ull) & (m->slot_count - 1);
    while (m->slots[h].key_plus1) {
        if (m->slots[h].key_plus1 == key) {
            m->page_cache_key_plus1[cache_slot] = key;
            m->page_cache_page[cache_slot] = m->slots[h].page;
            return m->slots[h].page;
        }
        h = (h + 1) & (m->slot_count - 1);
    }
    /* allocate a new page */
    {
        Page* page = (Page*)malloc(sizeof(Page));
        if (!page) {
            PyErr_NoMemory();
            return NULL;
        }
        page->words = (uint64_t*)calloc(PAGE_WORDS, sizeof(uint64_t));
        if (!page->words) {
            free(page);
            PyErr_NoMemory();
            return NULL;
        }
        page_compute_validity(m, page_index, page);
        m->slots[h].key_plus1 = key;
        m->slots[h].page = page;
        m->slots_used++;
        m->page_cache_key_plus1[cache_slot] = key;
        m->page_cache_page[cache_slot] = page;
        return page;
    }
}

/* validity check for the interpreted program's accesses.
   returns 1 if ok to access; 0 if the run must terminate with a memory error (sets m->mem_error),
   -1 on python error. in continue-mode invalid accesses are allowed (read 0 / write). */
static inline int access_check(MemoryObject* m, Page* page, uint64_t word_address)
{
    uint64_t off = word_address & PAGE_MASK;
    if (off >= page->valid_start && off < page->valid_end) {
        return 1;
    }
    if (word_is_valid(m, word_address)) {
        return 1;
    }
    if (!m->garbage_stop) {
        return 1;
    }
    m->mem_error = 1;
    m->error_bit_address = word_address << m->ww;
    return 0;
}

static inline int flat_garbage(MemoryObject* m, uint64_t word_address)
{
    if (!m->garbage_stop) {
        return 1; /* continue-mode reads 0 (flat mode requires garbage_stop, but be safe) */
    }
    m->mem_error = 1;
    m->error_bit_address = word_address << m->ww;
    return 0;
}

/* read the w-bit word at the word-address. returns 0 on success, -1 on stop (mem_error or
   python error - distinguish via m->mem_error). */
static inline int mem_read_word(MemoryObject* m, uint64_t word_address, uint64_t* out)
{
    Page* page;
    if (m->flat) {
        uint64_t value;
        if (word_address >= m->flat_count) {
            if (!flat_garbage(m, word_address)) {
                return -1;
            }
            *out = 0;
            return 0;
        }
        value = m->flat[word_address];
        if (value & GARBAGE_SENTINEL) {
            if (!flat_garbage(m, word_address)) {
                return -1;
            }
            value = 0;
        }
        *out = value;
        return 0;
    }
    page = mem_get_page(m, word_address >> PAGE_BITS);
    if (!page) {
        return -1;
    }
    if (!access_check(m, page, word_address)) {
        return -1;
    }
    *out = page->words[word_address & PAGE_MASK];
    return 0;
}

/* flip the bit at the bit-address. returns 0 on success, -1 on stop. */
static inline int mem_flip_bit(MemoryObject* m, uint64_t bit_address)
{
    uint64_t word_address = bit_address >> m->ww;
    Page* page;
    if (m->flat) {
        uint64_t value;
        if (word_address >= m->flat_count) {
            return flat_garbage(m, word_address) ? 0 : -1;
        }
        value = m->flat[word_address];
        if (value & GARBAGE_SENTINEL) {
            if (!flat_garbage(m, word_address)) {
                return -1;
            }
            value = 0; /* continue-mode: the garbage word becomes a live 0 */
        }
        m->flat[word_address] = value ^ (1ull << (bit_address & (uint64_t)(m->w - 1)));
        return 0;
    }
    page = mem_get_page(m, word_address >> PAGE_BITS);
    if (!page) {
        return -1;
    }
    if (!access_check(m, page, word_address)) {
        return -1;
    }
    page->words[word_address & PAGE_MASK] ^= 1ull << (bit_address & (uint64_t)(m->w - 1));
    return 0;
}

/* set/clear the bit at the bit-address. returns 0 on success, -1 on stop. */
static inline int mem_write_bit(MemoryObject* m, uint64_t bit_address, int bit_value)
{
    uint64_t word_address = bit_address >> m->ww;
    uint64_t bit = 1ull << (bit_address & (uint64_t)(m->w - 1));
    Page* page;
    if (m->flat) {
        uint64_t value;
        if (word_address >= m->flat_count) {
            return flat_garbage(m, word_address) ? 0 : -1;
        }
        value = m->flat[word_address];
        if (value & GARBAGE_SENTINEL) {
            if (!flat_garbage(m, word_address)) {
                return -1;
            }
            value = 0;
        }
        m->flat[word_address] = bit_value ? (value | bit) : (value & ~bit);
        return 0;
    }
    page = mem_get_page(m, word_address >> PAGE_BITS);
    if (!page) {
        return -1;
    }
    if (!access_check(m, page, word_address)) {
        return -1;
    }
    if (bit_value) {
        page->words[word_address & PAGE_MASK] |= bit;
    } else {
        page->words[word_address & PAGE_MASK] &= ~bit;
    }
    return 0;
}

/* read the (possibly unaligned) w-bit word at the bit-address. */
static inline int mem_get_word_unaligned(MemoryObject* m, uint64_t bit_address, uint64_t* out)
{
    uint64_t word_address = bit_address >> m->ww;
    uint64_t bit_offset = bit_address & (uint64_t)(m->w - 1);
    uint64_t lsw, msw;
    if (bit_offset == 0) {
        return mem_read_word(m, word_address, out);
    }
    if (word_address == m->word_mask) {
        /* an unaligned read whose high word would wrap past the top of the address space -
           the python reference terminates with a memory error here */
        m->mem_error = 1;
        m->error_bit_address = bit_address;
        return -1;
    }
    if (mem_read_word(m, word_address, &lsw) < 0) {
        return -1;
    }
    if (mem_read_word(m, word_address + 1, &msw) < 0) {
        return -1;
    }
    *out = ((lsw >> bit_offset) | (msw << (m->w - bit_offset))) & m->word_mask;
    return 0;
}

/* the effective flat-storage span limit: the constructor parameter, else the
   FLIPJUMP_FLAT_MAX_WORDS environment variable, else the built-in default. */
static uint64_t mem_flat_words_limit(MemoryObject* m)
{
    if (m->flat_max_words) {
        return m->flat_max_words;
    }
    {
        const char* env_limit = getenv("FLIPJUMP_FLAT_MAX_WORDS");
        if (env_limit && env_limit[0]) {
            uint64_t limit = strtoull(env_limit, NULL, 0);
            if (limit) {
                return limit;
            }
        }
    }
    return FLAT_MAX_WORDS_DEFAULT;
}

/* decide the storage mode (once, at the first run): build the flat array when eligible -
   w<=32 (bit 63 is free for the garbage sentinel), garbage-stop mode, and all segments
   ending below the flat-words limit. copies the already-loaded page data in, then frees
   the pages. a failed flat-array allocation falls back to paged mode (never an error). */
static int mem_decide_storage(MemoryObject* m)
{
    uint64_t max_end = 0, i;
    Py_ssize_t seg;
    if (m->storage_decided) {
        return 0;
    }
    m->storage_decided = 1;

    if (m->w > 32 || !m->garbage_stop || m->segment_count == 0) {
        return 0; /* paged */
    }
    {
        const char* no_flat = getenv("FLIPJUMP_NO_FLAT");
        if (no_flat && no_flat[0] == '1') {
            return 0; /* paged (forced - for A/B benchmarking and debugging) */
        }
    }
    for (seg = 0; seg < m->segment_count; seg++) {
        if (m->segments[seg].end > max_end) {
            max_end = m->segments[seg].end;
        }
    }
    if (max_end > mem_flat_words_limit(m)) {
        return 0; /* paged */
    }

    {
        /* deterministic allocation-failure injection for the fallback-path tests
           (a real flat-array OOM is not safely reproducible across platforms) */
        const char* simulate_alloc_fail = getenv("FLIPJUMP_TEST_FLAT_ALLOC_FAIL");
        if (simulate_alloc_fail && simulate_alloc_fail[0] == '1') {
            return 0; /* paged */
        }
    }
    m->flat = (uint64_t*)malloc((size_t)max_end * sizeof(uint64_t));
    if (!m->flat) {
        return 0; /* paged fallback - the program still runs, just slower */
    }
    m->flat_count = max_end;
    for (i = 0; i < max_end; i++) {
        m->flat[i] = GARBAGE_SENTINEL;
    }
    for (seg = 0; seg < m->segment_count; seg++) {
        memset(m->flat + m->segments[seg].start, 0,
               (size_t)(m->segments[seg].end - m->segments[seg].start) * sizeof(uint64_t));
    }
    /* copy the loaded data: each allocated page, intersected with each segment */
    if (m->slots) {
        for (i = 0; i < m->slot_count; i++) {
            uint64_t page_start, page_end;
            if (!m->slots[i].key_plus1) {
                continue;
            }
            page_start = (m->slots[i].key_plus1 - 1) << PAGE_BITS;
            page_end = page_start + PAGE_WORDS;
            for (seg = 0; seg < m->segment_count; seg++) {
                uint64_t lo = (m->segments[seg].start > page_start) ? m->segments[seg].start : page_start;
                uint64_t hi = (m->segments[seg].end < page_end) ? m->segments[seg].end : page_end;
                if (lo < hi) {
                    memcpy(m->flat + lo, m->slots[i].page->words + (lo - page_start),
                           (size_t)(hi - lo) * sizeof(uint64_t));
                }
            }
            free(m->slots[i].page->words);
            free(m->slots[i].page);
        }
        free(m->slots);
        m->slots = NULL;
        m->slot_count = 0;
        m->slots_used = 0;
        memset(m->page_cache_key_plus1, 0, sizeof(m->page_cache_key_plus1));
        memset(m->page_cache_page, 0, sizeof(m->page_cache_page));
    }
    return 0;
}

/* ---------------------------------------------------------------- Memory type */

static int Memory_init(PyObject* op, PyObject* args, PyObject* kwds)
{
    MemoryObject* self = (MemoryObject*)op;
    static char* kwlist[] = {"memory_width", "garbage_stop", "flat_max_words", NULL};
    int w, garbage_stop = 1;
    unsigned long long flat_max_words = 0; /* 0: use FLIPJUMP_FLAT_MAX_WORDS / the default */
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i|pK", kwlist, &w, &garbage_stop, &flat_max_words)) {
        return -1;
    }
    if (w != 8 && w != 16 && w != 32 && w != 64) {
        PyErr_SetString(PyExc_ValueError, "memory_width must be 8, 16, 32 or 64");
        return -1;
    }
    self->w = w;
    self->ww = (w == 8) ? 3 : (w == 16) ? 4 : (w == 32) ? 5 : 6;
    self->word_mask = (w == 64) ? ~0ull : ((1ull << w) - 1);
    self->garbage_stop = garbage_stop;
    self->slots = NULL;
    self->slot_count = 0;
    self->slots_used = 0;
    memset(self->page_cache_key_plus1, 0, sizeof(self->page_cache_key_plus1));
    memset(self->page_cache_page, 0, sizeof(self->page_cache_page));
    self->segments = NULL;
    self->segment_count = 0;
    self->segment_capacity = 0;
    self->segments_sorted = 1;
    self->flat = NULL;
    self->flat_count = 0;
    self->flat_max_words = flat_max_words;
    self->storage_decided = 0;
    self->mem_error = 0;
    self->error_bit_address = 0;
    self->last_run_op_count = 0;
    self->last_run_paused_seconds = 0.0;
    return 0;
}

static void Memory_dealloc(PyObject* op)
{
    MemoryObject* self = (MemoryObject*)op;
    PyTypeObject* type = Py_TYPE(op);
    freefunc tp_free;
    if (self->slots) {
        for (uint64_t i = 0; i < self->slot_count; i++) {
            if (self->slots[i].key_plus1) {
                free(self->slots[i].page->words);
                free(self->slots[i].page);
            }
        }
        free(self->slots);
    }
    free(self->flat);
    free(self->segments);
    tp_free = (freefunc)PyType_GetSlot(type, Py_tp_free);
    tp_free(op);
    Py_DECREF(type); /* heap types own a reference from their instances */
}

static PyObject* Memory_add_segment(MemoryObject* self, PyObject* args)
{
    unsigned long long start_word, length_words;
    if (!PyArg_ParseTuple(args, "KK", &start_word, &length_words)) {
        return NULL;
    }
    /* reject overflowing ranges - a wrapped end would corrupt the flat-array build
       (memset/memcpy with a wild size) and the validity binary-search invariants */
    if (start_word + length_words < start_word) {
        PyErr_SetString(PyExc_ValueError, "segment range overflows the 64-bit word-address space");
        return NULL;
    }
    if (self->segment_count == self->segment_capacity) {
        Py_ssize_t new_capacity = self->segment_capacity ? self->segment_capacity * 2 : 8;
        SegmentRange* new_segments = (SegmentRange*)realloc(self->segments, (size_t)new_capacity * sizeof(SegmentRange));
        if (!new_segments) {
            return PyErr_NoMemory();
        }
        self->segments = new_segments;
        self->segment_capacity = new_capacity;
    }
    self->segments[self->segment_count].start = start_word;
    self->segments[self->segment_count].end = start_word + length_words;
    self->segment_count++;
    self->segments_sorted = 0;
    /* validity ranges of already-allocated pages may change - recompute them */
    if (self->slots) {
        for (uint64_t i = 0; i < self->slot_count; i++) {
            if (self->slots[i].key_plus1) {
                page_compute_validity(self, self->slots[i].key_plus1 - 1, self->slots[i].page);
            }
        }
    }
    Py_RETURN_NONE;
}

static PyObject* Memory_set_word(MemoryObject* self, PyObject* args)
{
    unsigned long long word_address, value;
    Page* page;
    if (!PyArg_ParseTuple(args, "KK", &word_address, &value)) {
        return NULL;
    }
    if (self->flat) {
        if (word_address >= self->flat_count) {
            PyErr_SetString(PyExc_ValueError, "set_word address is beyond the flat-storage span");
            return NULL;
        }
        self->flat[word_address] = value & self->word_mask;
        Py_RETURN_NONE;
    }
    page = mem_get_page(self, word_address >> PAGE_BITS);
    if (!page) {
        return NULL;
    }
    page->words[word_address & PAGE_MASK] = value & self->word_mask;
    Py_RETURN_NONE;
}

static PyObject* Memory_get_word(MemoryObject* self, PyObject* args)
{
    unsigned long long word_address;
    Page* page;
    if (!PyArg_ParseTuple(args, "K", &word_address)) {
        return NULL;
    }
    if (self->flat) {
        uint64_t value = (word_address < self->flat_count) ? self->flat[word_address] : 0;
        return PyLong_FromUnsignedLongLong((value & GARBAGE_SENTINEL) ? 0 : value);
    }
    page = mem_get_page(self, word_address >> PAGE_BITS);
    if (!page) {
        return NULL;
    }
    return PyLong_FromUnsignedLongLong(page->words[word_address & PAGE_MASK]);
}

/* bulk-load: set_words(start_word_address, values_list) */
static PyObject* Memory_set_words(MemoryObject* self, PyObject* args)
{
    unsigned long long start_word;
    PyObject* values;
    Py_ssize_t count, i;
    if (!PyArg_ParseTuple(args, "KO", &start_word, &values)) {
        return NULL;
    }
    count = PySequence_Size(values);
    if (count < 0) {
        return NULL;
    }
    Py_INCREF(values);
    for (i = 0; i < count; i++) {
        unsigned long long value;
        Page* page;
        PyObject* item = PySequence_GetItem(values, i);
        if (!item) {
            Py_DECREF(values);
            return NULL;
        }
        value = PyLong_AsUnsignedLongLong(item);
        Py_DECREF(item);
        if (value == (unsigned long long)-1 && PyErr_Occurred()) {
            Py_DECREF(values);
            return NULL;
        }
        if (self->flat) {
            if ((uint64_t)(start_word + i) >= self->flat_count) {
                Py_DECREF(values);
                PyErr_SetString(PyExc_ValueError, "set_words address is beyond the flat-storage span");
                return NULL;
            }
            self->flat[start_word + i] = value & self->word_mask;
            continue;
        }
        page = mem_get_page(self, (start_word + i) >> PAGE_BITS);
        if (!page) {
            Py_DECREF(values);
            return NULL;
        }
        page->words[(start_word + i) & PAGE_MASK] = value & self->word_mask;
    }
    Py_DECREF(values);
    Py_RETURN_NONE;
}

#define CAUSE_PYTHON_ERROR (-2)

/* the dedicated flat-storage run loop - the common fast case (no last-ops ring, flat
   memory): all paged-mode and ring branches are out of the per-op path.
   returns the termination cause, or CAUSE_PYTHON_ERROR with the python error set. */
static int run_flat_loop(MemoryObject* self, PyObject* read_bit, PyObject* write_bit, PyObject* eof_exception_type,
                         uint64_t start_ip, uint64_t* ops_out, double* paused_seconds_out)
{
    const uint64_t width = (uint64_t)self->w;
    const uint64_t ww = (uint64_t)self->ww;
    const uint64_t bit_mask = width - 1;
    const uint64_t dw = 2 * width;
    const uint64_t out1 = dw + 1;
    const uint64_t in_addr = 3 * width + ww + 1; /* 3w + #w */
    const uint64_t in_lo_exclusive = in_addr - dw;
    uint64_t* const flat = self->flat;
    const uint64_t flat_count = self->flat_count;

    uint64_t ip = start_ip, ops = 0;
    int cause = CAUSE_PYTHON_ERROR;

    self->mem_error = 0;
    for (;;) {
        uint64_t word_address, f, flip_word_address, flip_value, j;

        if ((ops & SIGNAL_CHECK_MASK) == SIGNAL_CHECK_MASK) {
            self->last_run_op_count = ops;
            if (PyErr_CheckSignals() < 0) {
                goto done;
            }
        }

        /* read flip word */
        if (ip & bit_mask) {
            if (mem_get_word_unaligned(self, ip, &f) < 0) {
                goto memory_error;
            }
            word_address = (uint64_t)-2; /* the jump word is read the slow way below */
        } else {
            word_address = ip >> ww;
            if (word_address + 1 >= flat_count) {
                if (!flat_garbage(self, word_address)) {
                    goto memory_error;
                }
                f = 0;
            } else {
                f = flat[word_address];
                if (f & GARBAGE_SENTINEL) {
                    if (!flat_garbage(self, word_address)) {
                        goto memory_error;
                    }
                    f = 0;
                }
            }
        }

        /* handle output */
        if (f <= out1 && f >= dw) {
            PyObject* result = PyObject_CallFunctionObjArgs(write_bit, (f == out1) ? Py_True : Py_False, NULL);
            if (!result) {
                goto done;
            }
            Py_DECREF(result);
        }

        /* handle input */
        if (ip <= in_addr && ip > in_lo_exclusive) {
            PyObject* result;
            int bit_value;
            double io_start = monotonic_seconds();
            result = PyObject_CallNoArgs(read_bit);
            *paused_seconds_out += monotonic_seconds() - io_start;
            if (!result) {
                if (PyErr_ExceptionMatches(eof_exception_type)) {
                    PyErr_Clear();
                    cause = TERM_EOF;
                    goto done;
                }
                goto done;
            }
            bit_value = PyObject_IsTrue(result);
            Py_DECREF(result);
            if (bit_value < 0) {
                goto done;
            }
            if (mem_write_bit(self, in_addr, bit_value) < 0) {
                goto memory_error;
            }
        }

        /* FLIP! */
        flip_word_address = f >> ww;
        if (flip_word_address >= flat_count) {
            if (!flat_garbage(self, flip_word_address)) {
                goto memory_error;
            }
        } else {
            flip_value = flat[flip_word_address];
            if (flip_value & GARBAGE_SENTINEL) {
                if (!flat_garbage(self, flip_word_address)) {
                    goto memory_error;
                }
                flip_value = 0;
            }
            flat[flip_word_address] = flip_value ^ (1ull << (f & bit_mask));
        }

        /* read jump word (after the flip - the flip may modify it) */
        if (word_address + 1 < flat_count) {
            j = flat[word_address + 1];
            if (j & GARBAGE_SENTINEL) {
                if (!flat_garbage(self, word_address + 1)) {
                    goto memory_error;
                }
                j = 0;
            }
        } else if (mem_get_word_unaligned(self, ip + width, &j) < 0) {
            goto memory_error;
        }
        ops++;

        /* check finish? */
        if (j == ip && !(f >= ip && f - ip < dw)) {
            cause = TERM_LOOPING;
            goto done;
        }
        if (j < dw) {
            cause = TERM_NULL_IP;
            goto done;
        }

        /* JUMP! */
        ip = j;
    }

memory_error:
    if (self->mem_error) {
        self->mem_error = 0;
        cause = TERM_MEMORY_ERROR;
    }
done:
    self->last_run_op_count = ops;
    self->last_run_paused_seconds = *paused_seconds_out;
    *ops_out = ops;
    return cause;
}

/* build the (cause, op_count, error_bit_address_or_None, last_ops, paused_seconds) result tuple.
   takes ownership of last_ops_ring (frees it). */
static PyObject* build_run_result(MemoryObject* self, int cause, uint64_t ops, uint64_t* last_ops_ring,
                                  Py_ssize_t last_ops_length, uint64_t ring_writes, double paused_seconds)
{
    PyObject* last_ops_list = PyList_New(0);
    PyObject* error_address;
    if (!last_ops_list) {
        free(last_ops_ring);
        return NULL;
    }
    (void)ops;
    if (last_ops_ring) {
        /* emit in execution order: oldest first */
        uint64_t total = (ring_writes < (uint64_t)last_ops_length) ? ring_writes : (uint64_t)last_ops_length;
        uint64_t ring_pos = ring_writes % (uint64_t)last_ops_length;
        uint64_t start = (ring_pos + (uint64_t)last_ops_length - total) % (uint64_t)last_ops_length;
        for (uint64_t i = 0; i < total; i++) {
            PyObject* address = PyLong_FromUnsignedLongLong(last_ops_ring[(start + i) % (uint64_t)last_ops_length]);
            if (!address || PyList_Append(last_ops_list, address) < 0) {
                Py_XDECREF(address);
                Py_DECREF(last_ops_list);
                free(last_ops_ring);
                return NULL;
            }
            Py_DECREF(address);
        }
        free(last_ops_ring);
    }
    if (cause == TERM_MEMORY_ERROR) {
        error_address = PyLong_FromUnsignedLongLong(self->error_bit_address);
    } else {
        error_address = Py_None;
        Py_INCREF(Py_None);
    }
    if (!error_address) {
        Py_DECREF(last_ops_list);
        return NULL;
    }
    return Py_BuildValue("iKNNd", cause, (unsigned long long)ops, error_address, last_ops_list, paused_seconds);
}

/* the run loop.
   run(read_bit, write_bit, eof_exception_type, last_ops_length=0, start_ip=0)
   -> (termination_cause, op_count, error_bit_address_or_None, last_ops_list, paused_seconds) */
static PyObject* Memory_run(MemoryObject* self, PyObject* args, PyObject* kwds)
{
    static char* kwlist[] = {"read_bit", "write_bit", "eof_exception_type", "last_ops_length", "start_ip", NULL};
    PyObject* read_bit;
    PyObject* write_bit;
    PyObject* eof_exception_type;
    Py_ssize_t last_ops_length = 0;
    unsigned long long start_ip = 0;

    uint64_t ip, ops = 0;
    uint64_t* last_ops_ring = NULL;
    uint64_t ring_writes = 0;
    int cause = -1;
    double paused_seconds = 0.0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOO|nK", kwlist, &read_bit, &write_bit, &eof_exception_type,
                                     &last_ops_length, &start_ip)) {
        return NULL;
    }

    if (mem_decide_storage(self) < 0) {
        return NULL;
    }

    if (self->flat && last_ops_length == 0) {
        /* the common fast case gets the dedicated loop (no ring, no paged branches) */
        uint64_t fast_ops = 0;
        double fast_paused = 0.0;
        int fast_cause =
            run_flat_loop(self, read_bit, write_bit, eof_exception_type, start_ip, &fast_ops, &fast_paused);
        if (fast_cause == CAUSE_PYTHON_ERROR) {
            return NULL;
        }
        return build_run_result(self, fast_cause, fast_ops, NULL, 0, 0, fast_paused);
    }

    if (last_ops_length > 0) {
        last_ops_ring = (uint64_t*)calloc((size_t)last_ops_length, sizeof(uint64_t));
        if (!last_ops_ring) {
            return PyErr_NoMemory();
        }
    }

    {
        const uint64_t width = (uint64_t)self->w;
        const uint64_t ww = (uint64_t)self->ww;
        const uint64_t bit_mask = width - 1;
        const uint64_t dw = 2 * width;
        const uint64_t out1 = dw + 1;
        const uint64_t in_addr = 3 * width + ww + 1; /* 3w + #w */
        const uint64_t in_lo_exclusive = in_addr - dw;
        uint64_t* const flat = self->flat;
        const uint64_t flat_count = self->flat_count;

        ip = start_ip;
        self->mem_error = 0;
        self->last_run_op_count = 0;

        for (;;) {
            uint64_t f, j, bit_offset;
            Page* op_page = NULL; /* the page holding both op words (aligned, non-straddling ops) */
            uint64_t op_offset = 0;
            uint64_t* op_flat_jump = NULL; /* flat mode: where this op's jump word lives */

            if ((ops & SIGNAL_CHECK_MASK) == SIGNAL_CHECK_MASK) {
                self->last_run_op_count = ops;
                if (PyErr_CheckSignals() < 0) {
                    goto python_error;
                }
            }

            if (last_ops_ring) {
                last_ops_ring[ring_writes % (uint64_t)last_ops_length] = ip;
                ring_writes++;
            }

            /* read flip word - flat mode reads it straight out of the dense array; paged
               mode shares one page lookup for the op's two words (unless the op straddles
               a page boundary, or the ip is unaligned) */
            bit_offset = ip & bit_mask;
            if (flat && !bit_offset) {
                uint64_t word_address = ip >> ww;
                if (word_address + 1 >= flat_count) {
                    if (mem_read_word(self, word_address, &f) < 0) {
                        goto memory_or_python_error;
                    }
                } else {
                    f = flat[word_address];
                    if (f & GARBAGE_SENTINEL) {
                        if (!flat_garbage(self, word_address)) {
                            goto memory_or_python_error;
                        }
                        f = 0;
                    }
                    op_flat_jump = flat + word_address + 1;
                }
            } else if (bit_offset) {
                if (mem_get_word_unaligned(self, ip, &f) < 0) {
                    goto memory_or_python_error;
                }
            } else {
                uint64_t word_address = ip >> ww;
                op_offset = word_address & PAGE_MASK;
                if (op_offset != PAGE_MASK) {
                    op_page = mem_get_page(self, word_address >> PAGE_BITS);
                    if (!op_page) {
                        goto memory_or_python_error;
                    }
                    if (!(op_offset >= op_page->valid_start && op_offset < op_page->valid_end)) {
                        if (!access_check(self, op_page, word_address)) {
                            goto memory_or_python_error;
                        }
                    }
                    f = op_page->words[op_offset];
                } else if (mem_read_word(self, word_address, &f) < 0) {
                    goto memory_or_python_error;
                }
            }

            /* handle output */
            if (f <= out1 && f >= dw) {
                PyObject* result = PyObject_CallFunctionObjArgs(write_bit, (f == out1) ? Py_True : Py_False, NULL);
                if (!result) {
                    goto python_error;
                }
                Py_DECREF(result);
            }

            /* handle input */
            if (ip <= in_addr && ip > in_lo_exclusive) {
                PyObject* result;
                int bit_value;
                double io_start = monotonic_seconds();
                result = PyObject_CallNoArgs(read_bit);
                paused_seconds += monotonic_seconds() - io_start;
                if (!result) {
                    if (PyErr_ExceptionMatches(eof_exception_type)) {
                        PyErr_Clear();
                        cause = TERM_EOF;
                        break;
                    }
                    goto python_error;
                }
                bit_value = PyObject_IsTrue(result);
                Py_DECREF(result);
                if (bit_value < 0) {
                    goto python_error;
                }
                if (mem_write_bit(self, in_addr, bit_value) < 0) {
                    goto memory_or_python_error;
                }
            }

            /* FLIP! */
            if (mem_flip_bit(self, f) < 0) {
                goto memory_or_python_error;
            }

            /* read jump word (after the flip - the flip may modify it, including this word) */
            if (op_flat_jump) {
                j = *op_flat_jump;
                if (j & GARBAGE_SENTINEL) {
                    if (!flat_garbage(self, (uint64_t)(op_flat_jump - flat))) {
                        goto memory_or_python_error;
                    }
                    j = 0;
                }
            } else if (op_page) {
                /* the jump word's validity is checked here, at read time (after the flip) -
                   matching the reference loops' op order exactly */
                if (!(op_offset + 1 >= op_page->valid_start && op_offset + 1 < op_page->valid_end)) {
                    if (!access_check(self, op_page, (ip >> ww) + 1)) {
                        goto memory_or_python_error;
                    }
                }
                j = op_page->words[op_offset + 1];
            } else if (bit_offset) {
                if (mem_get_word_unaligned(self, ip + width, &j) < 0) {
                    goto memory_or_python_error;
                }
            } else if (mem_read_word(self, (ip >> ww) + 1, &j) < 0) {
                goto memory_or_python_error;
            }
            ops++;

            /* check finish? (f >= ip && f - ip < dw  is the overflow-safe  ip <= f < ip+dw) */
            if (j == ip && !(f >= ip && f - ip < dw)) {
                cause = TERM_LOOPING;
                break;
            }
            if (j < dw) {
                cause = TERM_NULL_IP;
                break;
            }

            /* JUMP! */
            ip = j;
        }
    }

    self->last_run_op_count = ops;
    self->last_run_paused_seconds = paused_seconds;
    return build_run_result(self, cause, ops, last_ops_ring, last_ops_length, ring_writes, paused_seconds);

memory_or_python_error:
    if (self->mem_error) {
        self->mem_error = 0;
        self->last_run_op_count = ops;
        self->last_run_paused_seconds = paused_seconds;
        return build_run_result(self, TERM_MEMORY_ERROR, ops, last_ops_ring, last_ops_length, ring_writes,
                                paused_seconds);
    }
    /* fallthrough: a python error during a memory callback */
python_error:
    self->last_run_op_count = ops;
    self->last_run_paused_seconds = paused_seconds;
    free(last_ops_ring);
    return NULL;
}

static PyObject* Memory_get_op_count(MemoryObject* self, void* closure)
{
    (void)closure;
    return PyLong_FromUnsignedLongLong(self->last_run_op_count);
}

static PyObject* Memory_get_paused_seconds(MemoryObject* self, void* closure)
{
    (void)closure;
    return PyFloat_FromDouble(self->last_run_paused_seconds);
}

static PyObject* Memory_get_storage_mode(MemoryObject* self, void* closure)
{
    (void)closure;
    if (!self->storage_decided) {
        Py_RETURN_NONE;
    }
    return PyUnicode_FromString(self->flat ? "flat" : "paged");
}

static PyObject* Memory_get_allocated_bytes(MemoryObject* self, void* closure)
{
    (void)closure;
    return PyLong_FromUnsignedLongLong(self->flat_count * sizeof(uint64_t) +
                                       self->slots_used * PAGE_WORDS * sizeof(uint64_t) +
                                       self->slot_count * sizeof(Slot));
}

static PyMethodDef Memory_methods[] = {
    {"add_segment", (PyCFunction)Memory_add_segment, METH_VARARGS,
     "add_segment(start_word_address, length_words) - declare a valid memory segment"},
    {"set_word", (PyCFunction)Memory_set_word, METH_VARARGS, "set_word(word_address, value)"},
    {"get_word", (PyCFunction)Memory_get_word, METH_VARARGS, "get_word(word_address) -> value"},
    {"set_words", (PyCFunction)Memory_set_words, METH_VARARGS, "set_words(start_word_address, values)"},
    {"run", (PyCFunction)Memory_run, METH_VARARGS | METH_KEYWORDS,
     "run(read_bit, write_bit, eof_exception_type, last_ops_length=0, start_ip=0)\n"
     "-> (termination_cause, op_count, error_bit_address_or_None, last_ops, paused_seconds)"},
    {NULL, NULL, 0, NULL},
};

static PyGetSetDef Memory_getset[] = {
    {"last_run_op_count", (getter)Memory_get_op_count, NULL, "op count of the last run (valid on exceptions too)",
     NULL},
    {"last_run_paused_seconds", (getter)Memory_get_paused_seconds, NULL,
     "IO-paused seconds of the last run (valid on exceptions too)", NULL},
    {"allocated_bytes", (getter)Memory_get_allocated_bytes, NULL,
     "bytes allocated for memory pages (footprint scales with touched memory, not segment sizes)", NULL},
    {"storage_mode", (getter)Memory_get_storage_mode, NULL,
     "'flat'/'paged' - the storage mode chosen at the first run (None before it)", NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyType_Slot Memory_type_slots[] = {
    {Py_tp_dealloc, (void*)Memory_dealloc},
    {Py_tp_doc, (void*)"segment-aware FlipJump memory (flat/paged) + native run-loop"},
    {Py_tp_methods, (void*)Memory_methods},
    {Py_tp_getset, (void*)Memory_getset},
    {Py_tp_init, (void*)Memory_init},
    {Py_tp_new, (void*)PyType_GenericNew},
    {0, NULL},
};

static PyType_Spec Memory_type_spec = {
    "_fjcore.Memory",        /* name */
    sizeof(MemoryObject),    /* basicsize */
    0,                       /* itemsize */
    Py_TPFLAGS_DEFAULT,      /* flags */
    Memory_type_slots,       /* slots */
};

static PyModuleDef fjcore_module = {
    PyModuleDef_HEAD_INIT, "_fjcore", "native FlipJump interpreter engine", -1, NULL, NULL, NULL, NULL, NULL,
};

PyMODINIT_FUNC PyInit__fjcore(void)
{
    PyObject* module;
    PyObject* memory_type = PyType_FromSpec(&Memory_type_spec);
    if (!memory_type) {
        return NULL;
    }
    module = PyModule_Create(&fjcore_module);
    if (!module) {
        Py_DECREF(memory_type);
        return NULL;
    }
    if (PyModule_AddObject(module, "Memory", memory_type) < 0) {
        Py_DECREF(memory_type);
        Py_DECREF(module);
        return NULL;
    }
    PyModule_AddIntConstant(module, "TERM_LOOPING", TERM_LOOPING);
    PyModule_AddIntConstant(module, "TERM_EOF", TERM_EOF);
    PyModule_AddIntConstant(module, "TERM_NULL_IP", TERM_NULL_IP);
    PyModule_AddIntConstant(module, "TERM_MEMORY_ERROR", TERM_MEMORY_ERROR);
    return module;
}
