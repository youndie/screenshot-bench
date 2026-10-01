#!/usr/bin/env bash
# Drive the whole benchmark: generate N fixtures here, run tools/bench.py on the build machine (see
# tools/remote.sh; by default that is this machine), and time each run with this machine's clock, so
# a build machine whose monotonic clock drifts can be corrected (see bench.py and summarize.py).
#
#   tools/run-all.sh                # 10, 50, 200 at defaults + 200 with four forks
#   tools/run-all.sh viddik-forks   # viddik pinned to one and four forks
#   tools/run-all.sh large          # N=1000 and 2000, everyone at 1 and at 4 forks
#   tools/run-all.sh viddik-large   # viddik alone at N=2000, 1 and 4 forks
set -uo pipefail
cd "$(dirname "$0")/.."
. tools/remote.sh
mkdir -p results/raw

step() { # name n forks reps cold [extra bench args]
  local name=$1 n=$2 forks=$3 reps=$4 cold=$5; shift 5
  tools/gen.py "$n"
  local t0 t1
  t0=$(python3 -c 'import time; print(time.time())')
  on_build_machine "python3 tools/bench.py --forks $forks --reps $reps --cold $cold --out results/raw/$name.json $*" \
    > "results/raw/$name.stdout" 2>&1
  local rc=$?
  t1=$(python3 -c 'import time; print(time.time())')
  echo "$name rc=$rc mac_seconds=$(python3 -c "print(round($t1-$t0,3))")" | tee -a results/raw/mac-clock.txt
  # Only this step's file: a glob would also bring back older runs as the build machine has them,
  # over any correction made to them here.
  fetch "results/raw/$name.json" results/raw/
}

if [ "${1:-}" = "large" ]; then
  # Consumer-sized suites. Forks are passed explicitly, 1 and 4, so viddik runs on the same count as
  # the rest instead of its default two. Fewer reps: one verify at N=2000 on Robolectric is minutes.
  step n1000-f1 1000 1 3 1
  step n2000-f1 2000 1 3 1
  step n1000-f4 1000 4 3 0
  step n2000-f4 2000 4 3 0
elif [ "${1:-}" = "viddik-large" ]; then
  # viddik alone at N=1000 and 2000, for a snapshot that compiles there (the registry split, viddik#49).
  step n1000-f1-viddik 1000 1 3 1 --tools viddik
  step n1000-f4-viddik 1000 4 3 0 --tools viddik
  step n2000-f1-viddik 2000 1 3 1 --tools viddik
  step n2000-f4-viddik 2000 4 3 0 --tools viddik
elif [ "${1:-}" = "viddik-forks" ]; then
  # viddik forks on its own (shards = 2 by default); these pin it to the same fork count as the rest.
  step n50-viddik-f1 50 1 5 3 --tools viddik
  step n200-viddik-f1 200 1 5 3 --tools viddik
  step n200-viddik-f4 200 4 3 0 --tools viddik
else
  : > results/raw/mac-clock.txt
  step n10 10 0 5 3
  step n50 50 0 5 3
  step n200 200 0 5 3
  step n200-f4 200 4 3 0
fi
echo "DONE"
