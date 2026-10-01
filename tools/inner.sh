#!/usr/bin/env bash
# The inner loop: edit a component, get one fresh golden. Run from the workstation, against a
# module of N fixtures that has already been built and recorded on the build machine.
#
#   tools/gen.py 1000 && tools/inner.sh 500 5
#
# For each tool and each rep: once with no source change (the tool's floor: task graph, test JVM,
# one render), once right after an edit of the component fixture <i> draws (ListScreen's heading,
# a body-only change, so Kotlin's incremental compilation applies as it would for a real edit).
# The edit is made here and reaches the build machine the way BENCH_REMOTE carries the tree, like an
# editor's would; only the Gradle invocation on the build machine is timed.
set -euo pipefail
cd "$(dirname "$0")/.."
. tools/remote.sh
fixture=${1:-500}
reps=${2:-5}
out=results/raw/inner-n$(sed -n 's/.*FIXTURE_COUNT = \([0-9]*\).*/\1/p' fixtures/src/bench/Fixtures.kt).jsonl
templates=fixtures/src/bench/Templates.kt
grep -qF 'heading("Payments #$seed")' "$templates"
on_build_machine "rm -f $out ${out%.jsonl}.log"
toggle() {
  if grep -qF 'heading("Payments #$seed")' "$templates"; then
    perl -pi -e 's/heading\("Payments #\$seed"\)/heading("Payment #\$seed")/' "$templates"
  else
    perl -pi -e 's/heading\("Payment #\$seed"\)/heading("Payments #\$seed")/' "$templates"
  fi
}
trap 'grep -qF "heading(\"Payment #" "$templates" && toggle; true' EXIT
for tool in viddik roborazzi-desktop paparazzi roborazzi-android; do
  on_build_machine "python3 tools/bench.py --one $tool $fixture settle $out >/dev/null"
  for _ in $(seq "$reps"); do
    on_build_machine "python3 tools/bench.py --one $tool $fixture no-edit $out"
    toggle
    on_build_machine "python3 tools/bench.py --one $tool $fixture edit $out"
  done
done
fetch "$out" results/raw/
echo "DONE $out"
