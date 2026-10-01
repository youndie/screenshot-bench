#!/usr/bin/env python3
"""Turn results/raw/*.json into results/summary.md and results/summary.json.

    tools/summarize.py

Seconds are corrected from the build machine's monotonic clock to wall time with the factor
measured by run-all.sh (the driving machine's clock over the build machine's for the same runs). A row that is not valid —
wrong test count, failures, non-zero exit — is excluded and counted, never averaged in.
"""
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw"
TOOLS = ["viddik", "roborazzi-desktop", "paparazzi", "roborazzi-android"]


def clock_factor():
    mac = {}
    for line in (RAW / "mac-clock.txt").read_text().splitlines():
        m = re.match(r"(\S+) rc=0 mac_seconds=([\d.]+)", line)
        if m:
            mac[m.group(1)] = float(m.group(2))
    ratios = []
    for name, secs in mac.items():
        f = RAW / f"{name}.json"
        if f.exists():
            ratios.append(secs / json.loads(f.read_text())["monotonic_total"])
    # The driver's number also holds ssh, sync and gen.py — seconds against a run of minutes. Taking
    # the smallest ratio keeps that overhead out rather than folding it into every row.
    return min(ratios) if ratios else 1.0, ratios


def med(rows, key="seconds"):
    return statistics.median(r[key] for r in rows) if rows else None


def effective_forks(tool, run_name, run):
    """How many test JVMs a tool actually used in a run. viddik sets maxParallelForks from its own
    `shards` (two by default), and before -PbenchForks was routed there the shared knob did not reach
    it — so in the all-tools runs viddik ran on two forks whatever the run says."""
    passed = run.get("forks_passed", run["forks"] if "viddik" in run_name else 0)
    if tool == "viddik" and not passed:
        return 2
    return run["forks"]


def stats(rows, n, factor):
    rec = [r for r in rows if r["phase"] == "warm" and r["mode"] == "record"]
    ver = [r for r in rows if r["phase"] == "warm" and r["mode"] == "verify"]
    cold = [r for r in rows if r["phase"] == "cold-daemon"]
    if not ver:
        return None
    return {
        "record": med(rec) * factor if rec else None,
        "verify": med(ver) * factor,
        "cold": med(cold) * factor if cold else None,
        "test_seconds": med(ver, "test_seconds") * factor,
        "rss": max(r["peak_rss_mb"] for r in rows),
        "spread": [min(r["seconds"] for r in ver) * factor, max(r["seconds"] for r in ver) * factor],
        "ms_per_fixture": 1000 * med(ver) * factor / n,
    }


def main():
    factor, ratios = clock_factor()
    runs = {p.stem: json.loads(p.read_text()) for p in sorted(RAW.glob("n*.json"))}
    # (tool, n, forks) -> stats; `defaults` marks viddik at its own default of two forks.
    cells, invalid = {}, 0
    for name, run in runs.items():
        for tool in TOOLS:
            rows = [r for r in run["rows"] if r["tool"] == tool]
            invalid += sum(1 for r in rows if not r["valid"])
            st = stats([r for r in rows if r["valid"]], run["n"], factor)
            if st:
                st["run"] = name
                key = (tool, run["n"], effective_forks(tool, name, run))
                # A run dedicated to one tool (its name says which) was made later, against a newer
                # build of that tool, and wins over the all-tools run of the same size and forks.
                if key in cells and tool in cells[key]["run"] and tool not in name:
                    continue
                cells[key] = st

    out = {"clock_factor": factor, "clock_ratios": ratios, "invalid_rows": invalid,
           "cells": {f"{t}|{n}|{f}": v for (t, n, f), v in cells.items()}}
    fmt = lambda v: "—" if v is None else f"{v:.1f}"
    md = [f"Wall-clock seconds, median of the warm runs; build-machine clock corrected ×{factor:.3f}. "
          f"Invalid rows excluded: {invalid}.\n"]

    for n in sorted({n for (_, n, _) in cells}):
        md.append(f"\n### N = {n}, one test JVM per tool\n")
        md.append("| tool | record | verify (min–max) | verify, fresh daemon | ms per screenshot | peak RSS of test JVMs, MB |")
        md.append("|---|---|---|---|---|---|")
        for tool, label in [(t, t) for t in TOOLS] + [("viddik", "viddik, its default (2 forks)")]:
            forks = 2 if label.startswith("viddik,") else 1
            c = cells.get((tool, n, forks))
            if c:
                md.append(f"| {label} | {fmt(c['record'])} | {fmt(c['verify'])} ({c['spread'][0]:.1f}–{c['spread'][1]:.1f}) | "
                          f"{fmt(c['cold'])} | {c['ms_per_fixture']:.0f} | {c['rss']} |")

    ns = sorted({n for (t, n, f) in cells if f == 1 and n >= 50})
    if len(ns) >= 2:
        n1, n2 = ns[-2], ns[-1]
        md.append(f"\n### Cost of one more screenshot and of the run itself (warm verify, one JVM, N={n1} → {n2})\n")
        md.append("| tool | ms per additional screenshot | fixed seconds per run |")
        md.append("|---|---|---|")
        out["marginal"] = {}
        for tool in TOOLS:
            a, b = cells.get((tool, n1, 1)), cells.get((tool, n2, 1))
            if a and b:
                slope = (b["verify"] - a["verify"]) / (n2 - n1)
                fixed = a["verify"] - slope * n1
                out["marginal"][tool] = {"ms": slope * 1000, "fixed_s": fixed}
                md.append(f"| {tool} | {slope * 1000:.0f} | {fixed:.1f} |")

    for n in sorted({n for (_, n, f) in cells if f == 4}):
        md.append(f"\n### Forks (N = {n}, warm verify)\n")
        md.append("| tool | 1 fork | 2 forks | 4 forks | 1 → 4 |")
        md.append("|---|---|---|---|---|")
        for tool in TOOLS:
            v = {f: cells.get((tool, n, f)) for f in (1, 2, 4)}
            if v[1] and v[4]:
                md.append(f"| {tool} | {v[1]['verify']:.1f} | {fmt(v[2]['verify'] if v[2] else None)} | "
                          f"{v[4]['verify']:.1f} | ×{v[1]['verify'] / v[4]['verify']:.2f} |")

    sens = RAW / "sensitivity.json"
    if sens.exists():
        s = json.loads(sens.read_text())
        md.append(f"\n### Does verify fail when the picture changes? (N={s['n']}, default tolerances)\n")
        md.append("| tool | unchanged | heading + full stop | first letter → X |")
        md.append("|---|---|---|---|")
        for tool in TOOLS:
            r = {x["phase"]: x for x in s["rows"] if x["tool"] == tool}
            if r:
                md.append(f"| {tool} | {r['perturb-none']['caught']}/{s['n']} failed | "
                          f"{r['perturb-dot']['caught']}/{s['n']} caught | {r['perturb-word']['caught']}/{s['n']} caught |")

    for inner in sorted(RAW.glob("inner-n*.jsonl")):
        rows = [json.loads(l) for l in inner.read_text().splitlines()]
        md.append(f"\n### Inner loop: one golden, warm daemon ({inner.stem}, fixture f{rows[0]['fixture']:03d})\n")
        md.append("| tool | no edit | after a body-only edit | tasks run after the edit |")
        md.append("|---|---|---|---|")
        for tool in TOOLS:
            r = {ph: [x for x in rows if x["tool"] == tool and x["phase"] == ph] for ph in ("no-edit", "edit")}
            if r["edit"]:
                tasks = " ".join(t.rsplit(":", 1)[-1] for t in r["edit"][0]["tasks_run"])
                md.append(f"| {tool} | {med(r['no-edit']) * factor:.1f} | {med(r['edit']) * factor:.1f} | {tasks} |")

    cross = RAW / "cross-os.txt"
    if cross.exists():
        md.append("\n### Linux goldens on macOS\n\n```\n" + cross.read_text().strip() + "\n```")

    (ROOT / "results" / "summary.md").write_text("\n".join(md) + "\n")
    (ROOT / "results" / "summary.json").write_text(json.dumps(out, indent=1))
    print("\n".join(md))


if __name__ == "__main__":
    main()
