#!/usr/bin/env python3
"""Automatic review of an HTML presentation. Run it after every new scene.

  review.py pres.html [--pages N] [--strict] [--scene id[,id…]] [--screenshots DIR] [--no-style]

1. File (no browser): ORDER and scenes, duplicate ids, data-section / data-ref,
   images, fonts, unchanged template text, classes with no style and, with
   --pages N, slides or pages of the source that no scene cites
   (--slides is an alias).
2. Style (no browser): first person and colloquialisms, "slide" in the text, titles
   "from X to Y" or with arrows, em dash (—), decimal comma, number and unit without &nbsp;,
   examples without class="pr", long derivations without "Objective".
3. Browser (headless Chrome): walks through ALL the steps and on each one looks for JavaScript
   errors, malformed formulas, texts that go outside the canvas, step on the frame or
   the closing line (.punch), texts that overlap (also with the acronyms at the top
   right), text that goes outside its box (card, box, cell…), SVG labels
   crossed by a line, text that is too small, steps that change nothing and steps with
   too much text. It flags the acronyms of each scene that its data-acronyms does not explain.
   It also tests keyboard navigation and the index.
4. Scene → steps map (for screenshots.sh).

--scene id,id2: the browser only reviews those scenes (faster, shorter output).
--screenshots DIR:  also takes screenshots of the reviewed steps (with --scene) into DIR.

✗ = error (must be fixed) · ! = warning (check it in the screenshot and decide).
It ends with "OK" (code 0) or "PROBLEMS FOUND" (code 1). With --strict, warnings
also count as a problem.
A deliberate overlap is accepted by adding data-overlap to the element.
"""
import argparse, html, json, os, re, shutil, subprocess, sys, tempfile
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_TEXT = ['Presentation title', 'Short title', 'Block or context', 'Brand or subject',
                 'Title that says what is done', 'First point, as it is in the source',
                 'Brief subtitle (from the source)', 'Brief source note about this component',
                 'Closing line with the', 'Criterion 1',
                 'Advantage of A', 'Type 1', 'Brief definition, from the source', 'Element A', 'Branch A',
                 'Idea 1 from the source',
                 'First part', 'Source sentence about', 'What is done in this phase', 'Aspect 1',
                 'Date or data with supporting text', 'A sentence that presents the data',
                 'Obtain the sum of the first n terms', 'is deposited at a compound interest of',
                 'Expressions derived next, with their application']


class Html(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.els, self.stack, self.body = [], [], False
        self.script = self.style = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'body': self.body = True
        if tag == 'script': self.script = True
        if tag == 'style': self.style = True
        if self.body and not self.script:
            self.els.append((tag, a, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag == 'script': self.script = False
        if tag == 'style': self.style = False


def ranges(nums):
    nums = sorted(set(nums)); out = []; i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
        out.append(f'#{nums[i]}' if i == j else f'#{nums[i]}–{nums[j]}'); i = j + 1
    return ', '.join(out)


def cited_pages(refs):
    s = set()
    for r in refs:
        for chunk in re.split(r'[·|]', r):
            m = re.search(r'(?:slides?|pages?)\b\.?|\bp{1,2}\.', chunk, re.I)
            if not m: continue
            t = chunk[m.end():]
            for a, b in re.findall(r'(\d+)\s*[–-]\s*(\d+)', t): s.update(range(int(a), int(b) + 1))
            t = re.sub(r'(\d+)\s*[–-]\s*(\d+)', ' ', t)
            s.update(int(x) for x in re.findall(r'\d+', t))
    return s


def static_check(src, pages):
    errors, warnings = [], []
    p = Html(); p.feed(src)
    scenes = [(a.get('id'), a, ln) for t, a, ln in p.els if t == 'section' and 'scene' in (a.get('class') or '').split()]
    ids = [a.get('id') for t, a, ln in p.els if a.get('id')]
    for i in sorted(set(x for x in ids if ids.count(x) > 1)): errors.append(f'duplicate id: "{i}"')
    m = re.search(r'const ORDER = \[(.*?)\n\];', src, re.S)
    order = []
    if not m: errors.append('"const ORDER = [ … ];" not found')
    else:
        body = re.sub(r'//[^\n]*', '', m.group(1))
        order = re.findall(r"""['"]([\w-]+)['"]""", body)
        for o in order:
            if o not in [e[0] for e in scenes]: errors.append(f'ORDER cites "{o}", but there is no <section class="scene" id="{o}">')
    for sid, a, ln in scenes:
        if not sid: errors.append(f'scene without id (line {ln})'); continue
        if sid not in order: warnings.append(f'scene "{sid}" (line {ln}) is not in ORDER: it will not be shown')
        if sid == 'cover': continue
        if not a.get('data-section'): warnings.append(f'scene "{sid}" without data-section (name in the index)')
        if not a.get('data-ref') and not a.get('data-refs'): warnings.append(f'scene "{sid}" without data-ref (where it comes from)')
        if sid.startswith('q-') and ('qs' not in a.get('class', '').split() or 'Class question' not in a.get('data-ref', '')):
            warnings.append(f'question "{sid}": it must have class="scene qs" and data-ref="Class question · not from the source"')
    mi = re.search(r'^const IMG = (\{.*\});$', src, re.M)
    imgs = {}
    if not mi: errors.append('The line "const IMG = {…};" is not alone on its line (images.py will not be able to edit it)')
    else:
        try: imgs = json.loads(mi.group(1))
        except Exception: errors.append('The line "const IMG = {…};" is not valid JSON')
    for t, a, ln in p.els:
        if t == 'img' and 'data-img' in a and a['data-img'] not in imgs:
            (warnings if a['data-img'] == '' else errors).append(
                f'line {ln}: <img data-img="{a["data-img"]}"> does not exist in IMG (images.py … put {a["data-img"] or "name"} photo)')
        for k in ('data-in', 'data-out', 'data-go'):
            if k in a and not re.fullmatch(r'\d+', a[k] or ''):
                errors.append(f'line {ln}: {k}="{a[k] or ""}" is not a step number')
        if 'data-hl' in a and not all(re.fullmatch(r'\d+(?:-\d+)?', x.strip()) for x in (a['data-hl'] or '').split(',')):
            errors.append(f'line {ln}: data-hl="{a["data-hl"] or ""}" is not a list of steps or ranges (e.g. 2, 2-4, 1,3-4)')
    uses_tex = any('data-tex' in a for _, a, _ in p.els)
    if uses_tex and not re.search(r'@font-face\s*\{\s*font-family:\s*"EP Math"', src):
        warnings.append('There are formulas but the fonts are missing: tools/fonts.py ' + '<file>')
    if not uses_tex and 'Green box</b>' in src:
        warnings.append('The help (#help) mentions the "Green box" but there are no formulas: delete that sentence')
    body = src[src.find('<body'):]
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    for t in TEMPLATE_TEXT:
        if t in body: warnings.append(f'template text remains: "{t}"')
    # classes used without a style or JS use (typos)
    css = ' '.join(re.findall(r'<style[^>]*>(.*?)</style>', src, re.S))
    js = ' '.join(re.findall(r'<script[^>]*>(.*?)</script>', src, re.S))
    defined = set(re.findall(r'\.(-?[_a-zA-Z][\w-]*)', css)) | set(re.findall(r'[\w-]+', js))
    used = {}
    for t, a, ln in p.els:
        for c in (a.get('class') or '').split(): used.setdefault(c, ln)
    for c, ln in used.items():
        if c not in defined and c != 'qs': warnings.append(f'class "{c}" (line {ln}) has no style in the CSS: typo?')
    if pages:
        refs = [a.get('data-ref', '') + '|' + a.get('data-refs', '') for _, a, _ in scenes]
        cited = cited_pages(refs)
        missing = [n for n in range(2, pages + 1) if n not in cited]
        if missing: warnings.append('slides or pages not cited by any scene (is content missing or are they decorative?): ' +
                                    ', '.join(map(str, missing)))
    return errors, warnings, [e[0] for e in scenes if e[0]]


# uppercase words that are not acronyms to explain (units, molecules, the document itself)
NO_ACRONYMS = {'MN', 'GN', 'MW', 'GW', 'MJ', 'GJ', 'MPa', 'GPa', 'PPT', 'PDF', 'CO', 'OK', 'HTML'}


class Text(HTMLParser):
    """Visible text of an HTML fragment (without <script>/<style>; attributes do not count)."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.t = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        elif tag in ('br', 'li', 'p', 'div', 'td', 'th', 'h2', 'text'): self.t.append(' ')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
    def handle_data(self, d):
        if not self.skip: self.t.append(d)


def text(h):
    p = Text(); p.feed(h); return re.sub(r'[ \t\r\n]+', ' ', ''.join(p.t)).strip()


FIRST_PERSON = [r'we', r'us', r'our', r'ours', r'my', r'mine', r'(?-i:\bI\b)',
                r"let's", r"we're", r"we'll", r"we've", r"we'd",
                r"don't", r"can't", r"won't", r"doesn't", r"didn't", r"isn't", r"aren't",
                r"it's", r"that's", r'note that', r'remember that', r'keep in mind',
                r'as we know', r'does not matter', r'goes away', r'comes out',
                r'what .{0,20} about', r'why .{0,20} matters']
UNITS = (r'MN|kN|GN|N|kPa|MPa|GPa|Pa|bar|atm|K|°C|°R|km/s|m/s|km|m|kg|g|t|s|min|h|MW|kW|GW|W|MJ|kJ|J|eV|'
         r'psia|psi|ft|lbf|lb|%')


def style_check(src):
    """Style warnings per scene: [(id, message)]."""
    out = []
    scenes = [(a, c) for a, c in re.findall(r'<section\b((?:[^>"]|"[^"]*")*)>(.*?)</section>', src, re.S)
              if re.search(r'\bclass="scene\b', a)]
    m = re.search(r'const ORDER = \[(.*?)\n\];', src, re.S)
    order = re.findall(r"""['"]([\w-]+)['"]""", re.sub(r'//[^\n]*', '', m.group(1))) if m else []
    goal = {}
    for attrs, body in scenes:
        sid = (re.search(r'\bid="([^"]+)"', attrs) or [None, ''])[1]
        goal[sid] = 'class="goal' in body
    for attrs, body in scenes:
        sid = (re.search(r'\bid="([^"]+)"', attrs) or [None, ''])[1]
        if sid == 'cover': continue
        cls = (re.search(r'\bclass="([^"]*)"', attrs) or [None, ''])[1].split()
        t = text(body)
        h2 = text((re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S) or [None, ''])[1])
        subs = [text(x) for x in re.findall(r'<div class="sub[^"]*"[^>]*>(.*?)</div>', body, re.S)]
        q = []
        for pat in FIRST_PERSON:
            mm = re.search(r'(?<![\w-])' + pat + r'(?![\w-])', t, re.I)
            if mm: q.append(f'first person or colloquial: "{mm.group(0)}" (use an impersonal form: "T is solved for", "the result is obtained")')
        mm = re.search(r'\b(?:slides?|pages?|p\.)[^.;:]{0,20}', t, re.I)
        if mm: q.append(f'cites a slide or page in the text ("{mm.group(0).strip()}"): only in data-ref, at the bottom right')
        for title in [h2] + subs:
            if '→' in title or '->' in title or re.match(r'\s*from\s.+\s(to|into)\s', title, re.I):
                q.append(f'title or subtitle "from X to Y" or with arrows: "{title[:60]}" (say with words what is done)')
        if '—' in t: q.append('em dash (—) as punctuation: use a comma, colon or parentheses')
        mm = re.search(r'(?<![\w.,])\d+,(?!\d{3}(?!\d))\d+(?!\d)', t)
        if mm: q.append(f'decimal comma: "{mm.group(0)}" (decimal point)')
        mm = re.search(r'\d (' + UNITS + r')(?![\w/])', t)
        if mm: q.append(f'number and unit with a normal space: "{mm.group(0)}" (use &nbsp;)')
        if re.match(r'(Example|Exercise|Approach|Solution)\b', h2) and 'pr' not in cls:
            q.append('practice without class="scene pr" (examples are in blue)')
        if re.match(r'Application\s*:', h2): q.append('title "Application: …" in an example: use "Example: …"')
        if body.count('class="rw') >= 3 and 'sub obj' not in body and not goal.get(sid) and 'pr' not in cls:
            i = order.index(sid) if sid in order else -1
            if not (i > 0 and goal.get(order[i - 1])):
                q.append('derivation without "Objective" (<div class="sub obj">) or an "objective" scene before')
        out += [(sid, x) for x in q]
    return out


PROBE = r'''<script>
addEventListener('load', async () => {
  const out = { errors: window.__errors, steps: [], n: 0, nav: '', index: 0, indexScenes: 0, js: [], acronyms: {} };
  const ONLY = window.__only || null;
  const finish = () => { const s = document.createElement('script'); s.type = 'application/json'; s.id = '__probe';
    s.textContent = JSON.stringify(out).replace(/</g, '\\u003c'); document.body.appendChild(s); };
  try {
    await document.fonts.ready; await new Promise(r => setTimeout(r, 150));
    const key = k => dispatchEvent(new KeyboardEvent('keydown', { key: k }));
    const cnt = () => document.querySelector('#count').textContent.split(' / ').map(Number);
    let P = window.PRES;
    if (!P) {  /* legacy engine (no window.PRES): walk through with the keyboard */
      out.legacy = true; key('Home'); const n = cnt()[1], steps = [];
      if (!n) { out.errors.push('The engine did not start (no step counter)'); finish(); return; }
      for (let j = 0, prev = null, k = 0; j < n; j++) { const id = document.querySelector('.scene.active').id;
        k = id === prev ? k + 1 : 0; prev = id; steps.push(id + ':' + k); key('ArrowRight'); }
      key('Home');
      P = { steps, js: [], go: i => { if (i === 0) key('Home'); else key('ArrowRight'); } };
    }
    const stage = document.getElementById('stage'), N = P.steps.length; out.n = N; out.js = P.js || [];
    document.querySelectorAll('.m').forEach(m => { if (m.textContent.startsWith('⚠')) out.errors.push('Malformed formula: ' + m.textContent.slice(2) + ' · data-tex="' + (m.dataset.tex || '').slice(0, 80) + '"'); });
    const sr = stage.getBoundingClientRect(), sc = sr.width / 1600;
    const R = r => ({ x: (r.left - sr.left) / sc, y: (r.top - sr.top) / sc, w: r.width / sc, h: r.height / sc });
    const inter = (a, b) => { const x = Math.max(a.x, b.x), y = Math.max(a.y, b.y);
      const w = Math.min(a.x + a.w, b.x + b.w) - x, h = Math.min(a.y + a.h, b.y + b.h) - y; return w > 0 && h > 0 ? { x, y, w, h } : null; };
    const area = rs => rs.reduce((s, r) => s + r.w * r.h, 0);
    const visible = el => { for (let e = el; e && e !== stage; e = e.parentElement) { const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.1) return false; } return true; };
    /* clip of ancestors with overflow other than visible (e.g. the camera <svg>) */
    const clip = el => { let c = null; for (let e = el.parentElement; e && e !== stage; e = e.parentElement) {
      const cs = getComputedStyle(e); if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') {
        const r = R(e.getBoundingClientRect()); c = c ? inter(c, r) || { x: 0, y: 0, w: 0, h: 0 } : r; } } return c; };
    const shorten = t => { t = t.replace(/\s+/g, ' ').trim(); return t.length > 38 ? t.slice(0, 36) + '…' : t; };
    function units(scene) {
      const U = [];
      for (const e of scene.querySelectorAll('*')) {
        if (e.closest('.qs-bg')) continue;
        if (e.closest('.m') && !e.classList.contains('m')) continue;
        const tag = e.tagName.toLowerCase();
        if (tag === 'tspan' || tag === 'script' || tag === 'style') continue;
        let rs = [], t = '', fs = 0, img = false, rotated = false;
        if (e.classList.contains('m') || tag === 'text') {
          rs = [R(e.getBoundingClientRect())]; t = e.textContent;
          const M = tag === 'text' ? (e.getScreenCTM() || { a: sc, b: 0 }) : { a: sc, b: 0 };
          rotated = Math.abs(M.b) > 0.01 * Math.abs(M.a || 1);
          fs = parseFloat(getComputedStyle(e).fontSize) * Math.hypot(M.a, M.b) / sc;
        } else if (tag === 'img') {
          if (!e.getAttribute('src')) continue; rs = [R(e.getBoundingClientRect())]; t = '[image ' + (e.dataset.img || '') + ']'; img = true;
        } else if (!(e instanceof SVGElement)) {
          const tn = [...e.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim());
          if (!tn.length) continue;
          for (const n of tn) { const rg = document.createRange(); rg.selectNodeContents(n);
            for (const q of rg.getClientRects()) if (q.width >= 1 && q.height >= 1) rs.push(R(q)); }
          t = tn.map(n => n.textContent).join(' ');
          fs = e.closest('sub,sup') ? 99 : parseFloat(getComputedStyle(e).fontSize);
        } else continue;
        rs = rs.filter(r => r.w >= 1 && r.h >= 1);
        if (!rs.length || !visible(e)) continue;
        const c = clip(e); let clipped = false;
        if (c) { const a0 = area(rs); rs = rs.map(r => inter(r, c)).filter(Boolean);
          if (!rs.length) continue; clipped = area(rs) < 0.97 * a0; }
        const b = { x: Math.min(...rs.map(r => r.x)), y: Math.min(...rs.map(r => r.y)) };
        b.w = Math.max(...rs.map(r => r.x + r.w)) - b.x; b.h = Math.max(...rs.map(r => r.y + r.h)) - b.y;
        U.push({ e, rs, b, t: shorten(t), full: t, fs, img, clipped, ok: rotated || !!e.closest('[data-overlap]') });
      }
      return U;
    }
    /* visible boxes (border or colored background): the text inside must not overflow */
    const opaque = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return false; const v = m[1].split(',').map(parseFloat);
      return (v.length < 4 || v[3] > 0.05) && !(v[0] > 250 && v[1] > 250 && v[2] > 250); };
    /* sides of a box that are visible: all four if it has a background; otherwise those with a border (.punch at the top, .nt on the left) */
    const boxSides = e => { const cs = getComputedStyle(e);
      if (opaque(cs.backgroundColor)) return { Top: 1, Right: 1, Bottom: 1, Left: 1 };
      const l = {}; ['Top', 'Right', 'Bottom', 'Left'].forEach(k => { if (parseFloat(cs['border' + k + 'Width']) > 0 && cs['border' + k + 'Style'] !== 'none' && opaque(cs['border' + k + 'Color'])) l[k] = 1; });
      return Object.keys(l).length ? l : null; };
    function overflows(scene, U) {
      const q = [];
      for (const c of scene.querySelectorAll('*')) {
        if (c instanceof SVGElement || c.closest('.m') || c.closest('.qs-bg') || !visible(c)) continue;
        const L = boxSides(c); if (!L) continue;
        const cr = R(c.getBoundingClientRect()), outside = [];
        for (const u of U) { if (!c.contains(u.e) || u.ok || (u.e === c && u.e.classList.contains('m'))) continue;
          if (u.rs.some(r => (L.Left && r.x < cr.x - 3) || (L.Right && r.x + r.w > cr.x + cr.w + 3) || (L.Top && r.y < cr.y - 3) || (L.Bottom && r.y + r.h > cr.y + cr.h + 3))) outside.push(u); }
        if (outside.length) q.push(['E', 'goes outside its box (' + c.tagName.toLowerCase() + (c.className && typeof c.className === 'string' ? '.' + c.className.trim().split(/\s+/).join('.') : '') + '): "' + outside[0].t + '"' + (outside.length > 1 ? ' and ' + (outside.length - 1) + ' more' : '')]);
      }
      return q;
    }
    /* labels of an SVG crossed by a line (the stroke of each shape is sampled) */
    const light = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return true; const v = m[1].split(',').map(parseFloat);
      return (v.length > 3 && v[3] < 0.2) || (0.299 * v[0] + 0.587 * v[1] + 0.114 * v[2]) > 215; };
    const covers = e => { const cs = getComputedStyle(e), m = cs.fill.match(/rgba?\(([^)]+)\)/);
      return !!m && (m[1].split(',').length < 4 || parseFloat(m[1].split(',')[3]) > 0.5) && +cs.fillOpacity > 0.5 && +cs.opacity > 0.5; };
    function crossings(scene) {
      const q = [];
      const txt = [...scene.querySelectorAll('svg text')].filter(t => visible(t) && !t.closest('[data-overlap]') && t.textContent.trim());
      if (!txt.length) return q;
      const geo = [...scene.querySelectorAll('svg path, svg line, svg polyline, svg polygon, svg rect, svg circle, svg ellipse')].filter(g => {
        if (g.closest('defs, marker, pattern, mask, clipPath, [data-overlap]') || !visible(g)) return false;
        const cs = getComputedStyle(g); return cs.stroke !== 'none' && parseFloat(cs.strokeWidth) > 0 && !light(cs.stroke); });
      for (const t of txt) {
        const r = t.getBoundingClientRect(), C = t.getScreenCTM();
        if (r.width < 2 || (C && Math.abs(C.b) > 0.01 * Math.abs(C.a || 1))) continue;  /* rotated: its box is not usable */
        const b = { l: r.left + 1, r: r.right - 1, t: r.top + 0.3 * r.height, b: r.bottom - 0.25 * r.height };
        for (const g of geo) {
          const gr = g.getBoundingClientRect();
          if (gr.right < b.l || gr.left > b.r || gr.bottom < b.t || gr.top > b.b) continue;
          let L = 0; try { L = g.getTotalLength(); } catch (e) { continue; }
          const M = g.getScreenCTM(); if (!M || !L) continue;
          const step = Math.max(L / 600, 1.5); let n = 0;
          for (let d = 0; d <= L && n < 2; d += step) { const p = g.getPointAtLength(d);
            const x = M.a * p.x + M.c * p.y + M.e, y = M.b * p.x + M.d * p.y + M.f;
            if (!(x > b.l && x < b.r && y > b.t && y < b.b)) continue;
            /* it only counts if the line is visible there: no filled shape (circle, box…) is on top of it */
            const stack = document.elementsFromPoint(x, y), j = stack.indexOf(g);
            if (j < 0 || !stack.slice(0, j).some(e => e !== t && !t.contains(e) && e instanceof SVGGeometryElement && covers(e))) n++; }
          if (n >= 2) { q.push(['A', 'a line in the drawing crosses the label "' + shorten(t.textContent) + '" (move it, or use data-overlap if it is intentional)']); break; }
        }
      }
      return q;
    }
    /* acronym-looking words and subscripts, to check data-acronyms (in Python) */
    function acronyms(scene) {
      const tx = new Set(), sb = new Set(), w = document.createTreeWalker(scene, NodeFilter.SHOW_TEXT);
      for (let n; (n = w.nextNode());) {
        const p = n.parentElement; if (!p || p.closest('script, style, .qs-bg')) continue;
        const t = n.textContent;
        if (p.closest('sub, .sb') || p.getAttribute('baseline-shift') === 'sub' || (p.closest('.ss') && p.closest('.sb'))) { t.split(/[\s,]+/).forEach(x => x && sb.add(x)); continue; }
        if (p.closest('.m, .v, .vr')) { (t.match(/[A-Za-z]{2,}/g) || []).forEach(x => sb.add(x)); continue; }
        /* chemical formula: capitals attached to a numeric subscript (HNO<sub>3</sub>, N<sub>2</sub>O<sub>4</sub>) */
        const chem = (n.nextSibling && n.nextSibling.nodeName === 'SUB' && /^\d/.test(n.nextSibling.textContent)) ||
          (n.previousSibling && n.previousSibling.nodeName === 'SUB' && /^\d/.test(n.previousSibling.textContent));
        (t.match(/(?<![\w-])[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*(?![\w-])/g) || [])
          .filter(x => (x.match(/[A-Z]/g) || []).length >= 2)
          .filter(x => !(chem && (t.trim().endsWith(x) || t.trim().startsWith(x)))).forEach(x => tx.add(x));
      }
      return { tx: [...tx], sb: [...sb], dec: scene.dataset.acronyms || '', all: scene.textContent.replace(/\s+/g, ' ') };
    }
    const signature = s => [...s.querySelectorAll('[data-in],[data-out],[data-go],[data-hl]')]
      .map(e => (e.classList.contains('vis') ? 1 : 0) + '' + (e.classList.contains('go') ? 1 : 0) + (e.classList.contains('on') ? 1 : 0)).join('');
    let prev = null;
    const acronymEl = document.getElementById('acronyms');
    for (let i = 0; i < N; i++) {
      const [id, k] = P.steps[i].split(':');
      if (ONLY && !ONLY.includes(id)) { prev = null; continue; }
      P.go(i);
      const scene = document.getElementById(id), q = [];
      if (!out.acronyms[id]) out.acronyms[id] = acronyms(scene);
      const U = units(scene);
      q.push(...overflows(scene, U), ...crossings(scene));
      const punch = [...scene.querySelectorAll('.punch, .qz-f')].filter(visible).map(e => ({ e, r: R(e.getBoundingClientRect()) }));
      for (const u of U) for (const p of punch) if (!p.e.contains(u.e) && !u.ok && u.b.y + u.b.h > p.r.y + 2 && u.b.y < p.r.y + p.r.h
        && u.b.x < p.r.x + p.r.w && u.b.x + u.b.w > p.r.x) q.push(['E', 'invades the closing-line area (.punch): "' + u.t + '"']);
      if (acronymEl && id !== 'cover') for (const u of units(acronymEl)) { u.frame = true; U.push(u); }
      for (const u of U) {
        if (u.frame) continue;
        const b = u.b, name = '"' + u.t + '"';
        if (b.x < 30 || b.x + b.w > 1570 || b.y < 20 || b.y + b.h > 880) q.push(['E', 'goes outside the canvas: ' + name]);
        else if (id !== 'cover' && b.y + b.h > 852) q.push(['E', 'steps on the footer: ' + name]);
        else if (id !== 'cover' && b.y < 60) q.push(['E', 'steps on the header: ' + name]);
        if (u.clipped) q.push(['E', 'is cut off by the edge of its figure: ' + name]);
        if (!u.img && u.fs && u.fs < 15) q.push(['A', 'small text (' + u.fs.toFixed(0) + ' px): ' + name]);
      }
      for (let a = 0; a < U.length; a++) for (let c = a + 1; c < U.length; c++) {
        const A = U[a], B = U[c];
        if (A.img && B.img) continue;
        if (A.frame && B.frame) continue;
        if (A.ok || B.ok || A.e.contains(B.e) || B.e.contains(A.e) || !inter(A.b, B.b)) continue;
        let ar = 0; for (const ra of A.rs) for (const rb of B.rs) { const x = inter(ra, rb); if (x && x.w > 2 && x.h > 2) ar += x.w * x.h; }
        const ref = A.img ? area(B.rs) : B.img ? area(A.rs) : Math.min(area(A.rs), area(B.rs));
        if (ar > 0.2 * ref && ar > 40) q.push(['E', A.frame || B.frame ? 'steps on the acronyms at the top right (data-acronyms): "' + (A.frame ? B : A).t + '"'
          : '"' + A.t + '" and "' + B.t + '" overlap']);
      }
      const words = U.filter(u => !u.img).reduce((s, u) => s + u.full.split(/\s+/).filter(w => /\w/.test(w)).length, 0);
      if (words > 150) q.push(['A', 'too much text at once (' + words + ' words): split it into steps or scenes']);
      const f = signature(scene);
      if (prev && prev.id === id && f && prev.f === f && !out.js.includes(id)) q.push(['A', 'this step changes nothing from the previous one (extra data-in/out?)']);
      prev = { id, f };
      out.steps.push({ i: i + 1, id, k: +k, q });
    }
    // keyboard navigation and index
    P.go(0);
    for (let j = 0; j < N + 2; j++) key('ArrowRight');
    const [a1, b1] = cnt();
    for (let j = 0; j < N + 2; j++) key('ArrowLeft');
    const [a2] = cnt();
    key('i'); out.index = document.querySelectorAll('#idx li.s').length || document.querySelectorAll('#idx li').length;
    out.indexScenes = document.querySelectorAll('#idx li.s ol .it').length; key('Escape');
    out.nav = (a1 === b1 && b1 === N && a2 === 1) ? 'OK' : `fails: after moving forward ${a1}/${b1}, after going back ${a2}`;
    await new Promise(r => setTimeout(r, 300));
  } catch (e) { out.errors.push('Error during review: ' + e.message); }
  finish();
});
</script>'''


def browser(src, path, only=None):
    src = src.replace('<head>', "<head><script>window.__only=" + json.dumps(only) + ";window.__errors=[];addEventListener('error',e=>__errors.push(e.message+' (line '+e.lineno+')'));"
                      "const __ce=console.error;console.error=(...a)=>{__errors.push(a.map(String).join(' '));__ce(...a);};</script>", 1)
    src = src.replace('</body>', PROBE + '</body>', 1)
    d = tempfile.mkdtemp(); p = os.path.join(d, 'review.html')
    try:
        open(p, 'w', encoding='utf-8').write(src)
        chrome = subprocess.run(['bash', '-c', f'source "{HERE}/_chrome.sh" && echo "$CHROME"'], capture_output=True, text=True).stdout.strip()
        if not chrome: return None, ('Chrome/Chromium not found: the browser review could NOT be run (environment problem, not content). '
                                     'Install Chrome/Chromium or export CHROME (see _chrome.sh). The presentation was NOT reviewed.')
        try:
            r = subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=1600,900',
                                '--virtual-time-budget=120000', '--dump-dom', 'file://' + p + '?static'],
                               capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            return None, 'Chrome did not finish in 5 minutes'
        m = re.search(r'<script type="application/json" id="__probe">(.*?)</script>', r.stdout, re.S)
        if not m: return None, 'Chrome returned no result (does the HTML never finish loading?). ' + r.stderr[-300:]
        return json.loads(m.group(1)), None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description='Automatic review of an HTML presentation')
    ap.add_argument('html'); ap.add_argument('--pages', '--slides', dest='pages', type=int,
                    help='number of slides or pages in the source (--slides is an alias)')
    ap.add_argument('--strict', action='store_true', help='warnings also count as a problem')
    ap.add_argument('--scene', help='only these scenes in the browser (ids separated by commas)')
    ap.add_argument('--screenshots', metavar='DIR', help='screenshots of the reviewed steps (with --scene)')
    ap.add_argument('--no-style', action='store_true', help='do not review the text style')
    a = ap.parse_args()
    only = [x.strip() for x in a.scene.split(',')] if a.scene else None
    src = open(a.html, encoding='utf-8').read()
    print('Review of', os.path.basename(a.html))
    errors, warnings, scene_ids = static_check(src, a.pages)
    unknown = [i for i in (only or []) if i not in scene_ids]
    if unknown:
        errors.append(f'--scene: unknown scene id(s): {", ".join(unknown)} · available: {", ".join(scene_ids)}')
    print('File:', 'no issues' if not errors and not warnings else '')
    for e in errors: print('  ✗', e)
    for e in warnings: print('  !', e)
    n_errors, n_warnings = len(errors), len(warnings)
    if not a.no_style:
        style_warnings = [(i, m) for i, m in style_check(src) if not only or i in only]
        print('Style:', 'no warnings' if not style_warnings else '')
        for i, m in style_warnings: print(f'  ! ({i}) {m}')
        n_warnings += len(style_warnings)
    result, failure = (None, None) if unknown else browser(src, a.html, only)
    if unknown:
        print('Browser: not run (--scene ids do not exist, fix them first)')
    elif failure:
        print('Browser:', failure)
        n_errors += 1
    else:
        if result.get('legacy'): print('(legacy engine, without window.PRES: keyboard walkthrough; "step with no changes" is not checked in scenes with their own JS)')
        print(f'Browser: {result["n"]} steps · index with {result["index"]} sections' +
              (f' and {result["indexScenes"]} scenes' if result.get('indexScenes') else '') + f' · navigation {result["nav"]}')
        if result['nav'] != 'OK': n_errors += 1
        for e in dict.fromkeys(result['errors']): print('  ✗ JavaScript:', e); n_errors += 1
        groups = {}
        for p in result['steps']:
            for t, msg in p['q']: groups.setdefault((p['id'], t, msg), []).append(p['i'])
        for (sid, t, msg), steps in groups.items():
            print(f'  {"✗" if t == "E" else "!"} {ranges(steps)} ({sid}): {msg}')
            if t == 'E': n_errors += 1
            else: n_warnings += 1
        for sid, d in result.get('acronyms', {}).items():
            if sid == 'cover' or sid.startswith('q-'): continue
            bs = re.findall(r'<b>(.*?)</b>', html.unescape(d['dec']))
            dec = {re.sub(r'<[^>]+>', '', b) for b in bs} | {re.sub(r'<[^>]+>', '', re.sub(r'<sub>.*?</sub>', '', b)) for b in bs}
            word = lambda t: re.search(r'(?<![A-Za-z])' + re.escape(t) + r'(?![A-Za-z])', d['all'])
            missing = [t for t in d['tx'] if t not in dec and t not in NO_ACRONYMS and not re.fullmatch(r'[IVXLC]+', t)
                       and f'({t})' not in d['all']]
            extra = sorted(t for t in {re.sub(r'<[^>]+>', '', b) for b in bs}
                           if not word(t) and t not in d['sb'] and re.sub(r'\d+$', '', t) not in d['tx'])
            if missing:
                print(f'  ! ({sid}) acronyms not explained by data-acronyms: {", ".join(missing)} (if they are proper names or units, ignore)')
                n_warnings += 1
            for t in extra: print(f'  ! ({sid}) data-acronyms explains "{t}", which does not appear in the scene'); n_warnings += 1
        step_map, prev = [], None
        for p in result['steps']:
            if prev and prev[0] == p['id'] and prev[2] == p['i'] - 1: prev[2] = p['i']
            else: prev = [p['id'], p['i'], p['i']]; step_map.append(prev)
        print('Step map (for screenshots.sh):')
        print('  ' + ' · '.join(f'{m[0]} {m[1]}' + (f'-{m[2]}' if m[2] > m[1] else '') for m in step_map))
    if a.screenshots and not unknown and not failure:
        steps = [str(p['i']) for p in result['steps'] if not only or p['id'] in only]
        if steps:
            r = subprocess.run(['bash', os.path.join(HERE, 'screenshots.sh'), a.html, *steps], env={**os.environ, 'OUT': a.screenshots})
            if r.returncode:
                print(f'Screenshots: FAILED (exit {r.returncode}): they were not generated in {a.screenshots}')
                n_errors += 1
    ok = n_errors == 0 and (n_warnings == 0 or not a.strict)
    print(f'Result: {"OK" if ok else "PROBLEMS FOUND"} ({n_errors} errors, {n_warnings} warnings)')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
