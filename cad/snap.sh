#!/usr/bin/env bash
# snap.sh — log a dated render frame.  usage: MACHINE=megamop NOTE=first-build bash snap.sh
set -euo pipefail
MACHINE="${MACHINE:-megamop}"
NOTE="${NOTE:-update}"
dir="renders/$MACHINE"
mkdir -p "$dir"
n=$(printf '%04d' $(( $(ls "$dir"/*.png 2>/dev/null | wc -l) + 1 )))
cp "build/${MACHINE}_iso.png" "$dir/${n}-${NOTE}.png"
echo "- ${n}-${NOTE}.png — $(date -I) — ${NOTE}" >> "$dir/INDEX.md"
echo "logged $dir/${n}-${NOTE}.png"
