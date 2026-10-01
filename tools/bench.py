#!/usr/bin/env python3
"""Time record and verify for each tool on the fixtures currently generated.

Runs on the build machine, inside the checkout:

    tools/bench.py --reps 5 --tools viddik,roborazzi-desktop --out results/raw/n50.json

For every tool: one warm-up record (compiles, fills the daemon), then `reps` rounds of record and
verify on the warm daemon, then `cold` rounds of verify after `gradlew --stop`. Each measured
invocation passes a fresh -PbenchRun, so the Test task always executes; the JUnit XML it leaves is
read back to prove that — a run whose test count is not N is reported as invalid, not as fast.

Durations are time.monotonic(). On the build machine these numbers come from (a WSL2 guest) that
clock runs ~4-10% slow against wall time; run-all.sh measures the whole run with the driving
machine's clock, and summarize.py applies the ratio. Ratios between tools do not depend on it.
"""
import argparse
import glob
import json
import os
import random
import re
import shutil
import subprocess
import threading
import time
import xml.etree.ElementTree as ET

TOOLS = {
    "viddik": {
        "record": [":viddik:viddikRecord"],
        "verify": [":viddik:viddikVerify"],
        "goldens": ["viddik/build/goldens"],
        "results": {"record": "viddik/build/test-results/viddikRecord",
                    "verify": "viddik/build/test-results/viddikVerify"},
    },
    "roborazzi-desktop": {
        "record": [":roborazzi-desktop:test", "-Proborazzi.test.record=true"],
        "verify": [":roborazzi-desktop:test", "-Proborazzi.test.verify=true"],
        "goldens": ["roborazzi-desktop/build/goldens", "roborazzi-desktop/build/outputs/roborazzi"],
        "results": {"record": "roborazzi-desktop/build/test-results/test",
                    "verify": "roborazzi-desktop/build/test-results/test"},
    },
    "roborazzi-android": {
        "record": [":roborazzi-android:testDebugUnitTest", "-Proborazzi.test.record=true"],
        "verify": [":roborazzi-android:testDebugUnitTest", "-Proborazzi.test.verify=true"],
        "goldens": ["roborazzi-android/build/goldens", "roborazzi-android/build/outputs/roborazzi"],
        "results": {"record": "roborazzi-android/build/test-results/testDebugUnitTest",
                    "verify": "roborazzi-android/build/test-results/testDebugUnitTest"},
    },
    "paparazzi": {
        "record": [":paparazzi:recordPaparazziDebug"],
        "verify": [":paparazzi:verifyPaparazziDebug"],
        "goldens": ["paparazzi/src/test/snapshots"],
        "results": {"record": "paparazzi/build/test-results/testDebugUnitTest",
                    "verify": "paparazzi/build/test-results/testDebugUnitTest"},
    },
}


def fixture_count():
    src = open("fixtures/src/bench/Fixtures.kt").read()
    return int(src.split("const val FIXTURE_COUNT = ")[1].split("\n")[0])


class RssSampler(threading.Thread):
    """Peak summed RSS of the test JVMs (Gradle Test Executor N), sampled every 200 ms."""

    def __init__(self):
        super().__init__(daemon=True)
        self.peak_kb = 0
        self.stop = threading.Event()

    def run(self):
        if not os.path.isdir("/proc"):  # macOS: no /proc, no RSS figure
            return
        while not self.stop.is_set():
            total = 0
            for pid in os.listdir("/proc"):
                if not pid.isdigit():
                    continue
                try:
                    cmd = open(f"/proc/{pid}/cmdline", "rb").read()
                    if b"Gradle Test Executor" not in cmd:
                        continue
                    for line in open(f"/proc/{pid}/status"):
                        if line.startswith("VmRSS:"):
                            total += int(line.split()[1])
                except OSError:
                    pass
            self.peak_kb = max(self.peak_kb, total)
            self.stop.wait(0.2)


FIXTURE = re.compile(r"(^|[ .])f\d{3,}$")  # gen.py pads to three digits; N=2000 reaches f1999


def read_results(results_dir):
    """Fixture testcases only: viddik adds its own bookkeeping cases ("Capture session",
    "Record summary") that are not captures and would inflate the count."""
    tests = failures = 0
    test_seconds = 0.0
    for f in glob.glob(f"{results_dir}/**/*.xml", recursive=True):
        root = ET.parse(f).getroot()
        suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
        for s in suites:
            test_seconds += float(s.get("time", 0))
            for case in s.findall("testcase"):
                if not FIXTURE.search(case.get("name", "")):
                    continue
                tests += 1
                if case.find("failure") is not None or case.find("error") is not None:
                    failures += 1
    return tests, failures, test_seconds


def gradle(args, forks, log, extra=()):
    cmd = ["./gradlew", "--console=plain", f"-PbenchRun={random.getrandbits(48)}", *args, *extra]
    if forks:
        cmd.append(f"-PbenchForks={forks}")
    sampler = RssSampler()
    sampler.start()
    start_wall = time.time()
    t0 = time.monotonic()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    elapsed = time.monotonic() - t0
    sampler.stop.set()
    sampler.join()
    with open(log, "a") as fh:
        fh.write(f"\n$ {' '.join(cmd)}\n{proc.stdout}")
    return proc.returncode, elapsed, sampler.peak_kb, start_wall


GRADLE_ARGS = []


def measure(tool, mode, forks, n, log, extra=()):
    spec = TOOLS[tool]
    extra = (*GRADLE_ARGS, *extra)
    # The results directory is emptied first, so what is read back belongs to this run — file mtimes
    # cannot be trusted on a guest whose realtime clock jumps by seconds.
    shutil.rmtree(spec["results"][mode], ignore_errors=True)
    rc, elapsed, rss, _ = gradle(spec[mode], forks, log, extra)
    tests, failures, test_seconds = read_results(spec["results"][mode])
    return {
        "tool": tool, "mode": mode, "forks": forks or 1, "n": n,
        "seconds": round(elapsed, 3), "test_seconds": round(test_seconds, 3),
        "exit": rc, "tests": tests, "failures": failures, "peak_rss_mb": rss // 1024,
        "valid": rc == 0 and tests == n and failures == 0,
    }


# One fixture, the way a developer or an agent asks for it while editing a component.
SINGLE = {
    "viddik": lambda i: [":viddik:viddikRecord", "--component", f"bench - f{i:03d}", "--force"],
    "roborazzi-desktop": lambda i: [":roborazzi-desktop:test", "--tests", f"bench.RoborazziDesktopTest{i // 10:02d}.f{i:03d}",
                                    "-Proborazzi.test.record=true"],
    "roborazzi-android": lambda i: [":roborazzi-android:testDebugUnitTest", "--tests",
                                    f"bench.RoborazziAndroidTest{i // 10:02d}.f{i:03d}", "-Proborazzi.test.record=true"],
    "paparazzi": lambda i: [":paparazzi:recordPaparazziDebug", "--tests", f"bench.PaparazziTest{i // 10:02d}.f{i:03d}"],
}


def one(tool, fixture, label, log):
    """Record a single fixture once on the warm daemon; print the wall time and which tasks ran."""
    rc, elapsed, rss, _ = gradle(SINGLE[tool](fixture), 1, log)
    out = open(log).read().rsplit("\n$ ", 1)[-1]
    ran = [l.split()[2] for l in out.splitlines()
           if l.startswith("> Task ") and not l.rstrip().endswith(("UP-TO-DATE", "NO-SOURCE", "SKIPPED", "FROM-CACHE"))]
    row = {"tool": tool, "phase": label, "fixture": fixture, "seconds": round(elapsed, 3), "exit": rc,
           "peak_rss_mb": rss // 1024, "tasks_run": ran}
    print(json.dumps(row), flush=True)
    return row


def main():
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--one":
        # tools/bench.py --one TOOL FIXTURE LABEL OUT.jsonl
        tool, fixture, label, out = os.sys.argv[2], int(os.sys.argv[3]), os.sys.argv[4], os.sys.argv[5]
        os.makedirs(os.path.dirname(out), exist_ok=True)
        row = one(tool, fixture, label, out.replace(".jsonl", ".log"))
        with open(out, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--cold", type=int, default=3)
    ap.add_argument("--forks", type=int, default=0)
    ap.add_argument("--tools", default=",".join(TOOLS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--gradle-arg", action="append", default=[],
                    help="passed to every measured Gradle invocation, e.g. -PbenchStrict")
    ap.add_argument("--sensitivity", action="store_true",
                    help="record clean, then verify against perturbed pictures; count what was caught")
    a = ap.parse_args()

    GRADLE_ARGS.extend(a.gradle_arg)
    n = fixture_count()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    log = a.out.replace(".json", ".log")
    open(log, "w").close()
    rows = []
    t_start = time.monotonic()
    load = [f"{x:.2f}" for x in os.getloadavg()]

    if a.sensitivity:
        for tool in a.tools.split(","):
            for d in TOOLS[tool]["goldens"]:
                shutil.rmtree(d, ignore_errors=True)
            measure(tool, "record", a.forks, n, log)
            for level in ("none", "dot", "word"):
                extra = () if level == "none" else (f"-PbenchPerturb={level}",)
                r = measure(tool, "verify", a.forks, n, log, extra)
                r["phase"] = f"perturb-{level}"
                r["caught"] = r["failures"]
                rows.append(r)
                print(json.dumps(r), flush=True)
    for tool in ([] if a.sensitivity else a.tools.split(",")):
        for d in TOOLS[tool]["goldens"]:
            shutil.rmtree(d, ignore_errors=True)
        warm = measure(tool, "record", a.forks, n, log)
        warm["phase"] = "warmup"
        rows.append(warm)
        print(json.dumps(warm), flush=True)
        for _ in range(a.reps):
            for mode in ("record", "verify"):
                r = measure(tool, mode, a.forks, n, log)
                r["phase"] = "warm"
                rows.append(r)
                print(json.dumps(r), flush=True)
        for _ in range(a.cold):
            subprocess.run(["./gradlew", "--stop"], stdout=subprocess.DEVNULL)
            r = measure(tool, "verify", a.forks, n, log)
            r["phase"] = "cold-daemon"
            rows.append(r)
            print(json.dumps(r), flush=True)

    out = {
        "n": n, "reps": a.reps, "forks": a.forks or 1, "forks_passed": a.forks, "rows": rows,
        "monotonic_total": round(time.monotonic() - t_start, 3),
        "loadavg_at_start": load, "nproc": os.cpu_count(),
        "java_home": os.environ.get("JAVA_HOME", ""), "gradle_args": a.gradle_arg,
    }
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"DONE {a.out} monotonic_total={out['monotonic_total']}", flush=True)


if __name__ == "__main__":
    main()
