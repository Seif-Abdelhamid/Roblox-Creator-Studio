#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 2 ]; then
  echo "Usage: $0 input.mp4 output.gif" >&2
  exit 1
fi
in=$1
out=$2
palette=$(mktemp /tmp/palette-XXXX.png)
# Generate palette
ffmpeg -v warning -i "$in" -vf "fps=15,scale=960:-1:flags=lanczos,palettegen" -y "$palette"
# Apply palette
ffmpeg -v warning -i "$in" -i "$palette" -lavfi "fps=15,scale=960:-1:flags=lanczos [x]; [x][1:v] paletteuse" -y "$out"
rm -f "$palette"
echo "Wrote $out"