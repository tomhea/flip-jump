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
#include <Python.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define PAGE_BITS 14
#define PAGE_WORDS (1ull << PAGE_BITS) /* 16K words, 128KB per page */
#define PAGE_MASK (PAGE_WORDS - 1)

/* how often to check for signals (Ctrl+C): every 2^18 ops */
#define SIGNAL_CHECK_MASK 0x3FFFFull

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

    uint64_t last_page_index_plus1; /* 1-entry page cache */
    Page* last_page;

    SegmentRange* segments; /* sorted, merged */
    Py_ssize_t segment_count;
    Py_ssize_t segment_capacity;
    int segments_sorted;

    int mem_error;            /* set when garbage_stop fired */
    uint64_t error_bit_address;

    unsigned long long last_run_op_count; /* op count of the last run (also on exceptions) */
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
    uint64_t h;
    if (key == m->last_page_index_plus1) {
        return m->last_page;
    }
    if (m->slots_used * 2 >= m->slot_count) {
        if (mem_grow_slots(m) < 0) {
            return NULL;
        }
    }
    h = (key * 0x9E3779B97F4A7C15ull) & (m->slot_count - 1);
    while (m->slots[h].key_plus1) {
        if (m->slots[h].key_plus1 == key) {
            m->last_page_index_plus1 = key;
            m->last_page = m->slots[h].page;
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
        m->last_page_index_plus1 = key;
        m->last_page = page;
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

/* read the w-bit word at the word-address. returns 0 on success, -1 on stop (mem_error or
   python error - distinguish via m->mem_error). */
static inline int mem_read_word(MemoryObject* m, uint64_t word_address, uint64_t* out)
{
    Page* page = mem_get_page(m, word_address >> PAGE_BITS);
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
    Page* page = mem_get_page(m, word_address >> PAGE_BITS);
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
    Page* page = mem_get_page(m, word_address >> PAGE_BITS);
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
    if (mem_read_word(m, word_address, &lsw) < 0) {
        return -1;
    }
    if (mem_read_word(m, word_address + 1, &msw) < 0) {
        return -1;
    }
    *out = ((lsw >> bit_offset) | (msw << (m->w - bit_offset))) & m->word_mask;
    return 0;
}

/* ---------------------------------------------------------------- Memory type */

static int Memory_init(MemoryObject* self, PyObject* args, PyObject* kwds)
{
    static char* kwlist[] = {"memory_width", "garbage_stop", NULL};
    int w, garbage_stop = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i|p", kwlist, &w, &garbage_stop)) {
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
    self->last_page_index_plus1 = 0;
    self->last_page = NULL;
    self->segments = NULL;
    self->segment_count = 0;
    self->segment_capacity = 0;
    self->segments_sorted = 1;
    self->mem_error = 0;
    self->error_bit_address = 0;
    self->last_run_op_count = 0;
    return 0;
}

static void Memory_dealloc(MemoryObject* self)
{
    if (self->slots) {
        for (uint64_t i = 0; i < self->slot_count; i++) {
            if (self->slots[i].key_plus1) {
                free(self->slots[i].page->words);
                free(self->slots[i].page);
            }
        }
        free(self->slots);
    }
    free(self->segments);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* Memory_add_segment(MemoryObject* self, PyObject* args)
{
    unsigned long long start_word, length_words;
    if (!PyArg_ParseTuple(args, "KK", &start_word, &length_words)) {
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
    values = PySequence_Fast(values, "set_words expects a sequence");
    if (!values) {
        return NULL;
    }
    count = PySequence_Fast_GET_SIZE(values);
    for (i = 0; i < count; i++) {
        unsigned long long value = PyLong_AsUnsignedLongLong(PySequence_Fast_GET_ITEM(values, i));
        Page* page;
        if (value == (unsigned long long)-1 && PyErr_Occurred()) {
            Py_DECREF(values);
            return NULL;
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

        ip = start_ip;
        self->mem_error = 0;
        self->last_run_op_count = 0;

        for (;;) {
            uint64_t f, j, bit_offset;

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

            /* read flip word */
            bit_offset = ip & bit_mask;
            if (bit_offset) {
                if (mem_get_word_unaligned(self, ip, &f) < 0) {
                    goto memory_or_python_error;
                }
            } else if (mem_read_word(self, ip >> ww, &f) < 0) {
                goto memory_or_python_error;
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
                clock_t io_start = clock();
                result = PyObject_CallNoArgs(read_bit);
                paused_seconds += (double)(clock() - io_start) / CLOCKS_PER_SEC;
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

            /* read jump word (after the flip - the flip may modify it) */
            if (bit_offset) {
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
    return build_run_result(self, cause, ops, last_ops_ring, last_ops_length, ring_writes, paused_seconds);

memory_or_python_error:
    if (self->mem_error) {
        self->mem_error = 0;
        self->last_run_op_count = ops;
        return build_run_result(self, TERM_MEMORY_ERROR, ops, last_ops_ring, last_ops_length, ring_writes,
                                paused_seconds);
    }
    /* fallthrough: a python error during a memory callback */
python_error:
    self->last_run_op_count = ops;
    free(last_ops_ring);
    return NULL;
}

static PyObject* Memory_get_op_count(MemoryObject* self, void* closure)
{
    (void)closure;
    return PyLong_FromUnsignedLongLong(self->last_run_op_count);
}

static PyObject* Memory_get_allocated_bytes(MemoryObject* self, void* closure)
{
    (void)closure;
    return PyLong_FromUnsignedLongLong(self->slots_used * PAGE_WORDS * sizeof(uint64_t) +
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
    {"allocated_bytes", (getter)Memory_get_allocated_bytes, NULL,
     "bytes allocated for memory pages (footprint scales with touched memory, not segment sizes)", NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyTypeObject MemoryType = {
    PyVarObject_HEAD_INIT(NULL, 0) /* */
    .tp_name = "_fjcore.Memory",
    .tp_basicsize = sizeof(MemoryObject),
    .tp_dealloc = (destructor)Memory_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "segment-aware paged FlipJump memory + native run-loop",
    .tp_methods = Memory_methods,
    .tp_getset = Memory_getset,
    .tp_init = (initproc)Memory_init,
    .tp_new = PyType_GenericNew,
};

static PyModuleDef fjcore_module = {
    PyModuleDef_HEAD_INIT, "_fjcore", "native FlipJump interpreter engine", -1, NULL, NULL, NULL, NULL, NULL,
};

PyMODINIT_FUNC PyInit__fjcore(void)
{
    PyObject* module;
    if (PyType_Ready(&MemoryType) < 0) {
        return NULL;
    }
    module = PyModule_Create(&fjcore_module);
    if (!module) {
        return NULL;
    }
    Py_INCREF(&MemoryType);
    if (PyModule_AddObject(module, "Memory", (PyObject*)&MemoryType) < 0) {
        Py_DECREF(&MemoryType);
        Py_DECREF(module);
        return NULL;
    }
    PyModule_AddIntConstant(module, "TERM_LOOPING", TERM_LOOPING);
    PyModule_AddIntConstant(module, "TERM_EOF", TERM_EOF);
    PyModule_AddIntConstant(module, "TERM_NULL_IP", TERM_NULL_IP);
    PyModule_AddIntConstant(module, "TERM_MEMORY_ERROR", TERM_MEMORY_ERROR);
    return module;
}
