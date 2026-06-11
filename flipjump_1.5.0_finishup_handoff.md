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

### WI-G2 - Flat-storage mode: configurable limit + observability (owner ask)

The game MUST run on the native engine's flat path. Aligned dispatch tables inflate the
address span (each table pads to a power-of-two boundary), so the game may exceed today's
hardcoded `FLAT_MAX_WORDS` (2^23 words = 64MB of flat array).

1. Make the limit runtime-configurable: keep the 2^23 default, add a `Memory` constructor
   parameter, plumbed from `fjm_run.run(...)`, an `fj --flat-max-words N` CLI flag, and a
   `FLIPJUMP_FLAT_MAX_WORDS` env var. (Answer to "will it hurt anything?": no hot-path cost
   - the decision happens once at run start; the per-op loop is unchanged regardless of the
   limit's value.)
2. On flat-array allocation failure, fall back to PAGED mode instead of erroring.
3. **Observability**: expose which mode ran (`Memory.storage_mode` -> 'flat'/'paged',
   surfaced in the non-silent run output) so "the game runs flat" is verifiable, not assumed.
4. Costs to document (answers to "will it hurt the speed?"): per-op speed - none. Startup +
   footprint - real: the flat build sentinel-fills the whole span, touching every page, so
   RSS = 8 bytes x span and fill time ~0.1s/GB. A game with a 2^26-word span costs 512MB
   RAM. Optional improvement if that bites: chunk the sentinel fill / use a high-water-mark
   scheme so untouched tail pages stay virtual.
5. Tests: flat/paged selection across limits (env/CLI/param), the fallback path, and
   storage_mode reporting.

### WI-H - CR loop + release mechanics

1. Address the owner manual-CR findings (the branch is presented for review - do NOT merge).
2. After approval: re-run the full gate (`--regular`, `--hexlib`, unit, catalog), re-run
   `python tests/benchmark_interpreter.py` and update numbers if the engine changed,
   verify `python -m build` produces the abi3 wheel, and dry-run
   `.github/workflows/wheels.yml` via workflow_dispatch (repo is public; the arm runners
   `ubuntu-24.04-arm` / `windows-11-arm` are available).

## THE game target (owner decision): 160x100, textured, 25fps

16,000 pixels/frame, 25fps. Budget: ~11.2M fj-ops/frame on the current engine (280M fj/s),
~18-24M after the speculation tier (WI-F -> implementation, if GO).

| per-frame cost | static stores + dispatch-LUTs (required) |
|---|---|
| pixel stores (16K x ~80 ops) | ~1.3M |
| texture+colormap dispatch reads (16K x ~100-200 ops) | ~1.6-3.2M |
| column math (160 cols) + BSP + game logic | ~1.5-3M |
| **total** | **~5-7M of 11.2M - fits the CURRENT engine with margin** |

So textured 160x100@25 does NOT depend on the speculation tier - that tier becomes pure
headroom (eventually 320x200). Mandatory techniques: static pixel stores (fixed
column-buffer or column-unroll) and dispatch-LUTs for ALL table reads.

**Owner directive: fixed-address-LUT (aligned dispatch tables, the hex.and way) everything
that can be** - finesine/finecosine, reciprocal/scale, yslope, viewangletox/xtoviewangle,
the colormaps, and evaluate texture data itself as dispatch tables. Each generated table
gets its own thorough test (hexlib-style: generated program + host-reference fixtures over
many indices, including the first/last entries and wrap boundaries).

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
- **The LUT generator AND the generated tables live in the `doom-flipjump` repo** (same
  github user; PR there). A finish-up task in THIS repo: relocate `flipjump/lut_generator.py`
  (+ its tests) out of flipjump into doom-flipjump; keep the generic `hex.read_table` /
  `hex.read_table_byte` STL macros here, with their entry-layout contract documented in the
  STL itself (not by reference to the generator). The flipjump test programs that embed
  generated tables keep their inlined copies.
- **OPEN (owner: keep thinking about it): hex-memory vs byte-memory for pixels (decide in
  the game repo, R1).** Owner's
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
- **LUT access must be redesigned the `hex.and` way (owner directive) - aligned
  code-table dispatch, NOT pointer reads.** Study `stl/hex/tables_init.fj` until this is
  obvious; the mechanism:
  1. The table is a `pad`-aligned CODE region (entry k at `base + k*dw`; base's low address
     bits are zero). A dedicated jumper op's jump word points at `base`.
  2. A hex variable's data bits sit at jump-word bits `#w..` - exactly the bit positions
     that encode `k*dw` inside an address. So `hex.xor jumper, index` (one per index nibble,
     at `jumper`, `jumper+4`, ...) IS the `base+index` computation - a few @ each, no O(w)
     pointer machinery. `wflip ret+w, return, jumper` then jumps through it.
  3. Entries are single ops ("stride 1") that jump to where the entry is really handled:
     either the hypercube chain (`clean_table_entry__table`: entry d flips one result bit
     and jumps to entry `d ^ (1 << (#d - 1))`, cascading to entry 0 -> ret; avg log(n)/2
     ops per lookup), or per-entry handler code for arbitrary values.
  4. For multi-nibble LUT values (e.g. 32-bit finesine entries), evaluate both shapes:
     one aligned table per result-nibble using the hypercube chain (8 cheap dispatches), vs
     one table of per-entry handlers xoring the whole value into a result register
     (1 dispatch + ~popcount flips). Estimate: ~10-30x cheaper than `hex.read_table`
     (~10@ vs ~w-scaled pointer reads), at a space cost of entries x handler-size.
  The doom-flipjump generator emits these dispatch-code tables; a generic
  `hex.xor_table_lookup`-style macro may belong in the flipjump STL (decide during
  implementation). The index must be kept nibble-aligned (it already is - U6).
- **No decoded-op cache** (measured, rejected - OQ-A1); **no GUI debugger**; **the screen
  reads memory via the hook** as primary (the raw command of WI-G is an addition, not a
  replacement).