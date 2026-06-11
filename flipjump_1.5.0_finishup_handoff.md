# FlipJump 1.5.0 - Finish-up Handoff

The goal of the session executing this handoff: **finish everything 1.5.0-related**, on the
existing branch `feature/flipjump-1.5.0` (pushed to origin; ~20 commits on top of `main`).
The branch will NOT be merged by the executing session - the owner CRs manually and merges.

- **Methodology (unchanged from the original handoff):** TDD; assemble with `--werror`;
  byte-exact verification via `flipjump.assemble_and_run_test_output(...)`; the full catalog
  (`pytest --catalog`, ~2,350 tests, ~16 min) must stay green after every change - run it as
  the gate before declaring any work item done.
- **Authoring `.fj`:** through the flipjump-dev skill (`tomhea/skills`).
- **Trap:** scripts run as `python scripts/foo.py` import the *site-packages* flipjump, not
  the repo. Insert the repo root into `sys.path` first (several scripts in `scripts/` show
  the pattern), or run from the repo root via `python -c` / stdin.
- **Native engine:** rebuild after touching `_fjcore.c` with `python build_fjcore.py`
  (abi3; `--pgo-instrument`/`--pgo-use` for tuned local builds - train on BOTH
  `--program loop` and `--program sieve` or the paged path regresses).

## What 1.5.0 already contains (done, validated, pushed)

- **WI-A** - three interpreter engines; native `_fjcore` C extension: flat-storage mode for
  compact programs (~280-307M fj/s, ~16 cycles/op), paged mode for sparse (~120-140M).
  History + cycle accounting in `tests/benchmark_results.md`. `FLIPJUMP_NO_NATIVE=1` /
  `FLIPJUMP_NO_FLAT=1` toggles. Benchmarks: `python tests/benchmark_interpreter.py
  [--program {sieve,loop}]`.
- **WI-B** - device<->memory hook (`DeviceMemory`, `IODevice.attach_memory`);
  `InMemoryScreen256` (headless: PNG/frame + sha256 frame-hash log + present timestamps);
  `KeyboardIO` (see protocol below); `fj --di/--do` CLI flags.
- **WI-C** - CLI debugger (terminal prompts, ASCII-only, EOF-safe defaults), tested.
- **WI-D** - fixed-point STL (`hex.fixed_mul/fixed_div/mul_const/read_table`), LUT
  generator (`flipjump.lut_generator`), DOOM-prep helpers (`hex.abs`,
  `hex.fill_bytes/copy_bytes`, `hex.read_table_byte` + `generate_byte_lut_fj`).
- **Packaging** - abi3 stable-ABI extension; setuptools backend (PEP 621); best-effort
  ext build in `setup.py` (pure-python fallback with a warning); cibuildwheel matrix in
  `.github/workflows/wheels.yml` (8 wheels: manylinux/musllinux x x86_64/aarch64, macOS
  x86_64/arm64, Windows amd64/arm64 + sdist, published on GitHub release).
- **Renames/cleanups** - `flipjump/interpretter/` -> `flipjump/interpreter/`; README
  documents the engines/devices/debugger; easygui removed.

### Device protocols (v3 - the final 1.5.0 shapes)

- **Keyboard**: one status HEX per polled tic (`hex.input_hex`): `0x0` = no event,
  `0x8` = key released, `0x9` = key pressed (bit 3 = event, bit 0 = is_down). On an event,
  the keycode byte follows via `hex.input` (stream mode), or sits in the one-packed-byte
  memory mailbox (mailbox mode). Idle never EOFs. Scripted `tic, down/up, keycode` event
  files replay deterministically. Concurrent keys = consecutive down events; the game keeps
  its own `keydown[]` array (DOOM-style) - the device only streams transitions.
- **Screen**: command bytes over the output stream; framebuffer/palette read from program
  memory via the hook. Framebuffer = packed bytes (one pixel per op, stride dw); palette =
  3 packed bytes per entry. A `hex.vec` framebuffer also works at bpp=4 (a hex op data
  bits are the byte low nibble) - so fixed-address hex math on pixels is possible at 16
  colors without any device change.

## Work items remaining for 1.5.0

### WI-E - Assembler speedup (research -> implement; ships in 1.5.0)

The interpreter got ~1,700x faster; the assembler is now the slow half (catalog compile:
1,029 programs ~ 14 min, ~0.8s per small program; DOOM mega-tables will stress it more).

**Owner's knowledge (start from this, then verify with measurements):** the parsing+lexing
phase is one of the SMALL parts. The dominant phases are **macro resolve** and
**create binary** - profile those first (the assembler already prints per-phase times;
cProfile/py-spy inside them).

1. **Profile first** on three workloads: `hello_world.fj` (fixed cost), `prime_sieve.fj`
   (macro-heavy), and a generated ~64K-entry LUT program (data-heavy - generate with
   `flipjump.lut_generator`; this is the DOOM-shaped workload, R-C risk).
2. **Suspected wins, in expected order:**
   - **Macro resolve** (`preprocessor.resolve_macros`): expression-tree (`expr.py`)
     evaluation/substitution churn per macro instantiation, label-dict building, `rep`
     expansion. Look for per-op object allocations and quadratic label handling.
   - **Create binary** (`assembler.py` + `fjm_writer`): the `wflip` resolution/emission,
     big-int bit packing of the words, lzma compression cost.
   - Minor (fixed cost on small programs): the STL's 34 files are re-lexed/re-parsed on
     every assemble - a parse cache keyed by file-content hash helps the catalog's many
     small programs, but is NOT the main event.
3. **Acceptance:** bit-identical `.fjm` outputs (hash-compare a catalog sample before/after);
   measured speedup reported for all three workloads; catalog compile-phase time recorded in
   `tests/benchmark_results.md` (add an "assembler" section); full catalog green.

### WI-F - Speculation miss-rate measurement (pre-study for the ~600M fj/s tier)

The native engine is bounded (~16 cy/op) by the serial chain: this op jump-word load ->
next op address -> next load. The only C-level way past it is **jump-target speculation**:
remember the last jump target per op address, start the next op loads early, verify.
FlipJump property that makes it promising: most *executed* ops (truth-table cells, plain
code) have jump words that never change after init - wflip-mutability concentrates in few
dispatch/return cells.

**This work item is measurement only - GO/NO-GO data, not the implementation:**
1. Add a counting mode to `_fjcore.c` (behind `FLIPJUMP_MEASURE_SPECULATION=1` env or a
   compile flag, NOT on the hot path of normal builds): per executed op, count whether the
   jump word at this ip differs from the value it had on the previous execution of this ip
   (a hash/array shadow keyed by ip; flat-mode-only is fine).
2. Report the would-be miss-rate on: `--program loop`, `--program sieve` (w=64), and a few
   catalog programs (e.g. the hexlib mul/div tests - table-dispatch-heavy).
3. Verdict in `tests/benchmark_results.md`: if miss-rate < ~10%, speculation is worth
   building (expected +50-80%, toward ~450-600M fj/s); else document and close.

### WI-G - Screen device: raw-frame command (decision + small implementation)

(DOOM is 256-color - an 8-bit palettized framebuffer with colormap-based light diminishing -
so bpp=8 is the game baseline; bpp=4 exists for small demos.)

Per the owner: a "no memory-hook" mode is philosophically interesting. The numbers
(96x64 @ 10fps, budget re-baselined below): a full frame as a **fixed-address** hex.vec
print costs ~60-120K fj-ops (~0.3-0.5% of budget) - viable; per-pixel *pointer* output is
~4M ops - not viable. DOOM redraws the full 3D view every frame (update_rectangle is for
status-bar/menu only), so full-frame is the common case anyway.

- Add `CMD_UPDATE_SCREEN_RAW = 0x05`: `[0x05][w*h pixel bytes]` - pixels arrive in-stream,
  no memory read. TDD like the other commands (golden frame-hash + an .fj E2E).
- Keep the memory-hook commands as the primary (they are ~free and DMA-like); document both.

### WI-H - CR loop + release mechanics

1. Address the owner manual-CR findings (the branch is presented for review - do NOT merge).
2. After approval: re-run the full gate (`--regular`, `--hexlib`, unit, catalog), re-run
   `python tests/benchmark_interpreter.py` and update numbers if the engine changed,
   verify `python -m build` produces the abi3 wheel, and dry-run
   `.github/workflows/wheels.yml` via workflow_dispatch (repo is public; the arm runners
   `ubuntu-24.04-arm` / `windows-11-arm` are available).

## Design decisions already made (do not relitigate without new data)

- **Budget re-baseline:** the original plan budgeted 1M fj-ops/frame assuming 10M fj/s.
  At ~280M fj/s (flat path), the budget at 10fps is ~28M ops/frame - per-pixel pointer
  writes (~500 ops each, ~3M/frame for a full 96x64 redraw) are comfortably affordable.
- **w=32** for the game (halves op count; 16.16 fits; see `tests/benchmark_results.md`).
- **Game memory layout:** compute in fixed-address `hex.vec` registers (player state,
  angles, counters - all direct math); stream through pointers only for the framebuffer,
  map data, and LUT reads (`read_table`/`read_table_byte`). Packed-byte buffers for
  pointer-streamed data; `hex.vec` for anything needing arithmetic. Keep every segment
  below 8M words so the native engine flat mode applies.
  - Note on LUTs: their BASE addresses are compile-time labels, but the INDEX (angle,
    distance) is runtime - so reads go through pointers. Only a compile-time-constant index
    is a static read.
- **The generated LUT tables live in the `doom-flipjump` repo** (same github user; PR
  there) - flipjump ships only the generator (`flipjump.lut_generator`). The game repo
  generates its `finesine`/reciprocal/colormap tables at build time.
- **OPEN: hex-memory vs byte-memory for pixels (decide in the game repo, R1).** Owner's
  criterion: if pixel-color computation can run "statically" on fixed compile-time-known
  addresses (no FJ-pointer dereferences), hex-memory wins big; otherwise packed-byte wins.
  Two credible static designs to evaluate with real measurements:
  (a) **fixed column buffer**: render each column into a fixed-address `hex.vec` buffer
  (all per-pixel math static), then one sequential pointer pass blits it into the
  framebuffer (`write_byte_and_inc` x height) - per-pixel compute static, one pointer op
  per pixel for placement;
  (b) **full column unroll**: `rep(SCREEN_WIDTH, x) render_column x` makes even the
  framebuffer stores static (every column's addresses compile-time) - zero pointer
  dereferences on the whole pixel path, at the cost of SCREEN_WIDTH copies of the column
  code (program size + assemble time - feeds the WI-E mega-program workload).
  At 256 colors a static byte store is two static hex stores - still far cheaper than one
  pointer dereference (~O(w) ops).
- **No decoded-op cache** (measured, rejected - OQ-A1); **no GUI debugger**; **the screen
  reads memory via the hook** as primary (the raw command of WI-G is an addition, not a
  replacement).