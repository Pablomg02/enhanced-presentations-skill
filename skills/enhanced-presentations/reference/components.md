# Components

The code for each component comes from the template: `python3 EP/tools/component.py <name>`.
Here is **when** to use each one, how to distribute the steps, its variants and its limits.
To see them in action: `new.py` does not include them, but the template does:
`EP/tools/screenshots.sh EP/template.html 1-55` (the step map for each component is given by
`review.py EP/template.html`).

When pasting any component (better with `component.py <name> --in pres.html --id …`, which sets the id and
adds it to `ORDER`): change `data-section`, `data-ref` and `data-acronyms` (the template ones are samples)
and replace the text with the source text. The insertion removes the template's `data-refs` (the footer uses
`data-ref`); if the steps come from different places, fill in `data-refs` by hand. Then `review.py --scene <id>`
and screenshots.

## Common skeleton of a scene

```html
<section class="scene" id="ID" data-section="Index section" data-ref="Slide 5">
  <h2>Title (the one from the source, or a clearer one)</h2>
  <div class="sub">Optional subtitle, 22 px, gray</div>      <!-- top 124 -->
  … content between y = 170 and y = 790 …
  <div class="punch up" data-in="3">Closing line with the <b>key idea</b></div>   <!-- optional, bottom -->
</section>
```

`data-ref` accepts the reference that corresponds to the source: `"Slide 5"`, `"PDF p. 12"`,
`"Document · 3.2"`, `"Assignment · 5.2"`.

- `h2`, `.sub`, `.punch`, `.lead` (large sentence at the top, top 176) and `.txl` (780 px text block on the
  left, top 178) already have their place: no need to position them.
- Everything else is positioned with `style="position:absolute;left:…;top:…;width:…"` or with the layouts
  (`.split`, `.cols2`, `.cols3`, `.cards`, `.tiles`, `.flow`, `.dv`).
- Always `class="up" data-in="k"` on what enters by steps (the `up` class gives it the movement).

## list
Points that enter one by one + figure on the right (560 px) that reacts to the same steps.
- Max. 5 points (with `ul.l.s` or `.xs` if they are long). Subpoints with `<ul>` inside the `<li>`.
- Without a figure: remove `.split` and use `<div class="txl" style="width:1440px"><ul class="l">…</ul></div>`.
- Larger figure or in another position: `.txl` + `<svg class="fig sk" style="left:960px;top:150px;width:580px;height:690px" viewBox="0 0 580 690">`.

## diagram
Full-width SVG that is assembled by steps: first the components, then the flow, then how it
works, then the key idea (`.punch`).
- Pieces ready to copy in `diagrams.md` (they are examples from one domain; adapt the shapes to the content).
- A callout (source note about a piece) only in its step: `<g data-in="1" data-out="2">`.
- The same diagram changing by steps (e.g. four variants of a cycle): one `<g data-in="k" data-out="k+1">`
  per variant over the common pieces; with `data-refs` if each step comes from a different place in the source.

## objective
Scene "Result · Usefulness · Procedure" (`.goal`) **before a long derivation**: the final formula
boxed (`.gf` with `.m.res`), what it allows you to calculate (`.gt`) and the route in 2-4 steps (`.route`, in words).
- Fixed subtitle: "Result, utility and procedure of the derivation". Same `data-section` as the derivation.
- Short derivation (one scene): instead of this scene, `<div class="sub obj">` under the derivation title.

## derivation
Rows "formula | note" (`.dv > .rw > .e + .nt`); each row one operation. Full guide in `formulas.md`.
- Under the title, `<div class="sub obj">Objective in one sentence</div>` (or `objective` scene before).
- Max. 4-5 rows per scene; if the derivation is long, continue in a second scene that starts from
  the last result.
- Row without a note: `<div class="rw w">`. Note with several lines that enter in different steps:
  `<span class="nl">…</span><span class="nl" data-in="2">…</span>`.
- Reference formulas on the left and derivation on the right: a
  `<div style="position:absolute;left:80px;top:196px;width:520px;…">` with the formulas (`.m.res`) and
  `<div class="dv" style="left:640px">`.

## example
Literal statement from the source (`.ex p`), the question in bold, "Given" and "Find" tiles (`.chips`) and a
figure on the right. **All practice is in blue**: `class="scene pr"` on the statement, approach and
solution; titles "Example: …" (not "Application: …").
- If the source solves the example: `example` → `approach` → `solution` (one or several scenes). If it does not
  solve it, it is not solved (that would be new material). The source hint, if any: `<div class="hint up" data-in="3">`.
- Statement with parts: `<ol><li>…</li></ol>` inside `.ex`.

## approach
Before solving: which formulas are needed and why. `.sub.dt` with "Given … Find …"; one `.rw` row
per unknown: `<span class="fx">For T<sub>2</sub></span>` + the formula **boxed as in the theory**
(`.m.res`) + note with why it can be used (hypothesis). `.punch` with the order of calculation.
- Formula from an earlier part: `.m.res.earlier` (gray dashed box) and say it in the note.

## solution
Row-by-row solution (`.dv`), in blue. `.tag` numbers each unknown (1, 2…; empty in the rows that follow);
the first row of each unknown repeats the boxed formula; the numeric result in `\bx{…}`. Notes:
what is substituted or solved for. Long parts: one scene per part ("Solution: part a").

## toolbox
Cards with a boxed formula and a line "**Application:** …" (`.card .pq`), in two uses:
- **"Preview: toolbox for Part N"**, after the scene that presents each part: the formulas that are
  going to be obtained and what they are for (mental image before deriving). Numbered cards: `.cards.numbered`,
  `<h5><span>1</span>Name</h5>`.
- **"Recap: toolbox"**, at the end of a part: the same formulas, already derived,
  with their application. No numbers and **no references to the source** in the text (only in `data-ref`).
- Six cards: `style="grid-template-rows:1fr 1fr;height:560px"` in `.cards`.

## chart
Empty `<svg id="g-…" class="fig pl" …></svg>` + a `chart('#g-…', {…})` call in the FIGURES block.
Full guide in `charts.md` (curves with formula, points read from a figure, log axes, highlights).
- Text on the left (`.txl` of ~560 px) and chart on the right (~840×620).
- Each curve, guide line or point with its `step`.

## compare
`table.cmp` table, one row per step. `td.pro` (+ green) and `td.con` (− red); `<small>` for the secondary
data; `.legend` below.
- Max. 6 rows and 3 data columns. The key word of each cell in `<b>`.
- More columns or long cells: `style="font-size:22px"` in the table, or split into two scenes.
- Highlight a row in some steps: `<tr data-hl="3">` + custom class `.cmp tr.on td { background: var(--acc-l); }`.

## cards
`.cards` (3 columns), `.cards.two`, `.cards.four`. Each `.card`: `h5` (green uppercase label)
or `h3` (title), `p`, `ul`, formulas `.m` (one per line), `.pq` ("Application: …"). No references to the
source in the text.
- Useful for: "The thread" at the start; types in parallel; formula summary at the end of a part.
- Six cards: `.cards` with `style="grid-template-rows:1fr 1fr;height:620px"`.

## tiles
`.tiles > .tile`: large number (`.big`, with unit in `<small>`) and a line of text (`p`).
- 4 tiles per row (change `grid-template-columns` in the `style` for 3). Above, a `.lead`.

## phases
`.flow > .phase` (number, `h3`, short list) with an arrow between phases; `.band` below for cross-cutting content.
- 4 phases per row; with 6-8 phases there are two rows (the arrow on the last one of each row is unnecessary:
  custom class `.phase:nth-child(4n)::after { display: none; }`).

## bars
Rows photo | name | bar with its value (`--w` = % of the bar width, proportional to the value).
- Max. 3 rows (196 px each). Without a photo: leave `<img data-img="" alt="">` (takes no space) or remove the column.
- Very different values or many elements: better a bar chart (`charts.md`).

## camera
A 1440×640 SVG with nodes `<g data-k="key"><rect class="bx" …/><text …>…</text></g>` and lines;
`CAMERA` (block 3) says in each step the view `[x, y, width, height]`, the highlighted node, the footer and the section.
- The view keeps the 2.25 ratio (width = 2.25 × height). Zoom in at most ×1.7.
- Each node entirely inside the view or completely outside (`review.py` warns if it is cut off).
- The scene `--id` can be any name; there can be only one `camera` scene per file. To return to it later:
  `[<id>, [4]]` in `ORDER`.
- Large trees reused between scenes: use a scene with reusable custom JS (pattern of
  `SCENES.camera` in the template).

## question
Only if the user asks for it. `id="q-…"`, `class="scene qs"`, `data-section` = that of the neighboring
scene (so it does not split the index), `data-ref="Class question · not from the source"`.
- Step structure: question (+ context `.qz-c`) → hint (`.qz-h`, optional) → answer (`.qz-a`) →
  link with what follows (`.qz-f`).
- Options to choose from: `<div class="qz-op"><div><b>A</b>Cold gas</div><div><b>B</b>Electric<span class="okm up" data-in="2"></span></div></div>`
  (the `.okm` box marks the correct one in the answer step).
- Advantages versus disadvantages: two `.cards.two` cards inside `.qz`.
- Photo on the right: `<img class="qz-img" data-img="dawn">` and a narrower `.qz`.
- Real verified data (with source), short question and a one- or two-sentence answer.

## Standalone pieces (without their own scene in the template)

**Source data table** (numbers right-aligned; first column left-aligned):
```html
<table class="tb up" data-in="1" style="position:absolute;left:1000px;top:200px">
  <thead><tr><th>Station</th><th>P (psia)</th><th>T (°R)</th></tr></thead>
  <tbody><tr><td>20</td><td>200</td><td>5000</td></tr><tr data-hl="3"><td>25</td><td>108.9</td><td>4420</td></tr></tbody>
</table>
```
(`tr.on` is highlighted with `data-hl`.)

**Photo with caption**:
```html
<figure class="photo-c up" data-in="0" style="left:1100px;top:180px;width:420px;height:520px">
  <img data-img="f1" alt="Photo description"><figcaption>Source photo caption</figcaption></figure>
```
The figure needs `width` and `height`; the photo fits inside without being distorted.

**Quote** (long literal definition): `<blockquote class="quote">…</blockquote>` (860 px on the left)
+ photo `<img class="photo" data-img="…" style="left:1020px;top:230px;width:500px;height:500px">`.

**Two or three columns with a diagram on top and text below**: `.cols2` / `.cols3`, each column
`<div class="up" data-in="k"><h3>…</h3><svg class="sk" viewBox="0 0 640 220">…</svg><ul class="l s">…</ul></div>`.

**Short definition needed in the scene**: light green box
`<div class="def up" data-in="1" style="right:80px;top:150px"><b>Term:</b> short definition</div>`.
If the scene has `data-acronyms`, do not put it at the top right (`review.py` warns if they overlap).

**Small note** (clarification of units, source of a fact): `<div class="note" style="position:absolute;left:800px;top:790px">…</div>`.

**Variable in the text**: `<span class="v">P<sub>e</sub></span>`; upright descriptive subscript:
`<span class="v">T<sub class="r">s</sub></span>`.

**One scene in several passes**: `ORDER = [… ['camera', [0, 1]], 'gas', 'mono', ['camera', [2]], …]`
(the scene keeps its state; useful to return to the tree between branches).

**Scene with custom JS** (timeline, tree that is built, calculated animation): in the engine,
next to `SCENES.camera`, `SCENES.miId = { steps: N, render(k, ctx) { … }, sec: k => '…' }`. Only if
no component works; copy the pattern of `SCENES.camera` and of the `camera` scene in the template.
