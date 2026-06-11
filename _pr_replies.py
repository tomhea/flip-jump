import json, subprocess, sys

REPLIES = {
 3398169681: "Done - every action in this file is now referenced by commit hash at its newest release, with the version as an inline comment (checkout v6.0.3, setup-python v6.2.0, upload-artifact v7.0.1, download-artifact v8.0.1, cibuildwheel v4.0.0, gh-action-pypi-publish v1.14.0). Note cibuildwheel jumped 2.23 -> 4.0 (a major bump); the workflow_dispatch dry-run will validate the build matrix still behaves.",
 3398180339: "Right - removed. `word_segments` is gone; `memory_segments` now holds word addresses (matching its own docstring - it was previously built in bit units, contradicting it) and is what the native engine consumes. It was also otherwise unused.",
 3398509026: "Done - renamed to `user_queries.py` with `show_message` / `ask_for_text` / `ask_for_choice`, the docstring is now 3 lines, and no file in the repo mentions agents anymore.",
 3398671595: "It is actually used - `attach_memory`'s `'DeviceMemory'` annotation needs the name for type checkers. The TYPE_CHECKING guard keeps the runtime import graph clean (IODevice is imported by every device; importing device_memory at runtime would pull in fjm_reader too, just for an annotation). Removed the work-item reference from the docstring. Happy to switch to a plain runtime import if you prefer it simpler.",
 3398695735: "Audited. The redundant chunk was the speculation-measurement code (a study tool) - removed entirely. Everything that remains is used: add_segment/set_word/get_word/set_words/run are called by fjm_run + the device-memory adapter; last_run_op_count / last_run_paused_seconds keep statistics valid on exception paths; storage_mode is the flat/paged observability you asked for; allocated_bytes is what pins the lazy-footprint property in the tests. mem_* internals all serve the run loops.",
 3398703893: "Searched and fixed four: (1) a raised flat_max_words could make the flat-array byte-size overflow size_t -> under-allocation + heap overflow during the sentinel fill - now falls back to paged; (2) calling __init__ again on a live Memory leaked all previous allocations - now freed (shared logic with dealloc); (3) set_words could wrap around the 64-bit address space and silently write low pages - the whole range is validated up front now; (4) a negative last_ops_length reached calloc - clamped to 0. Each has a test. An independent full-file review pass afterwards found no further memory issues.",
 3398894691: "Done.",
 3398915003: "Done - it's a regular bullet in the hex file-list now.",
 3398932775: "Removed (the C counting mode, this field, and the measuring script). The study's verdict stays recorded in tests/benchmark_results.md, and the tool itself is recoverable from commit 282a0ea if the speculation tier work ever needs it again.",
 3398956237: "Rewritten generic and shorter - no game references. The --do/--di help now also covers the new interactive modes: `--do screen` opens a real window (scaled, F11 fullscreen, closing stops the run), `--di keyboard` feeds its live key presses to the program.",
 3398982827: "Yes - it matters in debug() whenever the native engine actually runs, which is every run without breakpoints/trace/profile (those force the featured python loop, which ignores it). The docstring now states exactly that.",
 3398985594: "Done - cut to a 3-sentence bullet plus a 3-sentence flat-limit note.",
 3399006479: "Done - the fixed_point/LUT tests left with stl/hex/fixed_point.fj. What stayed is hexlib/helpers (hex.abs + the byte-buffer block helpers, which live in math_basic.fj/strings.fj and remain stl).",
 3399059341: "Done.",
 3399060122: "Done.",
 3399063238: "Done - and swept the whole repo: no 'flip-jump' (or 'Flip-Jump') string remains in any tracked file; all URLs point at tomhea/flipjump.",
 3399077643: "Done - rewritten concise.",
 3399083553: "Done - generic and shorter (and it now documents the interactive window modes).",
 3399087581: "Done - no 'since X' phrasing remains anywhere in the docs (README, flipjump/README, benchmark_results).",
 3399102420: "Done - the full debugging documentation lives in flipjump/interpreter/debugging/README.md now; both the main README and flipjump/README reference it with a one-line pointer.",
}

failed = []
for comment_id, body in REPLIES.items():
    result = subprocess.run(
        ['gh', 'api', f'repos/tomhea/flipjump/pulls/354/comments/{comment_id}/replies',
         '-f', f'body={body}'],
        capture_output=True, text=True)
    status = 'ok' if result.returncode == 0 else 'FAILED'
    if result.returncode != 0:
        failed.append((comment_id, result.stderr.strip()[:200]))
    print(comment_id, status)
print('failures:', failed if failed else 'none')
