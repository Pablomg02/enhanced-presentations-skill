#!/usr/bin/env python3
"""Embed the formula fonts ("EP Math" and "EP Sym") into an HTML presentation.

  fonts.py topic.html        → fills <style id="fonts">…</style> (new.py already does it)
  fonts.py --generate        → rebuilds fonts/*.woff2 from the system STIX Two
                               (only if another symbol is needed; requires fonttools and brotli)

The fonts are trimmed STIX Two (Latin, Greek, ṁ ẋ… and math symbols). Without
them the formulas are shown with the system serif font, but they do not break.
"""
import base64, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, 'fonts')
FONTS = [  # (file, family, style, origin in the system, characters)
    ('ep-math.woff2', 'EP Math', 'normal', 'STIXTwoText-Regular.otf', 'text'),
    ('ep-math-i.woff2', 'EP Math', 'italic', 'STIXTwoText-Italic.otf', 'text'),
    ('ep-sym.woff2', 'EP Sym', 'normal', 'STIXTwoMath-Regular.otf', 'symbols'),
]
TEXT = ('U+0020-007E,U+00A0-00FF,U+0304,U+0307,U+0370-03FF,U+1E40-1E41,U+1E44-1E45,'
        'U+1E86-1E87,U+1E8A-1E8B,U+2009,U+2013-2014,U+2022,U+2026,U+202F,U+2032-2033,U+2212')
SYMBOLS = '←↑→↓↔↦⇐⇒⇔∀∂∃∆∇∈∉∏∑∓∗∘∙√∝∞∠∥∫∮∼≃≅≈≠≡≤≥≪≫⊂⊥⋅⟨⟩ℓ'


def generate():
    from fontTools import subset
    base = next((d for d in ['/usr/share/fonts/opentype/stix', '/usr/share/fonts/truetype/stix']
                 if os.path.isdir(d)), None)
    if not base: sys.exit('STIX Two not found in /usr/share/fonts (fonts-stix package)')
    os.makedirs(DIR, exist_ok=True)
    for filename, _, _, origin, kind in FONTS:
        src = os.path.join(base, origin if 'opentype' in base else origin.replace('.otf', '.ttf'))
        uni = TEXT if kind == 'text' else ','.join(f'U+{ord(c):04X}' for c in SYMBOLS)
        subset.main([src, f'--unicodes={uni}', '--flavor=woff2', '--layout-features=*',
                     '--no-hinting', '--desubroutinize', f'--output-file={os.path.join(DIR, filename)}'])
        print(filename, os.path.getsize(os.path.join(DIR, filename)) // 1024, 'KB')


def block():
    rules = []
    for filename, family, style, _, _ in FONTS:
        b64 = base64.b64encode(open(os.path.join(DIR, filename), 'rb').read()).decode()
        rules.append(f'@font-face {{ font-family: "{family}"; font-style: {style}; '
                     f'src: url(data:font/woff2;base64,{b64}) format("woff2"); }}')
    return ('<style id="fonts">/* Formula fonts (trimmed STIX Two). '
            'Provided by tools/fonts.py: do not edit. */\n' + '\n'.join(rules) + '\n</style>')


if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit(__doc__)
    if sys.argv[1] == '--generate': generate(); sys.exit()
    html = sys.argv[1]
    src = open(html, encoding='utf-8').read()
    new_style = block()
    m = re.search(r'<style id="fonts">.*?</style>', src, re.S)
    if m: src = src[:m.start()] + new_style + src[m.end():]
    elif '</body>' in src: src = src.replace('</body>', new_style + '\n</body>', 1)
    else: sys.exit('No <style id="fonts"> or </body> found in ' + html)
    open(html, 'w', encoding='utf-8').write(src)
    print('Fonts embedded in', html)
