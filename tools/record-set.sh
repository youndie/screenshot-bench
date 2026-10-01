#!/usr/bin/env bash
# Record every tool's goldens on this machine into one directory, for tools/pngdiff.py to compare
# against the same set recorded on another OS.
#
#   tools/record-set.sh results/raw/goldens-linux
#
# Five sets: the four tools as benchmarked, plus roborazzi-desktop drawing with viddik's bundled
# font (-PbenchFont=viddik), which separates what the font does from what the capture engine does.
set -euo pipefail
cd "$(dirname "$0")/.."
out=$1
rm -rf "$out" && mkdir -p "$out"
g() { ./gradlew -q --console=plain "-PbenchRun=$RANDOM$RANDOM" "$@"; }

rm -rf viddik/build/goldens roborazzi-*/build/goldens paparazzi/src/test/snapshots
g :viddik:viddikRecord
g :roborazzi-desktop:test :roborazzi-android:testDebugUnitTest -Proborazzi.test.record=true
g :paparazzi:recordPaparazziDebug
cp -R viddik/build/goldens "$out/viddik"
cp -R roborazzi-desktop/build/goldens "$out/roborazzi-desktop"
cp -R roborazzi-android/build/goldens "$out/roborazzi-android"
cp -R paparazzi/src/test/snapshots/images "$out/paparazzi"

rm -rf roborazzi-desktop/build/goldens
g :roborazzi-desktop:test -Proborazzi.test.record=true -PbenchFont=viddik
cp -R roborazzi-desktop/build/goldens "$out/roborazzi-desktop-font"
echo "DONE $(find "$out" -name '*.png' | wc -l) png in $out"
