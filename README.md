# screenshot-bench

Four JVM screenshot-testing tools, one set of composables:

| module | tool | renderer |
|---|---|---|
| `viddik` | [viddik](https://github.com/youndie/viddik) | Compose Multiplatform / Skiko |
| `roborazzi-desktop` | [Roborazzi](https://github.com/takahirom/roborazzi) 1.76.0, `roborazzi-compose-desktop` | Compose Multiplatform / Skiko |
| `roborazzi-android` | Roborazzi 1.76.0 on Robolectric 4.17, native graphics | Android framework |
| `paparazzi` | [Paparazzi](https://github.com/cashapp/paparazzi) 2.0.0-alpha05 | layoutlib |

None of them needs an emulator. The questions here: what a run costs, what one more screenshot
costs, how long an edit-and-look cycle takes, whether goldens survive a change of operating system,
and whether a verify notices a small change.

Disclosure: viddik is written by the author of this repository. Every number below comes from the
scripts in `tools/`, every tool is set up the way its own documentation says, and the raw runs are
in `results/raw/`.

## Setup

- `fixtures/src/bench/Templates.kt`: five screen shapes (a list, a form, a card grid, a profile
  with controls, a settings page), foundation and material3 only. `tools/gen.py N` makes N fixtures
  from them and one capture per fixture for each tool. Every module compiles the same file.
- Every capture is 360×640 px at density 1 (`mdpi`), inside the same fixed `BenchTheme`.
- viddik draws text with its bundled font (`viddikTypography()`), as its README asks. The others
  use their defaults: layoutlib's and Robolectric's own fonts, and the host's system font for
  Compose Desktop. `-PbenchFont=viddik` gives `roborazzi-desktop` the same bundled font.
- `components` + `viddik-split`: the components in a KMP module of their own and the fixtures in a
  module with no main sources, the layout of a multi-module app (viddik#53).
- Kotlin 2.4.20, AGP 9.4.0, Compose Multiplatform 1.12.0, Compose BOM 2026.09.00, Gradle 9.7.1,
  JDK 21 for everything. Robolectric's SDK 36 sandbox fails on JDK 25 and needs
  `--add-opens java.base/jdk.internal.access` on 21.

## Method

`tools/run-all.sh` generates N fixtures and runs `tools/bench.py` on the build machine. For each
tool: a warm-up record, then rounds of record and verify on the warm Gradle daemon (five up to
N=200, three above), then verifies after `gradlew --stop`.

- Every measured run passes a fresh `-PbenchRun`, an input of every `Test` task, and the build
  cache is off, so nothing comes back up-to-date.
- The JUnit XML of each run is read back. A run whose fixture count is not N, or that has failures,
  is dropped.
- Peak memory is the summed RSS of the `Gradle Test Executor` JVMs, sampled every 200 ms.
- `-PbenchForks=K` sets `maxParallelForks` everywhere. viddik sets its own from `shards` (two by
  default), so the knob goes through `shards` there. Tables compare at equal forks.
- `tools/inner.sh` times the edit-and-look cycle: change a string in the component a fixture draws
  (a body-only edit), then record that one fixture, on the warm daemon.
- Build machine: 20 cores, 16 GB, Ubuntu 24.04 in WSL2, with other jobs present (load average
  1.5–3.9 at run starts). Its monotonic clock runs slow, so every number is corrected by the ratio
  of the driving machine's wall clock to the guest's over the same runs (×1.04).

## Results

Wall-clock seconds, medians. Full tables: [`results/summary.md`](results/summary.md).

**Warm verify, one test JVM per tool.** viddik 0.6.1 at N=50 and 200, 0.6.1.45 at N=1000 and 2000
(the code of 0.7.0 for this layout; 0.6.1 does not compile 2000 fixtures):

| tool | N=50 | N=200 | N=1000 | N=2000 | ms per extra screenshot, N=1000→2000 |
|---|---|---|---|---|---|
| viddik | 4.6 | 8.9 | 25.1 | 50.5 | 25 |
| roborazzi-desktop | 4.9 | 9.8 | 29.6 | 58.0 | 28 |
| paparazzi | 7.1 | 11.1 | 28.7 | 51.8 | 23 |
| roborazzi-android | 11.3 | 18.0 | 41.5 | 67.3 | 26 |

**Four forks, N=2000:** viddik 14.8 (×3.4), roborazzi-desktop 17.9 (×3.2), Paparazzi 22.7 (×2.3),
Robolectric 35.9 (×1.9).

**Edit a component, record one golden, N=1000** (viddik 0.6.1.45):

| tool | no edit | after a body-only edit |
|---|---|---|
| roborazzi-desktop | 2.6 | 2.8 |
| viddik | 2.9 | 3.3 |
| paparazzi | 5.1 | 5.5 |
| roborazzi-android | 7.1 | 7.4 |

On viddik 0.6.1.42 the same edit took 4.1 s: the Compose compiler's `@FunctionKeyMeta` offsets made
every edit look like a classpath change to KSP. The fixtures-only layout (`viddik-split`, 200
fixtures, isolated projects on) went from 5.5–6.4 s to 3.0–3.7 s with 0.6.1.48.

**Goldens recorded on Linux, verified on macOS (N=50, viddik 0.6.1):**

| tool | pixel-identical | worst image | tool's own verify |
|---|---|---|---|
| paparazzi | 50/50 | 0 px | passes |
| roborazzi-android | 50/50 | 0 px | passes |
| viddik | 38/50 | 13 px (0.006%) | passes |
| roborazzi-desktop | 0/50 | 8.8% of pixels | fails 50/50 |
| roborazzi-desktop, viddik's font | 0/50 | 3.5% of pixels | — |

**Does verify fail when the picture changes? (N=10, default tolerances, viddik 0.6.1):**

| tool | a full stop appended to the heading | first letter of the heading → X |
|---|---|---|
| roborazzi-desktop, roborazzi-android | 10/10 caught | 10/10 |
| viddik, paparazzi | 2/10 caught | 10/10 |

A full stop changes 12–13 pixels at a channel delta of 223. From viddik 0.7.0 its pixel floor
absorbs only faint pixels: with `tolerancePercent = 0.0` it catches 10/10, and the Linux goldens
still verify on macOS 50/50 (`results/raw/fix-0.6.1.42.txt`). At its default 0.05% share, 12 pixels
of a 360×640 screen still pass.

## What the numbers say

- **The renderer decides most of it.** The two Skiko tools and Paparazzi converge at ~25–30 ms a
  screenshot on large suites; Robolectric pays the most per run.
- **The edit-and-look cycle is where they differ by seconds**: roborazzi-desktop and viddik
  2.8–3.3 s, Paparazzi 5.5 s, Robolectric 7.4 s.
- **Portability splits by renderer.** The Android renderers give byte-identical goldens on both
  operating systems. On Skiko, Roborazzi's goldens differ everywhere, and a bundled font alone does
  not fix that; viddik gets within 13 px through its own glyph rasterisation and font-metric
  normalisation.
- **Tolerance is a trade.** A tool that forgives the cross-OS residue by pixel count also forgives
  a full stop of the same size. Telling them apart takes the channel delta (47 against 223).

## Caveats

- One build machine and one workstation (an M1). The fork speed-ups depend on the core count.
- All fixtures share one size, the best case for viddik's scene reuse.
- viddik's versions differ between tables, as labelled; the other three tools are the same versions
  throughout.
- Paparazzi 2.0 is an alpha, picked as the newest release. 1.3.5 was not tried.
- Gradle's default test heap (512 MB) applies to every tool; `-PbenchHeap=2g` raises it for all.
- Only the steady state is measured. First-run downloads (layoutlib, Robolectric's android-all jar)
  are not.

## Reproduce

```bash
tools/gen.py 50                        # N fixtures + tests for every tool
./gradlew :viddik:viddikRecord :viddik:viddikVerify
tools/run-all.sh                       # the benchmark; also: viddik-forks, large, viddik-large
tools/gen.py 1000 && tools/inner.sh 500 5
tools/record-set.sh out/linux          # every tool's goldens, for tools/pngdiff.py on another OS
tools/summarize.py                     # results/summary.md
```

Everything runs on the current machine by default. To run the builds elsewhere, set
`BENCH_REMOTE`, `BENCH_FETCH` and `BENCH_JAVA_HOME` (see `tools/remote.sh`).

## License

MIT, see [LICENSE](LICENSE).
