#!/bin/bash
# Prepares any source for reading: one image per slide, page or panel, contact
# sheets, text per page and the original photos when the format is a package.
#   usage: [DPI=130] source_to_images.sh SOURCE output_folder   (default DPI 80)
# SOURCE: .pptx .odp .pdf .docx .odt .rtf .xlsx .html … (converted by LibreOffice) or .md/.txt
# Output: slides/d-NN.png · contacts-N.png (12 per sheet) · text.txt · media/ + media.txt
# NOTE: pdftotext does not capture text written in equations or inside images:
# the reference content is the slide or page images, not text.txt.
# For a text-only source there are no images: the text is copied as is to text.txt.
set -e
IN=$(realpath "$1"); OUT=${2:?missing output folder}; mkdir -p "$OUT"; OUT=$(realpath "$OUT")
# discard artifacts from a previous run so nothing stale survives in OUT
rm -rf "$OUT/slides" "$OUT/media" "$OUT/_x" "$OUT/media.txt" "$OUT/text.txt" "$OUT"/contacts-*.png
BASE=$(basename "$IN"); EXT=${BASE##*.}; EXT=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')
case "$EXT" in
  txt|md)
    cp "$IN" "$OUT/text.txt"
    echo "Text source: read $OUT/text.txt in full (there are no slide images)."
    exit 0;;
esac
mkdir -p "$OUT/slides"
PDF="$IN"
if [ "$EXT" != pdf ]; then
  command -v soffice >/dev/null || { echo "LibreOffice (soffice) is required to convert $BASE; export it to PDF and try again." >&2; exit 1; }
  soffice --headless --convert-to pdf --outdir "$OUT" "$IN" >/dev/null 2>&1 || { echo "LibreOffice could not convert $BASE" >&2; exit 1; }
  PDF="$OUT/${BASE%.*}.pdf"
  [ -f "$PDF" ] || { echo "Could not find the PDF generated from $BASE" >&2; exit 1; }
fi
# original photos when the source is a package (pptx, odp); for the rest,
# images embedded in the generated PDF are extracted with pdfimages
mkdir -p "$OUT/media"
case "$EXT" in
  pptx)
    if command -v unzip >/dev/null; then
      unzip -qo "$IN" 'ppt/media/*' -d "$OUT/_x" || true
      [ -d "$OUT/_x" ] && find "$OUT/_x" -type l -delete || true
      if [ -d "$OUT/_x/ppt/media" ]; then
        find "$OUT/_x/ppt/media" -type f -exec mv {} "$OUT/media/" \;
      fi
      unzip -qo "$IN" 'ppt/slides/_rels/*' -d "$OUT/_x" || true
      [ -d "$OUT/_x" ] && find "$OUT/_x" -type l -delete || true
      for r in $(ls "$OUT/_x/ppt/slides/_rels/" 2>/dev/null | sort -V); do
        n=${r#slide}; n=${n%.xml.rels}
        echo "Slide $n: $(grep -o 'media/[^"]*' "$OUT/_x/ppt/slides/_rels/$r" | sed 's#media/##' | sort -u | tr '\n' ' ')"
      done > "$OUT/media.txt"
    else
      echo "WARNING: unzip is not installed: photos inside $BASE are not extracted." >&2
      : > "$OUT/media.txt"
    fi;;
  odp)
    if command -v unzip >/dev/null; then
      unzip -qo "$IN" 'Pictures/*' -d "$OUT/_x" || true
      [ -d "$OUT/_x" ] && find "$OUT/_x" -type l -delete || true
      if [ -d "$OUT/_x/Pictures" ]; then
        find "$OUT/_x/Pictures" -type f -exec mv {} "$OUT/media/" \;
      fi
      ls "$OUT/media" 2>/dev/null | sed 's/^/Image: /' > "$OUT/media.txt"
    else
      echo "WARNING: unzip is not installed: photos inside $BASE are not extracted." >&2
      : > "$OUT/media.txt"
    fi;;
  *)
    if command -v pdfimages >/dev/null; then
      pdfimages -png "$PDF" "$OUT/media/img" || echo "WARNING: pdfimages could not extract the images embedded in $BASE." >&2
      pdfimages -list "$PDF" | awk '
        NR > 2 && $1 ~ /^[0-9]+$/ {
          if ($1 != page) { if (line != "") print line; page = $1; line = "Page " $1 ":" }
          line = line " img-" sprintf("%03d", $2) ".png"
        }
        END { if (line != "") print line }
      ' > "$OUT/media.txt"
    else
      echo "WARNING: pdfimages (poppler) is not installed: images inside $BASE are not extracted." >&2
      : > "$OUT/media.txt"
    fi;;
esac
rm -rf "$OUT/_x"
pdftoppm -r ${DPI:-80} -png "$PDF" "$OUT/slides/d" || { echo "pdftoppm could not render $BASE to images" >&2; exit 1; }
N=$(ls "$OUT/slides" | wc -l)
: > "$OUT/text.txt"
for i in $(seq 1 $N); do
  echo "===== Page $i =====" >> "$OUT/text.txt"
  pdftotext -layout -f $i -l $i "$PDF" - >> "$OUT/text.txt" || echo "WARNING: could not extract the text from page $i of $BASE." >&2
done
python3 - "$OUT" <<'PY'
import sys, glob, re
from PIL import Image, ImageDraw
out = sys.argv[1]
fs = sorted(glob.glob(f'{out}/slides/d-*.png'), key=lambda f: int(re.findall(r'(\d+)\.png', f)[0]))
for j in range(0, len(fs), 12):
    ims = [Image.open(f).convert('RGB') for f in fs[j:j+12]]
    w, h = 480, round(480 * ims[0].height / ims[0].width)
    sheet = Image.new('RGB', (4 * w + 30, 3 * (h + 30)), 'white')
    for i, im in enumerate(ims):
        x, y = (i % 4) * (w + 10), (i // 4) * (h + 30)
        sheet.paste(im.resize((w, h)), (x, y + 26))
        ImageDraw.Draw(sheet).text((x + 4, y + 6), f'Page {j + i + 1}', fill='black')
    sheet.save(f'{out}/contacts-{j // 12 + 1}.png')
print(len(fs), 'pages or slides')
PY
echo "Done. Output in $OUT"
