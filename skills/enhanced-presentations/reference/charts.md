# Charts and calculated figures

The source charts are **recalculated** with their own formulas (or with points read from the figure),
instead of pasting the image: they look sharp and each curve can enter in its step. They are made in
script block 2 (FIGURES), under "FIGURES FOR THIS PRESENTATION", with one `chart()` call per chart.

## Basic use

In the scene, an empty SVG with class `pl` (on-screen size = viewBox):
```html
<svg id="g-growth" class="fig pl" style="left:700px;top:160px;width:840px;height:620px" viewBox="0 0 840 620" aria-label="Accumulated capital versus time"></svg>
```
In FIGURES:
```js
/* Slide 9: accumulated capital (template example) */
chart('#g-growth', {
  x: [0, 20], y: [0, 3.5], xl: 'Time (years)', yl: 'Capital (× C_{0})',
  xt: [0, 5, 10, 15, 20],                                 // marks (otherwise automatic)
  curves: [
    { f: t => Math.pow(1.03, t), step: 0, draw: true, label: 'i = 3 %', labelX: 15, dy: -12 },
    { f: t => Math.pow(1.06, t), step: 2, cls: 'd', label: 'i = 6 %', labelX: 14, dx: -70, dy: 34 },
  ],
  lines: [{ x: 10, step: 1 }],                            // dashed vertical guide at x = 10
  points: [{ x: 10, y: Math.pow(1.03, 10), label: num(Math.pow(1.03, 10), 2), step: 1 }],
});
```
The `f` functions are those of each subject: they are written in the call itself (here, compound
interest). No library is needed.

## Options

| Option | What |
|---|---|
| `x`, `y` | range `[min, max]` of each axis |
| `log` | `'x'`, `'y'` or `'xy'`: logarithmic axes (marks in decades) |
| `box` | `[left, top, right, bottom]` of the axes area, in viewBox px (by default it leaves room for the marks and titles) |
| `xt`, `yt` | marks: `[0, 1, 2]` or with text `[[0, '0'], [0.5, '0.5']]`; `[]` = no marks |
| `xl`, `yl` | axis titles; they accept `P_{t}` `x^{2}` (subscripts and superscripts) |
| `grid` | `false` removes the horizontal background lines |

Each **curve**:

| Field | What |
|---|---|
| `f: x => …` | function (sampled with 300 points; `n` to change it) |
| `data: [[x, y], …]` | points (e.g. read from a source figure); `smooth: true` joins them with a monotone curve; `marks: true` draws the points |
| `from`, `to` | x range where it is drawn |
| `cls` | `'d'` dashed · `'th'` thin · `'fa'` gray · `'ac'` green · `'fu'` red · `'ox'` blue · `'or'` orange (they combine: `'d fa'`) |
| `color` | manual color (`'#b5621b'`), if needed |
| `step` / `until` | `data-in` / `data-out` of the curve |
| `hl` | steps in which it is highlighted in green (`'3'`, `'2-4'`) |
| `draw: true` | the curve is drawn as it appears |
| `label`, `labelX`, `dx`, `dy`, `anchor` | curve label: text, x where it is placed, offset in px, alignment |

Stretches outside the y range are not drawn (asymptotes are no problem).

**Guide lines** (`lines`): `{ x: 1 }` vertical, `{ y: .5 }` horizontal, `{ x: 1, y: .68 }` in an L from
the axes to the point; with `step`, `label`, `dx`, `dy`.
**Points** (`points`): `{ x, y, label, step, dx, dy, hollow: true, r }`.

`chart()` returns `{ X, Y, g }` (scales and group) to add things by hand:
```js
const G1 = chart('#g-isp', { … });
el('path', { class: 'area', d: `M${G1.X(1)} ${G1.Y(0)} …`, 'data-in': 2 }, G1.g);
```
Block utilities: `el(tag, attributes, parent, text)`, `pth([[x, y], …])` (path),
`lin(a, b, c, d)` / `lg(…)` (scales), `num(v, decimals)` (decimal point), `txt(parent, attributes, 'P_{t}')`,
`pchip(xs, ys)` (monotone interpolation).

## Compressible flow functions (`GAS`)

**Example** utilities (compressible flow) included in the template; for another subject, write the
source functions in the `chart()` call itself. Calorically perfect gas, γ = `g`:
`GAS.tt(M, g)` = T<sub>t</sub>/T · `GAS.pp(M, g)` = P/P<sub>t</sub> · `GAS.ar(M, g)` = A/A* ·
`GAS.mfp(M, g)` = MFP·√R · `GAS.mOfPp(p, g)` = M from P/P<sub>t</sub> ·
`GAS.mOfAr(ar, g, sup)` = M from A/A* (`sup` true: supersonic branch) ·
`GAS.ns(M1, g)` = normal shock `{ M2, p21, pt21 }`.
Other subject formulas: write them as a function in the call itself (`f: x => …`), copied from the source.

## Curves read from a figure

If the source includes a chart without a formula (experimental data, curves from a book):
1. Open the slide or page at `DPI=130` and read 6-12 points from each curve (x, y) with their units.
2. `data: [[…], …], smooth: true`. Say it in the report ("curves read from the source figure").
3. Same axes, ranges and marks as the original figure.

## Bar chart

There is no dedicated function; with `el()`:
```js
(function () {
  const svg = document.querySelector('#g-bars'); if (!svg) return;
  const X = lin(0, 500, 420, 1380), ax = el('g', {}, svg), b = el('g', { 'data-in': 1 }, svg);
  [['Stored gas', 60, 179], ['Solids', 280, 300], ['LOX / LH2', 450, 450]].forEach(([t, a, c], i) => {
    const y = 60 + 70 * i;
    el('text', { class: 'al', x: 400, y: y + 7, 'text-anchor': 'end' }, ax, t);
    el('rect', { class: 'bar grow', x: X(a), y: y - 16, width: Math.max(X(c) - X(a), 8), height: 32, rx: 4 }, b);
    el('text', { class: 'tk', x: X(c) + 14, y: y + 7 }, b, (a === c ? a : a + '–' + c) + ' s');
  });
})();
```
(`.grow` makes the bar grow as it appears.)

## Profile figure (nozzle) with `data-noz` (optional)

The template includes, as an example resource for subjects with fluids or machines, a duct profile
generator. It is not necessary for other subjects.

```html
<g class="noz" data-noz="x0 x1 yc rc rt re xa xt closed cold"></g>
```
Inside any `.sk` SVG. It draws the interior, hatched walls and outline:
- `x0`, `x1`: start and end in x; `yc`: y of the axis.
- `rc`: chamber radius (straight until `xa`); `rt`: throat radius, at `xt`; `re`: exit radius at `x1`.
- `closed`: 1 = end wall (closed chamber); 0 = open. `cold`: 1 = gray interior (no combustion).

Examples: full C-D nozzle `data-noz="40 520 170 95 40 105 130 280 0"`; closed chamber with
convergent-divergent `data-noz="60 780 150 105 48 48 330 780 1"` (re = rt: no divergent section).
