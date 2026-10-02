#!/usr/bin/env python3
"""Template components: list them, view their code or insert them into a presentation.

  component.py                      → list of components and what each one is for
  component.py diagram              → HTML of the example scene (and the JS it needs)
  component.py derivation --in topic.html --id derivation-x [--after cover] \\
      [--section "Index section"] [--ref "Slide 5"]
                                     → inserts it into topic.html (after the --after scene, or at
                                       the end), with its id, data-section and data-ref, and adds it
                                       to ORDER in the same place. With "chart" it also inserts
                                       its chart() call in the FIGURES block.

The code comes from template.html (the single source). After inserting: replace the
text with the source text, run review.py --scene <id> and look at the screenshots.
Guide for each component: reference/components.md.
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '..', 'template.html'), encoding='utf-8').read()
BLOCKS = re.findall(r'(  <!-- =+\n       COMPONENT "([\w-]+)":(.*?)=+ -->\n)(  <section.*?\n  </section>\n)', src, re.S)
comps = {n: (com, desc, sec) for com, n, desc, sec in BLOCKS}
JS_CHART = re.search(r'  /\* Slide 9: accumulated capital.*?\n  \}\);\n', src, re.S).group(0)
JS_CAMERA = re.search(r'const CAMERA = \[.*?\n\];', src, re.S).group(0)

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('name', nargs='?')
ap.add_argument('--in', dest='in_', metavar='TOPIC.html', help='insert into this presentation')
ap.add_argument('--id', help='id of the new scene (short, no spaces)')
ap.add_argument('--after', metavar='ID', help='insert after this scene (default: at the end)')
ap.add_argument('--section', help='data-section (name in the index)')
ap.add_argument('--ref', help='data-ref, e.g. "Slide 5" or "Slides 5–7"')
a = ap.parse_args()

if not a.name:
    print('Components (component.py <name> to see the code; --in topic.html --id x to insert it):')
    for n, (_, desc, _) in comps.items():
        ls = [l.strip() for l in desc.split('\n')]
        k = next((k for k, l in enumerate(ls) if l.startswith('For: ')), None)
        for_text = ls[k][5:] if k is not None else ''
        while for_text and not for_text.endswith('.') and k + 1 < len(ls) and ls[k + 1]: k += 1; for_text += ' ' + ls[k]
        one = ' '.join(desc.split('\n')[0].split())
        print(f'  {n:13s} {one}' + (f'\n  {"":13s} For: {for_text}' if for_text else ''))
    sys.exit()
n = a.name
if n not in comps: sys.exit(f'There is no "{n}". Available: ' + ', '.join(comps))
com, desc, sec = comps[n]
old_id = re.search(r'id="([^"]+)"', sec).group(1)

if not a.in_:
    print(com + sec, end='')
    if n == 'chart':
        print('\n/* ---- JS: in the FIGURES block, under "FIGURES FOR THIS PRESENTATION" ---- */\n' + JS_CHART)
    if n == 'camera':
        print('\n/* ---- JS: in block 3, replace const CAMERA with the states of this scene ---- */\n' + JS_CAMERA)
    print(f"\n/* ---- Add to ORDER: '{old_id}' (with the new id) ---- */")
    sys.exit()

# ---------------- insert into a presentation ----------------
if not a.id or not re.fullmatch(r'[\w-]+', a.id): sys.exit('Missing --id (short, no spaces)')
if n == 'question' and not a.id.startswith('q-'): sys.exit('The id of a question must start with "q-" (e.g. --id q-altitude): review.py relies on it')
doc = open(a.in_, encoding='utf-8').read()
if re.search(rf'\bid="{re.escape(a.id)}"', doc): sys.exit(f'An element with id="{a.id}" already exists in {a.in_}')
inner_ids = set(re.findall(r'id="([^"]+)"', sec)) - {old_id}
if a.id in inner_ids: sys.exit(f'--id "{a.id}" collides with an internal id of the "{n}" component: ' + ', '.join(sorted(inner_ids)))

scene_html = sec.replace(f'id="{old_id}"', f'id="{a.id}"', 1)
open_tag = re.match(r'  <section\b(?:[^>"]|"[^"]*")*>', scene_html).group(0)
inherited = ''
if a.section is None and a.after:  # no --section: that of the previous scene (same index section)
    m = re.search(rf'<section\b(?:[^>"]|"[^"]*")*\bid="{re.escape(a.after)}"(?:[^>"]|"[^"]*")*>', doc)
    prev_section = m and re.search(r'data-section="([^"]*)"', m.group(0))
    if prev_section: a.section = inherited = prev_section.group(1)
pending = [re.search(x + r'="[^"]*"', open_tag).group(0) for x, v in (('data-section', a.section), ('data-ref', a.ref))
           if v is None and f'{x}="' in open_tag] + (['data-acronyms (example acronyms)'] if 'data-acronyms="' in open_tag else [])
new_tag = open_tag
for attr, val in (('data-section', a.section), ('data-ref', a.ref)):
    if val is None: continue
    val = val.replace('"', '&quot;')
    new_tag = re.sub(rf'{attr}="[^"]*"', lambda m: f'{attr}="{val}"', new_tag) if f'{attr}="' in new_tag else new_tag[:-1] + f' {attr}="{val}">'
refs_removed = 'data-refs="' in new_tag
if refs_removed: new_tag = re.sub(r'\s+data-refs="[^"]*"', '', new_tag)
scene_html = scene_html.replace(open_tag, new_tag, 1)
if n == 'chart': scene_html = scene_html.replace('id="g-example"', f'id="g-{a.id}"')

if a.after:
    m = re.search(rf'<section\b(?:[^>"]|"[^"]*")*\bid="{re.escape(a.after)}"', doc)
    if not m: sys.exit(f'Scene "{a.after}" not found in {a.in_}')
    end = doc.index('</section>\n', m.end()) + len('</section>\n')
    doc = doc[:end] + '\n' + scene_html + doc[end:]
else:
    i = doc.index('  <!-- Bottom frame -->')
    doc = doc[:i] + scene_html + '\n' + doc[i:]

m = re.search(r'const ORDER = \[\n(.*?)\n\];', doc, re.S)
if not m: sys.exit('"const ORDER = [ … ];" not found')
lines = m.group(1).split('\n')
pos = len(lines)
while pos and lines[pos - 1].strip().startswith('//'): pos -= 1  # before the trailing comments
if a.after:
    for j, l in enumerate(lines):
        if re.search(rf"""['"]{re.escape(a.after)}['"]""", re.sub(r'//.*', '', l)): pos = j + 1
lines.insert(pos, f"  '{a.id}',")
doc = doc[:m.start(1)] + '\n'.join(lines) + doc[m.end(1):]

warning = ''
if n == 'chart':
    js = JS_CHART.replace("'#g-example'", f"'#g-{a.id}'").replace('(template example)', f'(scene {a.id})')
    k = doc.find('FIGURES FOR THIS PRESENTATION')
    k = doc.find('*/\n', k) + 3 if k >= 0 else -1
    if k > 2: doc = doc[:k] + '\n' + js + doc[k:]
    else: warning = '\n"FIGURES FOR THIS PRESENTATION" not found: add the chart() call by hand (component.py chart).'
if n == 'camera':
    warning = '\nMissing JS: replace const CAMERA (block 3) with the states of this scene (component.py camera).'

open(a.in_, 'w', encoding='utf-8').write(doc)
print(f'Inserted "{n}" as id="{a.id}"' + (f' after "{a.after}"' if a.after else ' at the end') + ' (also in ORDER).' + warning)
if inherited: print(f'data-section="{inherited}" (that of "{a.after}"; another one: --section "…")')
if refs_removed: print('NOTE: data-refs removed from the inserted scene (the footer falls back to data-ref); if its steps come from different places, fill in data-refs by hand.')
if pending: print('NOTE: the template values remain in ' + ', '.join(pending) + ': change them')
print(f'Next: replace the text with the source text and run review.py {a.in_} --scene {a.id}')
