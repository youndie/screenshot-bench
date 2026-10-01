# Sourced by run-all.sh and inner.sh: how they reach the machine the builds run on.
#
# Unset, everything runs here, in this checkout. To drive another machine:
#
#   BENCH_REMOTE     a command that runs one shell string in this checkout on the build machine,
#                    after making its copy of the tree current (e.g. a sync, then ssh)
#   BENCH_FETCH      a command taking <path in the checkout> <local directory> that copies a
#                    result file back
#   BENCH_JAVA_HOME  the JDK the builds use there (default: $JAVA_HOME)

on_build_machine() {
  local script="export JAVA_HOME=${BENCH_JAVA_HOME:-${JAVA_HOME:-}}; $1"
  if [ -n "${BENCH_REMOTE:-}" ]; then $BENCH_REMOTE "$script"; else bash -c "$script"; fi
}

fetch() {
  if [ -n "${BENCH_FETCH:-}" ]; then $BENCH_FETCH "$1" "$2"; fi
}
