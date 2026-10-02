#!/usr/bin/env python3
"""Read the visual identity of a source presentation and apply it to the HTML presentation.

  theme.py SOURCE.pptx                 → shows the detected accent color and typography
  theme.py SOURCE.pptx --in pres.html  → applies the accent (--acc, --acc-d, --acc-l) to the HTML
  theme.py SOURCE.pptx --in pres.html --fonts → also applies the typography of the source
  theme.py SOURCE.pdf --json           → JSON output (for the report)

It supports PPTX/PPSX (package theme), ODP (colors from styles.xml/content.xml) and PDF
(colors with saturation from the first pages). If the source is a presentation, the
HTML imitates its palette this way; if nothing is detected, the template green is kept.
Only the accent colors are touched: the skill's semantic colors (red for what is
crossed out, blue for the second term, green for what is highlighted…) do not change.
"""
import argparse, colorsys, json, os, re, shutil, subprocess, sys, tempfile, zipfile
from xml.etree import ElementTree as ET

FALLBACK = '#92d050'


def _hex(v):
    v = (v or '').strip().lstrip('#')
    if len(v) == 3:
        v = ''.join(c * 2 for c in v)
    if len(v) == 8:  # ARGB
        v = v[2:]
    return '#' + v.lower() if re.fullmatch(r'[0-9a-fA-F]{6}', v) else ''


def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _sat_lightness(h):
    r, g, b = _rgb(h)
    _, l, s = colorsys.rgb_to_hls(r, g, b)
    return s, l


def _darken(h, f=0.62):
    return '#%02x%02x%02x' % tuple(round(x * f * 255) for x in _rgb(h))


def _lighten(h, white=0.88):
    return '#%02x%02x%02x' % tuple(round((x + (1 - x) * white) * 255) for x in _rgb(h))


FONT_RE = re.compile(r'^[\w .+-]+$')


def _safe_fonts(fonts):
    safe = []
    for f in fonts:
        if FONT_RE.fullmatch(f):
            safe.append(f)
        else:
            print(f'Warning: ignoring unsafe font name {f!r}', file=sys.stderr)
    return safe


def from_pptx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('ppt/theme/theme1.xml')
    root = ET.fromstring(xml)
    colors, fonts = [], []
    scheme = root.find('.//{*}clrScheme')
    if scheme is not None:
        for name in ('accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6', 'dk2', 'lt2'):
            el = scheme.find(f'{{*}}{name}')
            if el is None:
                continue
            c = el.find('{*}srgbClr')
            if c is None:
                c = el.find('{*}sysClr')
            if c is not None:
                h = _hex(c.get('val') or c.get('lastClr'))
                if h:
                    colors.append(h)
    fs = root.find('.//{*}fontScheme')
    if fs is not None:
        for tag in ('majorFont', 'minorFont'):
            e = fs.find(f'{{*}}{tag}/{{*}}latin')
            if e is not None and e.get('typeface'):
                fonts.append(e.get('typeface'))
    return colors, fonts


def from_odp(path):
    count, fonts = {}, []
    with zipfile.ZipFile(path) as z:
        for n in ('styles.xml', 'content.xml'):
            try:
                data = z.read(n).decode('utf-8', 'replace')
            except KeyError:
                continue
            for m in re.finditer(r'(?:fo:color|draw:fill-color|svg:stroke-color)="#([0-9A-Fa-f]{6})"', data):
                h = _hex(m.group(1))
                count[h] = count.get(h, 0) + 1
            for m in re.finditer(r'(?:style:font-name|fo:font-family)="([^"]+)"', data):
                f = m.group(1).split(',')[0].strip().strip("'")
                if f and f not in fonts:
                    fonts.append(f)
    return [c for c, _ in sorted(count.items(), key=lambda kv: -kv[1])], fonts


def from_pdf(path):
    if not shutil.which('pdftoppm'):
        return [], []
    try:
        from PIL import Image
    except ImportError:
        return [], []
    count = {}
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '50', '-png', '-f', '1', '-l', '3', path, os.path.join(d, 'p')],
                       capture_output=True)
        for f in sorted(os.listdir(d)):
            im = Image.open(os.path.join(d, f)).convert('RGB').resize((160, 100))
            data = im.tobytes()
            for i in range(0, len(data), 3):
                px = (data[i], data[i + 1], data[i + 2])
                if max(px) - min(px) < 40 or max(px) < 60 or min(px) > 230:
                    continue  # gray, black or white
                key = '#%02x%02x%02x' % tuple(v // 16 * 16 for v in px)
                count[key] = count.get(key, 0) + 1
    return [c for c, _ in sorted(count.items(), key=lambda kv: -kv[1])][:8], []


def accent(colors):
    for c in colors:
        s, l = _sat_lightness(c)
        if s >= 0.25 and 0.18 <= l <= 0.72:
            return c
    return colors[0] if colors else FALLBACK


def main():
    ap = argparse.ArgumentParser(description='Style (palette and typography) of a source presentation',
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument('source')
    ap.add_argument('--in', dest='in_', metavar='pres.html', help='apply the style to this HTML presentation')
    ap.add_argument('--fonts', action='store_true', help='also apply the detected typography')
    ap.add_argument('--json', action='store_true', help='JSON output')
    a = ap.parse_args()
    ext = os.path.splitext(a.source)[1].lower()
    if ext in ('.pptx', '.ppsx'):
        colors, fonts = from_pptx(a.source)
    elif ext == '.odp':
        colors, fonts = from_odp(a.source)
    elif ext == '.pdf':
        colors, fonts = from_pdf(a.source)
    else:
        sys.exit('theme.py supports .pptx, .ppsx, .odp and .pdf; for Word or other documents, export them to PDF.')
    fonts = _safe_fonts(fonts)
    if a.fonts and not fonts:
        applied = ' Only colors were applied.' if a.in_ else ' Only colors can be detected.'
        print(('Warning: typography is not available for PDF sources; export to PPTX/ODP or set --font by hand.'
               if ext == '.pdf' else 'Warning: no typography detected in the source.') + applied, file=sys.stderr)
    acc = accent(colors)
    data = {'source': os.path.basename(a.source), 'accent': acc, 'dark': _darken(acc),
            'light': _lighten(acc), 'colors': colors[:8], 'fonts': fonts[:4]}
    if a.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f'Source: {data["source"]}')
        print(f'Accent: {data["accent"]} · dark: {data["dark"]} · light: {data["light"]}'
              + ('' if colors else '  (no colors detected: the template green is kept)'))
        if data['colors']:
            print('Own colors: ' + ', '.join(data['colors']))
        if fonts:
            print('Typography: ' + ', '.join(fonts))
    if a.in_ and (colors or (a.fonts and fonts)):
        src = open(a.in_, encoding='utf-8').read()
        applied = []
        if colors:
            for var, val in (('--acc', data['accent']), ('--acc-d', data['dark']), ('--acc-l', data['light'])):
                src, n = re.subn(rf'({re.escape(var)}:\s*)#[0-9a-fA-F]{{3,6}}', lambda m: m.group(1) + val, src, count=1)
                if not n:
                    sys.exit(f'"{var}" not found in {a.in_}: is it a presentation created with new.py?')
            applied.append('--acc, --acc-d, --acc-l')
        if a.fonts and fonts:
            chain = ', '.join(f'"{f}"' for f in dict.fromkeys(fonts[:2] + ['Calibri', 'Carlito', 'Arial', 'sans-serif']))
            src, n = re.subn(r'--font:\s*[^;]+;', lambda m: f'--font: {chain};', src, count=1)
            if not n:
                print('Warning: "--font" not found in the CSS; typography is not applied.')
            else:
                applied.append(f'--font ({", ".join(fonts[:2])})')
        open(a.in_, 'w', encoding='utf-8').write(src)
        print((f'Applied to {a.in_}: ' + ' and '.join(applied)) if applied else 'Nothing to apply.')


if __name__ == '__main__':
    main()
