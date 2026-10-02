---
name: enhanced-presentations
description: 'Create animated HTML presentations from whatever is uploaded: a PowerPoint, a PDF, a document (Word, spreadsheet, guide…) or a text. (1) Subject or class, with the same content from the source told step by step, animated diagrams and derived formulas; if the source is a presentation, the HTML imitates its style and explains it better; if it is a text, it turns it into a presentation. (2) Presentation of a project or document (assignment, rubric, guide). Use when asked for "the HTML presentation", "turn this PDF/PPT/Word/text into an animated presentation", "make a presentation of this document", or when modifying an HTML created with this skill.'
---

# Enhanced Presentations

All the work relies on this folder (the skill, abbreviated `EP`; in commands, replace `EP` with its
actual path):

| What | Where |
|---|---|
| Template with engine, styles and an example of each component | `EP/template.html` |
| Create the new file | `python3 EP/tools/new.py …` |
| List components / view the code of one | `python3 EP/tools/component.py [name]` |
| **Insert a component** (scene + `ORDER` + JS if it has any) | `python3 EP/tools/component.py derivation --in pres.html --id x --after y --section "…" --ref "Slide 5"` |
| **Prepare the source for reading** (any document → images and text) | `EP/tools/source_to_images.sh source.pptx\|source.pdf\|source.docx <scratch>/source` |
| **Imitate the style of a source presentation** (palette; with `--fonts`, typography) | `python3 EP/tools/theme.py source.pptx [--in pres.html [--fonts]]` |
| **Automatic review** (errors, overlaps, overflows, acronyms, style…) | `python3 EP/tools/review.py pres.html` |
| Review a single scene and take its screenshots | `python3 EP/tools/review.py pres.html --scene x --screenshots <scratch>/cap` |
| Screenshots of specific steps | `OUT=<scratch>/cap EP/tools/screenshots.sh pres.html 5-8 12` |
| View the safe area and overflowing boxes in the browser | open `pres.html?debug#12` |
| Embedded photos | `python3 EP/tools/images.py pres.html put name photo.png` |
| Detailed guides (read the relevant one) | `EP/reference/*.md` |

Guides: **`style.md` (how presentations are written: always read it)** · `sources.md` (what to do
depending on the source: presentation, document or text) · `components.md` (when to use each component and
its variants) · `formulas.md` (formulas and derivations) · `diagrams.md` (drawing SVG diagrams: pieces ready
to copy) · `charts.md` (charts and calculated figures) · `documents.md` (presentations of a
project, exercise or document).
Model of what the scenes are like: `EP/template.html` itself (one example scene per component).

## 0. What the user asks for takes precedence

- This guide gives **defaults**, not a mold. A specific user request (an order, a tone,
  more or fewer steps, a scene without derivation, a different layout, an animation they have thought of)
  takes priority over it. If it clashes with a content rule (e.g. adding something that is not in the
  source), it is flagged in one sentence, done if the user confirms and written down in the report.
- **Components are a starting point, not a closed catalog.** They are adapted freely (positions,
  sizes, columns, combining two in one scene). If none fits what the source has (a one-off figure,
  a process that should be animated its own way, an interaction), it is made to measure: custom SVG in
  the scene, new classes in "SPECIFIC TO THIS PRESENTATION" or a scene with custom JS (`SCENES.id`, section 5).
- **Fixed**: the technical part (the engine and its step attributes, `review.py` until `OK`, looking at the
  screenshots), fidelity to the source (section 1) and the serious register of `style.md`. **Free**: layout,
  diagrams and animations. Any sober animation that helps understanding (assembling a diagram, moving the
  view, making a curve appear, showing a flow or a process that runs out) is welcome; only effects
  that explain nothing are out of place.

## 1. Content rules (by default)

**The presentation reproduces exactly the content of the source, told better.**
The source of truth is the given content: a `.pptx`/`.ppsx`/`.odp`, a `.pdf` (notes, slides,
article, report), another document (`.docx`, `.odt`, `.xlsx`…) or a text (pasted in the chat, or a
`.md`/`.txt`). Attendees can consult that original source; the HTML only helps to understand it.

**What is done depending on the source** (details in `reference/sources.md`):
- **Presentation**: same content, and the HTML **imitates its style** (palette, and typography if requested) with
  `theme.py`, explaining it better. This is the typical case: the presentation is the source of truth and the HTML, the
  most didactic aid.
- **Document**: notes, assignments, reports, rubrics or guides; `source_to_images.sh` converts it and
  `data-ref` cites the page or section.
- **Text**: there are no slides; the outline is built by the agent from its sections and it is
  **turned into something presentable** (short lists, diagrams, charts, derived formulas), without inventing.
- **Several sources**: read them all and agree with the user which one rules or how they are combined.

- **Do not add material**: no formulas, data, dates, examples or explanations that are not in the source.
- **Do not touch the source** (not to correct it, not to complete it). If a typo is seen, it is mentioned in the report.
- **Do not remove anything examinable**: every piece of data, list, definition, example, figure and formula in the source must
  appear. Only decorative items are omitted (cover pages, logos, filler photos).
- **What is allowed** (this is the value of the HTML): splitting into steps; reordering; grouping scattered material into tables or cards;
  redrawing and animating the source diagrams; recalculating its charts with its formulas; zooming
  the view into one part; highlighting the key idea; unit conversions ("≈ 6.7&nbsp;MN"); **intermediate steps
  of a derivation** (where each formula comes from, what is solved for, what is crossed out); very short
  linking sentences with no new content ("Each cycle is a different way of driving the pumps"); **explanatory
  scenes** (`objective`, `approach`, previews and recaps) that reorder what is already
  in the source.
- Everything that is not literal from the source is written down while it is being done and listed in the final report.
- **Exception: class questions** (component `question`), **only if the user asks for them**:
  they may use real examples outside the source (verified data), are marked as "Question" and with
  `data-ref="Class question · not from the source"`. Simple question; brief answer.
- **Formulas: never "out of nowhere".** Each formula from the source is built: where it comes from, what is substituted,
  what is simplified (crossed out), what is solved for. The formula as it appears in the source goes in a green
  box (`\bx{…}`). See `reference/formulas.md`.
- **Thread**: the whole must be told as a story. At the start, what will be seen and why it matters; after
  presenting each part, "Preview: toolbox for Part N"; at the end of each part, "Recap:
  toolbox" (component `toolbox`).
- **Say beforehand what is going to be done**: `objective` scene before a long derivation (or `.sub.obj` in
  short ones); `approach` scene before solving an example. Without padding: attendees want to see
  the formulas they will use in the exercises, where they come from and what they are for.

**Project or document**: same techniques, but the source of truth is the documents (assignment,
rubric, guide); its own rules in `reference/documents.md`.

**Style** (details and examples in `reference/style.md`; `review.py` checks almost everything):
- Academic and **impersonal** register: "T is solved for", "the result is obtained"; never "we are going to", "I solve", "we know",
  or colloquialisms. Short sentences; bold only on the key word; no em dash (—); `1.5&nbsp;MN`, decimal point.
- Titles that say what is done, with words: no "from X to Y" and no arrows.
- **Never cite slides or pages in the text** (nor in the toolboxes): only in `data-ref`.
- **Practice in blue**: `class="scene pr"` in the statement, approach and solution; titles "Example: …".
- **Acronyms** of each scene at the top right (`data-acronyms`), only those used in that scene.
- Important formulas boxed; specific notes on the right; `\ub` to explain terms.

## 2. Workflow (starting from a source)

Work in the scratchpad for everything intermediate. Check off each step when it is finished.

1. **Read the source of truth, in full.**
   - **Any document** (PPTX, ODP, PDF, DOCX, ODT, XLSX…): `EP/tools/source_to_images.sh source <scratch>/source`
     generates `slides/d-NN.png` (one per slide or page; `DPI=130` to see them larger),
     `contacts-N.png`, `text.txt`, `media/` and `media.txt` (which photo appears on which page). PPTX and ODP
     keep their original photos; in the other formats (PDF, DOCX, ODT…) the photos are extracted with
     `pdfimages` (poppler) when available and `media.txt` maps each page to its images; if the tool is
     missing, the script warns and continues without them. It converts to PDF with LibreOffice if the format
     is not already one.
     **Look at the images of ALL the slides or pages**, not only `text.txt`: `pdftotext` loses
     equations and text inside figures (in a class topic it gave the impression that content was missing
     when it was actually there).
   - **If the source is a presentation** (PPTX/ODP/PDF of slides), know its style:
     `python3 EP/tools/theme.py source.pptx` (colors; with `--fonts`, also typography). It is applied to the HTML
     when creating it (step 4). Typography is available for PPTX/ODP; on a PDF, `--fonts` applies only the
     colors and warns that the font is not available. Only the accent is imitated; the skill's color
     conventions do not change.
   - **Text** (pasted in the chat, or `.md`/`.txt`): read it in full; if it is long, number its sections and
     use that numbering in the inventory and in `data-ref` ("Document · 3.2"). The scene outline is
     built from those sections, turning the prose into presentable material.
   - If the user gives several documents, read them all and decide with the user which one rules or how they are combined.
2. **Inventory** (`<scratch>/inventory.md`), one row per slide, page or section:
   ```
   | Slide/p. | Examinable content (everything: data, formulas, lists, figures) | Scene · step | Done |
   |  5   | Tt = T + V²/2cp; h_t; "static temperature"; q−w = cp(Tt,out − Tt,in) | total · 0-3 | ☐ |
   ```
3. **Outline** (`<scratch>/outline.md`): list of scenes with their id, component, slides/pages/sections
   and what goes into each step. Rules:
   - **One idea per step; one diagram per scene, which is assembled as it goes.** Typical scene: 2 to 6 steps.
   - Max. ~5 list points or ~5 formula rows per scene; if it does not fit, split into two scenes
     (`area` and `area2`, with the same `data-section`).
   - Group slides or sections that deal with the same thing (advantages in one and disadvantages in another → one table).
   - If there is a classification, use it as the thread (component `camera`: overview and zoom into each branch).
   - Choose the component with the table in section 4.
   - Add the explanatory scenes (section 1): introduction, preview of each part, `objective` before
     each long derivation, `approach` before each solution, recap at the end of each part.
   - Long sources (> 40 slides or pages): split into parts at a logical point, do the first one,
     deliver it and continue when the user asks.
4. **Create the file** (do not copy the template by hand):
   ```
   python3 EP/tools/new.py presentation.html \
     --title "Presentation title" --short "Short title" --brand "Brand or subject" \
     --block "Block 2 · Kinetics" --source "topic_2.3.pptx" --parts "Introduction|Rate|Catalysis"
   ```
   If the source is a presentation, apply its style afterwards:
   `python3 EP/tools/theme.py source.pptx --in presentation.html`.
5. **Build scene by scene**, always with this cycle (do not write them all and review at the end):
   1. Insert the component (the scene, its place in `ORDER` and its JS, in one go):
      `python3 EP/tools/component.py <component> --in pres.html --id <id> --after <previous id> --section "…" --ref "Slide 5"`
      (`id` unique, short, no spaces; `data-section` = name in the index, if omitted it is inherited from
      `--after`; `data-ref` = where the scene comes from: "Slide 5", "Slides 5 and 6", "Slides 5–7", "PDF p. 12",
      "Document · 3.2"). If it says "NOTE: the template values remain", change them. The insertion removes the
      template's `data-refs` (the footer uses `data-ref`); if the steps come from different places in the
      source, fill in `data-refs` by hand (one reference per step, separated by `|`). Without `--in`, the
      component is printed to copy it by hand.
   2. Replace all the text with the source text and delete whatever is left over. Set `data-acronyms` if there are acronyms and
      `class="scene pr"` if it is practice.
   3. `python3 EP/tools/review.py pres.html --scene <id> --screenshots <scratch>/cap` → fix
      everything marked with ✗ and decide each !.
   4. **Look at the screenshots** (`<scratch>/cap/sheet-1.png`) and go through the checklist in section 6.
   5. Mark in the inventory what is already done.
6. **Photos** (few, the ones from the source, in gray): `python3 EP/tools/images.py pres.html put f1 <scratch>/source/media/image7.jpeg [--crop x0,y0,x1,y1]`
   and in the HTML `<img data-img="f1">`.
7. **Final review**:
   - `python3 EP/tools/review.py pres.html --pages N` (N = number of slides or pages in the
     source) → it must end with `Result: OK`. The warnings (!) are looked at one by one: they are fixed or
     justified in the report.
   - Screenshots of all the steps (in batches of 6) and look at them: they reveal the things the automatic
     review cannot judge (a confusing diagram, an arrow pointing the wrong way, colors with no meaning).
   - Go over the inventory: all rows checked.
8. **Deliver**: the HTML stays where the user asked for it. Do not commit unless asked.
   Brief report to the user (format in section 8).

## 3. Design

- Minimalist and useful for presenting: white background, no ornaments, no bounces or flashy effects.
  Default accent, green `#92D050` (text `#4f7d1e`); if the source is a presentation, it is replaced
  with its own using `theme.py`.
- Fixed canvas 1600×900 (it scales on its own). Side margins 80 px. Safe area: y from 170 to 790
  (up to 740 if there is a `.punch` at the bottom). Sizes: title 46; list 30 (27 with `.s`, 25 with `.xs`);
  subtitle 22; formulas 34 (`.s` 30, `.xs` 26); diagram labels 19; never less than 16.
- Semantic colors, always the same ones: `--neg` (red) for what is crossed out or highlighted in the negative,
  `--c2` (blue) for a second term, `--c3` (orange) as a third color, `--pos` (medium green) for what
  advances and `--warm` (light orange) for active or warm areas; what is highlighted in green (`--acc`). The
  specific meaning of each color is fixed at the start of the presentation and does not change.
- If the source is a presentation, the accent (`--acc`, `--acc-d`, `--acc-l`) is taken from its palette with
  `theme.py`; the skill's semantic colors are not touched.
- The animation explains something: flows (`.fl`) to indicate direction; running processes (flame, jet) when
  something works; loops for continuous processes (`.alt`); processes with an end for what runs out
  (`data-go` + `.once`). If it contributes nothing, it is not animated.
- Each scene indicates at the bottom where it comes from (`data-ref`, or `data-refs` with one reference per step), and at the top right
  its acronyms (`data-acronyms`). Practice (examples, exercises) in blue: `class="scene pr"`.
- Tables: the key word of each cell in bold, to follow it at a glance. If a table becomes
  confusing, summarize its features in a separate scene (cards).

## 4. Which component to use

`python3 EP/tools/component.py` lists them all. Full guide: `reference/components.md`.
The table is a guide: if the content calls for something else, adapt it or make it to measure (section 0).

| In the source there is… | Component |
|---|---|
| List of points (with or without a simple figure) | `list` (without a figure: `.txl` full width) |
| Diagram of a system: parts, pipes, layers, blocks… | `diagram` (pieces in `reference/diagrams.md`) |
| Before a long derivation: what is obtained, what for and how | `objective` |
| Equations, derivations, solving for | `derivation` |
| Example or exercise (statement) | `example` |
| Before solving: formulas needed and why | `approach` |
| Numerical solution | `solution` |
| Preview of a part / recap of formulas | `toolbox` |
| Chart (curves with a formula or read from a figure) | `chart` |
| Advantages / disadvantages; characteristics of several types | `compare` |
| Several types or cases in parallel; final summary | `cards` |
| Classification, tree | `camera` |
| Key figures, dates, typical values | `tiles` |
| Comparing a quantity across elements | `bars` |
| Procedure, phases, sequence | `phases` |
| Class question (only if requested) | `question` |

## 5. Engine: steps and attributes

The steps of a scene are counted from 0 (step 0 is what is seen on entry). The scene has as many
steps as the highest number used + 1.

| What | How |
|---|---|
| Order | `ORDER = ['cover', 'list', ['camera', [0, 1]], …]` (a scene can be repeated with individual steps) |
| Appear at step k | `data-in="k"` (`class="up"` = moves up slightly on entry) |
| Disappear at step k | `data-out="k"` (with `data-in`: visible from `in` to `out−1`) |
| Start a process with an end | `data-go="k"` (adds `.go`, hides nothing) |
| Highlight at certain steps | `data-hl="2"`, `"2-4"`, `"1,3-4"` (adds `.on`; e.g. `<g class="hlg" data-hl="2">`) |
| Section / reference | `data-section="…"`, `data-ref="Slide 5"`, `data-refs="Slide 5\|Slide 6"` (one per step) |
| Acronyms (top right) | `data-acronyms="<b>MFP</b>: <i>Mass Flow Parameter</i> (mass flow parameter) · <b>C-D</b>: …"` |
| Practice in blue | `class="scene pr"` |
| Index (key I) | sections (`data-section`) that expand in scenes (title = `h2`, or `data-title="…"` if it is long) |
| Formula | `<span class="m" data-tex="…">` (steps inside: `\in[k]{}`, `\cx[k]{}`, `\ha[k]{}`, `\ub[k]{term}{label}`) |
| Chart | `chart('#id', {…})` in the FIGURES block |
| Photos | `<img data-img="name">` (set by `images.py`) |
| Scene with custom JS | `SCENES.id = { render(k, {jump, entering, dir}), steps?, sec?(k) }`; `tween()` to interpolate |
| Tests | `#12` (step 12), `?static` (no transitions), `?t=ms` (freezes animations), `?debug` (safe area and overflowing boxes) |

## 6. Checklist for each scene

Before moving on to the next one (`review.py` checks what is marked with ⚙):
- [ ] Everything examinable from its slides, pages or sections is there; nothing added that is not in the
      source (except intermediate steps and linking sentences, noted for the report).
- [ ] If it derives: it says beforehand what it obtains (`objective` or `.sub.obj`) ⚙; one operation per row; specific notes;
      final formula boxed.
- [ ] If it is practice: `class="scene pr"` ⚙, title "Example: …" ⚙, and `approach` before the solution.
- [ ] Acronyms in `data-acronyms` ⚙; impersonal text ⚙; no "slide" or "p." in the text ⚙; titles without "from X to Y" ⚙.
- [ ] `review.py --scene <id>` with no ✗ and each ! decided ⚙; screenshots checked: the diagram is understandable,
      the arrows point correctly, the colors make sense.

If something does not fit, it is fixed by hand (split into steps or scenes, `.s`/`.xs`, move): there is no automatic adjustment.

## 7. Known pitfalls

- **Do not write all the scenes and review at the end**: review each scene when it is finished.
- `review.py` does not judge whether a diagram is correct or clear: that can only be seen in the screenshots.
- An element that animates its opacity (`.glow`, `.alt .fa`, `.stop`) cannot carry `data-in`:
  wrap it in `<g data-in="k">…</g>`.
- New classes: at the end of the CSS, in "SPECIFIC TO THIS PRESENTATION", and first check with `grep` that the
  name does not exist (there have already been clashes: `.tx`, `.stp`, `.card`). Do not redefine template classes.
- A scene in `ORDER` that does not exist breaks the whole presentation (`review.py` says so).
- Number and unit with `&nbsp;` so they do not split; values with a decimal point.
- With the camera, each node must stay entirely inside the view or entirely outside it (`review.py` warns
  of "is cut off").
- The line `const IMG = {...};` must stay on its own (it is edited by `images.py`).
- Component code is copied from `EP/template.html` (or with `component.py`), not from
  old presentations with different engines or classes.
- The template's `.note` is a small gray note; the definition box is `.def`.
- Equations inside figures or images do not appear in `text.txt`: read them in the images of the
  slides or pages.

## 8. Final report to the user

Brief, in English:
1. File(s) created; number of scenes and steps; result of `review.py`.
2. Scenes, one line each (or by sections if there are many).
3. **What is not literal from the source** (intermediate derivations, notes, linking sentences, redrawn or
   recalculated figures, conversions, questions), so that the user can decide whether to remove it.
4. Slides, pages or sections omitted as decorative; typos seen in the source (without touching it).
5. What could not be verified (e.g. animations in motion in a real browser).

## 9. Recipes per task

- **New presentation from a source**: section 2 in full.
- **Text source** (pasted, `.md`, `.txt`): number its sections and build the inventory per section;
  its own outline (one idea per scene and step) and `data-ref="Document · n"`; rules in `reference/sources.md`.
- **Imitate the style of the source presentation**: `theme.py source.pptx` to see its palette and
  `theme.py source.pptx --in pres.html` to apply it; with `--fonts`, also the typography (PPTX/ODP; on a
  PDF, only the colors are applied and it warns that the font is not available). Only the accent changes;
  the skill's semantic colors are kept.
- **Apply user comments to a finished presentation**: read the comments and `style.md`; locate
  the scenes (`review.py pres.html` prints the map); change only what was asked, without reordering or lengthening; for
  each scene touched, `review.py --scene <id> --screenshots …` and look; at the end, the full `review.py`. Style
  or acronym warnings in untouched scenes are mentioned in the report, not fixed without asking.
- **Add a solved example**: `example` + `approach` + `solution` (all `pr`), inserted with
  `component.py --in … --after <scene>`; same `data-section`.
- **Acronyms**: `review.py` lists, per scene, the words in capitals that its `data-acronyms` does not explain;
  those that are acronyms are explained there, and proper names or units are ignored.

## Worked examples

- `EP/template.html`: one example scene per component (list, diagram, objective, derivation,
  example/approach/solution, chart, comparison, cards, tiles, phases, bars, camera and question).
  It is the code reference: components are copied from here with `component.py`.
- Presentations created with this skill are not versioned in the repository (the content is usually
  third-party); the final HTML is self-contained and is delivered wherever the user asks.
