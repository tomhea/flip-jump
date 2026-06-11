"""
unit-tests for the native engine's memory (_fjcore.Memory).

the key property pinned here is the memory footprint at scale: declaring huge segments
(like prime_sieve's half-the-address-space reserve) must
not allocate memory upfront - pages are allocated lazily, so the footprint scales with the
words actually touched, not with the declared segment sizes.

also pins the flat-storage mode selection: the configurable span limit (constructor
parameter / FLIPJUMP_FLAT_MAX_WORDS env var / 2^23-word default), the paged fallback on a
failed flat-array allocation, and the storage_mode observability ('flat'/'paged').
"""

from typing import Any

import pytest

try:
    from flipjump.interpreter import _fjcore  # type: ignore[attr-defined]
except ImportError:
    _fjcore = None

from flipjump.utils.exceptions import IOReadOnEOF

pytestmark = pytest.mark.skipif(_fjcore is None, reason='the native engine (_fjcore) is not built')


@pytest.fixture(autouse=True)
def clean_flat_mode_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # the flat-mode env knobs must not leak into (or from) these tests
    monkeypatch.delenv('FLIPJUMP_NO_FLAT', raising=False)
    monkeypatch.delenv('FLIPJUMP_FLAT_MAX_WORDS', raising=False)
    monkeypatch.delenv('FLIPJUMP_TEST_FLAT_ALLOC_FAIL', raising=False)


def _unexpected_io(*args: object) -> bool:
    raise AssertionError('the program must not perform IO')


def _looping_memory(**kwargs: Any) -> Any:
    """a w=32 memory holding one op at address 0: a harmless flip (word 4) + jump-to-self."""
    memory = _fjcore.Memory(32, **kwargs)
    memory.add_segment(0, 8)
    memory.set_words(0, [128, 0])
    return memory


def _run_to_looping(memory: Any) -> None:
    cause, op_count, _, _, _ = memory.run(_unexpected_io, _unexpected_io, IOReadOnEOF)
    assert cause == _fjcore.TERM_LOOPING
    assert op_count == 1


def test_huge_segment_is_not_allocated_upfront() -> None:
    # half the w=32 address space (2^26 words = 512MB if dense at 8B/word)
    memory = _fjcore.Memory(32)
    memory.add_segment(0, 1 << 26)
    assert memory.allocated_bytes < 1 << 20  # nothing touched - under 1MB


def test_footprint_scales_with_touched_memory_at_scale() -> None:
    # ~1M words of data/code spread over a 2^26-word segment: the footprint must stay
    # near the touched size, far below dense.
    memory = _fjcore.Memory(32)
    memory.add_segment(0, 1 << 26)

    touched_words = 1_000_000
    stride = (1 << 26) // touched_words
    for i in range(0, touched_words, 4096):  # touch one word in each region
        memory.set_word(i * stride, 0xDEADBEEF & 0xFFFFFFFF)

    # each touch allocates at most one 128KB page
    assert memory.allocated_bytes < 256 * (1 << 20)  # well below the 512MB dense equivalent
    assert memory.get_word(0) == 0xDEADBEEF & 0xFFFFFFFF


def test_dense_data_footprint_is_proportional() -> None:
    # a contiguous 1M-word program: footprint ~8MB (8B/word) + page table
    memory = _fjcore.Memory(32)
    memory.add_segment(0, 1 << 20)
    memory.set_words(0, list(range(1 << 20)))
    assert memory.allocated_bytes < 12 * (1 << 20)
    assert memory.get_word(12345) == 12345


def test_get_set_word_roundtrip_and_masking() -> None:
    memory = _fjcore.Memory(16)
    memory.add_segment(0, 1024)
    memory.set_word(7, 0x12345)  # masked to 16 bits
    assert memory.get_word(7) == 0x2345
    assert memory.get_word(8) == 0


def test_storage_mode_is_none_before_the_first_run() -> None:
    assert _looping_memory().storage_mode is None


def test_storage_mode_flat_for_a_compact_program() -> None:
    memory = _looping_memory()
    _run_to_looping(memory)
    assert memory.storage_mode == 'flat'


def test_flat_max_words_parameter_forces_paged() -> None:
    memory = _looping_memory(flat_max_words=4)  # the segment ends at word 8, above the limit
    _run_to_looping(memory)
    assert memory.storage_mode == 'paged'


def test_flat_max_words_parameter_can_raise_the_limit() -> None:
    # a segment ending beyond the default 2^23-word limit still runs flat with a raised limit
    memory = _fjcore.Memory(32, flat_max_words=1 << 25)
    memory.add_segment(0, 8)
    memory.set_words(0, [128, 0])
    memory.add_segment((1 << 24) - 8, 8)
    _run_to_looping(memory)
    assert memory.storage_mode == 'flat'


def test_flat_max_words_env_var_forces_paged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('FLIPJUMP_FLAT_MAX_WORDS', '4')
    memory = _looping_memory()
    _run_to_looping(memory)
    assert memory.storage_mode == 'paged'


def test_flat_max_words_parameter_overrides_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('FLIPJUMP_FLAT_MAX_WORDS', '4')
    memory = _looping_memory(flat_max_words=1 << 23)
    _run_to_looping(memory)
    assert memory.storage_mode == 'flat'


def test_flat_allocation_failure_falls_back_to_paged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('FLIPJUMP_TEST_FLAT_ALLOC_FAIL', '1')
    memory = _looping_memory()
    _run_to_looping(memory)  # the run must still succeed, just paged
    assert memory.storage_mode == 'paged'


def test_reinitializing_a_memory_does_not_crash() -> None:
    # __init__ can be called again on a live object - the old allocations must be released
    memory = _looping_memory()
    _run_to_looping(memory)  # builds the flat array
    memory.__init__(16)
    memory.add_segment(0, 8)
    memory.set_word(3, 0x123)
    assert memory.get_word(3) == 0x123


def test_set_words_beyond_the_flat_span_raises() -> None:
    memory = _looping_memory()
    _run_to_looping(memory)  # flat storage is built now
    assert memory.storage_mode == 'flat'
    with pytest.raises(ValueError):
        memory.set_words(6, [1, 2, 3])  # words 6..8, beyond the 8-word span


def test_no_flat_env_var_forces_paged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('FLIPJUMP_NO_FLAT', '1')
    memory = _looping_memory()
    _run_to_looping(memory)
    assert memory.storage_mode == 'paged'


def test_negative_last_ops_length_behaves_like_no_ring() -> None:
    memory = _looping_memory()
    cause, op_count, _, last_ops, _ = memory.run(_unexpected_io, _unexpected_io, IOReadOnEOF, last_ops_length=-1)
    assert cause == _fjcore.TERM_LOOPING
    assert last_ops == []


def test_set_words_near_the_address_space_top_raises() -> None:
    # a wrapping (start + count overflows 64 bits) range must be rejected, not write low pages
    memory = _fjcore.Memory(32)
    memory.add_segment(0, 8)
    with pytest.raises(ValueError):
        memory.set_words((1 << 64) - 2, [1, 2, 3])


def test_huge_flat_limit_does_not_overflow_the_allocation_size() -> None:
    # a raised limit whose byte-size overflows size_t must fall back to paged (not crash)
    memory = _fjcore.Memory(32, flat_max_words=1 << 62)
    memory.add_segment(0, 8)
    memory.set_words(0, [128, 0])
    memory.add_segment(1 << 61, 8)
    _run_to_looping(memory)
    assert memory.storage_mode == 'paged'
