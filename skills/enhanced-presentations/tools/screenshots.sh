#!/bin/bash
# Screenshots of specific steps (1600×900) and contact sheets with the step number.
#   usage: [OUT=folder] [AT=ms] screenshots.sh theme.html step|from-to [...]
#   e.g.: OUT=/tmp/cap screenshots.sh theme.html 5-8 12   (the step map is given by review.py)
# Output: pNN.png (one per step) and sheet-1.png, sheet-2.png… (6 screenshots per sheet, 2 columns).
# Screenshots are taken with ?static (no transitions) and ?t=AT: animations are
# frozen at that instant (default 7500 ms, when the processes have already finished).
# To see an intermediate instant of an animation: AT=1500 screenshots.sh ...
source "$(dirname "$0")/_chrome.sh"
F=$(realpath "$1"); shift
OUT=${OUT:-$(mktemp -d)}; mkdir -p "$OUT"
STEPS=()
for a in "$@"; do
  if [[ "$a" =~ ^([0-9]+)-([0-9]+)$ ]]; then STEPS+=($(seq "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")); else STEPS+=("$a"); fi
done
for n in "${STEPS[@]}"; do
  timeout 30 "$CHROME" $CHROME_FLAGS --window-size=1600,900 --timeout=${T:-2000} \
    --screenshot="$OUT/p$(printf %02d $n).png" "file://$F?static&t=${AT:-7500}#$n" >/dev/null 2>&1
done
python3 - "$OUT" "${STEPS[@]}" <<'PY'
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
out, ns = sys.argv[1], sys.argv[2:]
for f in glob.glob(f'{out}/sheet-*.png'): os.remove(f)
try: font = ImageFont.truetype('DejaVuSans-Bold.ttf', 34)
except OSError: font = ImageFont.load_default()
for h, j in enumerate(range(0, len(ns), 6)):
    group = ns[j:j + 6]
    ims = [Image.open(f'{out}/p{int(n):02d}.png').convert('RGB') for n in group]
    w, hh = ims[0].size; c = 2 if len(ims) > 1 else 1; r = (len(ims) + c - 1) // c
    s = Image.new('RGB', (w * c + 12 * (c - 1), hh * r + 12 * (r - 1)), (120, 120, 120))
    for i, (im, n) in enumerate(zip(ims, group)):
        x, y = (i % c) * (w + 12), (i // c) * (hh + 12)
        s.paste(im, (x, y))
        d = ImageDraw.Draw(s); d.rectangle([x, y, x + 110, y + 50], fill=(31, 31, 31)); d.text((x + 12, y + 6), f'#{n}', fill='white', font=font)
    s.save(f'{out}/sheet-{h + 1}.png'); print(f'{out}/sheet-{h + 1}.png')
PY
