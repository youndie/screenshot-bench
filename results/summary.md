Wall-clock seconds, median of the warm runs; build-machine clock corrected ×1.040. Invalid rows excluded: 15.


### N = 10, one test JVM per tool

| tool | record | verify (min–max) | verify, fresh daemon | ms per screenshot | peak RSS of test JVMs, MB |
|---|---|---|---|---|---|
| roborazzi-desktop | 3.2 | 3.2 (3.1–3.5) | 10.1 | 323 | 262 |
| paparazzi | 5.9 | 5.7 (5.5–6.0) | 13.8 | 571 | 512 |
| roborazzi-android | 8.7 | 8.6 (8.0–8.8) | 16.2 | 858 | 571 |
| viddik, its default (2 forks) | 2.9 | 3.0 (2.6–3.2) | 9.8 | 300 | 464 |

### N = 50, one test JVM per tool

| tool | record | verify (min–max) | verify, fresh daemon | ms per screenshot | peak RSS of test JVMs, MB |
|---|---|---|---|---|---|
| viddik | 4.6 | 4.6 (4.5–5.4) | 11.7 | 92 | 375 |
| roborazzi-desktop | 4.7 | 4.9 (4.8–5.3) | 11.7 | 98 | 386 |
| paparazzi | 7.8 | 7.1 (6.6–7.5) | 15.4 | 143 | 546 |
| roborazzi-android | 11.3 | 11.3 (11.1–11.5) | 19.0 | 225 | 738 |
| viddik, its default (2 forks) | 3.8 | 3.7 (3.7–3.8) | 10.7 | 75 | 655 |

### N = 200, one test JVM per tool

| tool | record | verify (min–max) | verify, fresh daemon | ms per screenshot | peak RSS of test JVMs, MB |
|---|---|---|---|---|---|
| viddik | 8.9 | 8.9 (8.7–9.7) | 15.5 | 45 | 442 |
| roborazzi-desktop | 10.7 | 9.8 (8.4–11.8) | 16.9 | 49 | 408 |
| paparazzi | 14.7 | 11.1 (11.0–11.2) | 20.1 | 56 | 609 |
| roborazzi-android | 19.2 | 18.0 (17.4–18.8) | 25.9 | 90 | 1039 |
| viddik, its default (2 forks) | 5.5 | 5.3 (5.2–5.5) | 12.2 | 27 | 825 |

### N = 1000, one test JVM per tool

| tool | record | verify (min–max) | verify, fresh daemon | ms per screenshot | peak RSS of test JVMs, MB |
|---|---|---|---|---|---|
| viddik | 26.3 | 25.1 (25.1–26.0) | 33.4 | 25 | 574 |
| roborazzi-desktop | 34.7 | 29.6 (29.0–31.9) | 38.4 | 30 | 479 |
| paparazzi | 46.8 | 28.7 (28.7–28.9) | 38.5 | 29 | 669 |
| roborazzi-android | 44.9 | 41.5 (41.5–41.8) | 50.6 | 42 | 1172 |

### N = 2000, one test JVM per tool

| tool | record | verify (min–max) | verify, fresh daemon | ms per screenshot | peak RSS of test JVMs, MB |
|---|---|---|---|---|---|
| viddik | 50.1 | 50.5 (49.0–51.2) | 63.4 | 25 | 688 |
| roborazzi-desktop | 61.3 | 58.0 (56.9–59.0) | 68.2 | 29 | 664 |
| paparazzi | 101.4 | 51.8 (51.5–52.0) | 64.5 | 26 | 834 |
| roborazzi-android | 75.5 | 67.3 (65.9–67.7) | 82.1 | 34 | 1204 |

### Cost of one more screenshot and of the run itself (warm verify, one JVM, N=1000 → 2000)

| tool | ms per additional screenshot | fixed seconds per run |
|---|---|---|
| viddik | 25 | -0.2 |
| roborazzi-desktop | 28 | 1.1 |
| paparazzi | 23 | 5.6 |
| roborazzi-android | 26 | 15.8 |

### Forks (N = 200, warm verify)

| tool | 1 fork | 2 forks | 4 forks | 1 → 4 |
|---|---|---|---|---|
| viddik | 8.9 | 5.3 | 5.1 | ×1.75 |
| roborazzi-desktop | 9.8 | — | 5.0 | ×1.96 |
| paparazzi | 11.1 | — | 9.2 | ×1.21 |
| roborazzi-android | 18.0 | — | 13.5 | ×1.33 |

### Forks (N = 1000, warm verify)

| tool | 1 fork | 2 forks | 4 forks | 1 → 4 |
|---|---|---|---|---|
| viddik | 25.1 | — | 10.1 | ×2.48 |
| roborazzi-desktop | 29.6 | — | 10.9 | ×2.71 |
| paparazzi | 28.7 | — | 15.7 | ×1.82 |
| roborazzi-android | 41.5 | — | 25.8 | ×1.61 |

### Forks (N = 2000, warm verify)

| tool | 1 fork | 2 forks | 4 forks | 1 → 4 |
|---|---|---|---|---|
| viddik | 50.5 | — | 14.8 | ×3.42 |
| roborazzi-desktop | 58.0 | — | 17.9 | ×3.24 |
| paparazzi | 51.8 | — | 22.7 | ×2.28 |
| roborazzi-android | 67.3 | — | 35.9 | ×1.87 |

### Does verify fail when the picture changes? (N=10, default tolerances)

| tool | unchanged | heading + full stop | first letter → X |
|---|---|---|---|
| viddik | 0/10 failed | 2/10 caught | 10/10 caught |
| roborazzi-desktop | 0/10 failed | 10/10 caught | 10/10 caught |
| paparazzi | 0/10 failed | 2/10 caught | 10/10 caught |
| roborazzi-android | 0/10 failed | 10/10 caught | 10/10 caught |

### Inner loop: one golden, warm daemon (inner-n1000-0.6.1.42, fixture f500)

| tool | no edit | after a body-only edit | tasks run after the edit |
|---|---|---|---|
| viddik | 2.8 | 4.1 | kspKotlin compileKotlin jar kspTestKotlin viddikRecord |
| roborazzi-desktop | 2.4 | 2.9 | compileKotlin jar test finalizeTestRoborazziJvm |
| paparazzi | 5.0 | 5.5 | compileDebugKotlin bundleLibRuntimeToJarDebug bundleLibCompileToJarDebug transformDebugUnitTestClassesWithAsm testDebugUnitTest recordPaparazziDebug |
| roborazzi-android | 7.0 | 7.2 | compileDebugKotlin bundleLibRuntimeToJarDebug bundleLibCompileToJarDebug testDebugUnitTest finalizeTestRoborazziDebug |

### Inner loop: one golden, warm daemon (inner-n1000, fixture f500)

| tool | no edit | after a body-only edit | tasks run after the edit |
|---|---|---|---|
| viddik | 2.9 | 3.3 | kspKotlin compileKotlin jar viddikKspTestKotlinDeclarations viddikRecord |
| roborazzi-desktop | 2.6 | 2.8 | compileKotlin jar test finalizeTestRoborazziJvm |
| paparazzi | 5.1 | 5.5 | compileDebugKotlin bundleLibRuntimeToJarDebug bundleLibCompileToJarDebug transformDebugUnitTestClassesWithAsm testDebugUnitTest recordPaparazziDebug |
| roborazzi-android | 7.1 | 7.4 | compileDebugKotlin bundleLibRuntimeToJarDebug bundleLibCompileToJarDebug testDebugUnitTest finalizeTestRoborazziDebug |

### Linux goldens on macOS

```
# N=50 recorded on Linux (WSL2, amd64) and on macOS (M1, arm64); pixel comparison, no tool tolerance
viddik: 50 compared, 38 identical, median 0.000% px differ, worst bench_f043.png 13 px (0.006%), max channel delta 47
roborazzi-desktop: 50 compared, 0 identical, median 4.253% px differ, worst f004.png 20345 px (8.830%), max channel delta 255
roborazzi-desktop-font: 50 compared, 0 identical, median 1.651% px differ, worst f024.png 8167 px (3.545%), max channel delta 138
roborazzi-android: 50 compared, 50 identical, median 0.000% px differ, worst f000.png 0 px (0.000%), max channel delta 0
paparazzi: 50 compared, 50 identical, median 0.000% px differ, worst bench_PaparazziTest00_f000.png 0 px (0.000%), max channel delta 0

# Each tool's own verify on macOS against the Linux goldens, default settings
viddik: 0/50 failed
roborazzi-desktop: 50/50 failed
roborazzi-android: 0/50 failed
paparazzi: 0/50 failed
```
