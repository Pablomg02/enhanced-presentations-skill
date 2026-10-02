#!/usr/bin/env python3
"""Create a new presentation from template.html, ready to fill in.

  Subject or class (from a PPTX, a PDF or a text):
    new.py presentation.html --title "Chemical reactions" --brand "Chemistry" \\
        --block "Block 2 · Kinetics" --source "topic_2.3.pptx" \\
        --parts "Introduction|Rate|Catalysis"

  Project or document (assignment, rubric, guide):
    new.py report.html --title "Project X" --brand "Guided project" \\
        --source "Assignment and rubric" --parts "The project|What to do|Assessment|Dates" \\
        --no-formulas

It leaves the cover with the data, the frame, the engine and the formula fonts; without
example scenes (they are added with component.py) and with ORDER = ['cover'].
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import fonts  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('output')
ap.add_argument('--title', required=True, help='full title, e.g. "Chemical reactions"')
ap.add_argument('--short', help='short title for the header (default: the title)')
ap.add_argument('--brand', default='Presentation', help='footer and cover brand: subject, organization or "Guided project"')
ap.add_argument('--block', default='', help='green cover line, e.g. "Block 2 · Kinetics"')
ap.add_argument('--source', default='', help='source of truth: name of the .pptx/.pdf or description of the text')
ap.add_argument('--parts', default='', help='cover parts separated by |')
ap.add_argument('--no-formulas', action='store_true', help='remove the "Green box" sentence from the help (documents with no formulas)')
ap.add_argument('--force', action='store_true', help='overwrite if it already exists')
a = ap.parse_args()
if os.path.exists(a.output) and not a.force: sys.exit(f'{a.output} already exists (use --force to overwrite)')

src = open(os.path.join(HERE, '..', 'template.html'), encoding='utf-8').read()
short = a.short or a.title
brand = a.brand


def replace_once(old, new, count=1):
    global src
    if old not in src: sys.exit('The template has changed: cannot find ' + old[:60])
    src = src.replace(old, new, count)


def replace_re(pattern, new):
    global src
    src, n = re.subn(pattern, lambda m: new, src, count=1, flags=re.S)
    if not n: sys.exit('The template has changed: cannot find ' + pattern[:60])


source = a.source or 'the given content'
replace_once('<title>Presentation title</title>', f'<title>{a.title}</title>')
replace_re(r'  Animated HTML presentation · Short title\n.*?review this file\.\n',
           f'  Animated HTML presentation · {short}\n'
           f'  Visual aid for a class or talk. The source of truth is: {source}.\n'
           '  If it changes, review this file.\n')
replace_once('<div id="kicker">Short title<span id="sec"></span></div>', f'<div id="kicker">{short}<span id="sec"></span></div>')
replace_once('<div class="cv-k">Block or context</div>', f'<div class="cv-k">{a.block}</div>')
replace_once('<h1>Presentation title</h1>', f'<h1>{a.title}</h1>')
replace_once('<div class="cv-t">Brand or subject</div>', f'<div class="cv-t">{brand}</div>')
replace_once('<span id="brand">Brand or subject</span>', f'<span id="brand">{brand}</span>')
parts = [p.strip() for p in a.parts.split('|') if p.strip()]
replace_re(r'<ol class="cv-ag">.*?</ol>', '<ol class="cv-ag">\n' +
           ''.join(f'        <li><span>{i}</span>{p}</li>\n' for i, p in enumerate(parts, 1)) + '      </ol>')
if a.no_formulas:
    replace_once('<!-- delete this sentence if there are no formulas: --><b style="color:var(--acc-d)">Green box</b>: '
                 'formula as it appears in the source; the rest are intermediate steps showing where it comes from.', '')
# remove the example scenes
ini = src.index('  <!-- ============================================================\n       COMPONENT "')
fin = src.index('  <!-- Bottom frame -->')
src = src[:ini] + ('  <!-- ============================================================\n'
                   '       SCENES: add here, in the same order as ORDER. To copy a component:\n'
                   '       python3 EP/tools/component.py <name>\n'
                   '       ============================================================ -->\n\n') + src[fin:]
replace_re(r'const ORDER = \[\n.*?\n\];', "const ORDER = [\n  'cover',\n];")
replace_re(r'  /\* Slide 9: accumulated capital \(template example\) \*/\n.*?\n  \}\);\n\n', '')
src = re.sub(r'<style id="fonts">.*?</style>', lambda m: fonts.block(), src, count=1, flags=re.S)

os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
open(a.output, 'w', encoding='utf-8').write(src)
print('Created', a.output)
print('Next: add scenes with component.py, put them in ORDER and run review.py')
