# What to do depending on the source

The skill accepts any starting content. What changes is how it is read and what is imitated.
In all cases the fidelity rule applies: the presentation contains what is examinable from the
source, without adding material or removing anything, and each scene says where it comes from in `data-ref`.

## Presentation (PPTX, PPSX, ODP or PDF of slides)

- **Content**: the same as the slides, told better; the source remains the reference
  for attendees.
- **Style**: the HTML **imitates the visual identity of the source**. When preparing it, run
  `python3 EP/tools/theme.py source.pptx` and apply the accent to the HTML:
  `python3 EP/tools/theme.py source.pptx --in pres.html`. Only the accent color
  and its light/dark pair are adopted (and the typography if requested with `--fonts`); the skill's semantic
  colors (red for what is crossed out, blue for practice, green for what is highlighted)
  do not change, so that the conventions are maintained. If nothing is detected, the
  template green is kept.
- **Teaching value**: splitting into steps, assembling the diagrams, deriving the formulas and recalculating the
  charts. This is what the HTML contributes compared to the original slides.
- It is read with `source_to_images.sh` (converts to PDF if needed) and the **images of
  all the slides are looked at**: the extracted text loses equations and labels inside figures.

## Document (PDF, DOCX, ODT, RTF, XLSX, HTML…)

- Assignments, notes, project reports, reports, rubrics, guides. `source_to_images.sh` converts what
  is needed with LibreOffice and leaves one image per page.
- The source of truth is the documents. If there are several, decide with the user which one rules and
  how they are combined. Its own rules in `documents.md`.
- `data-ref` cites the document and its section: `"PDF p. 12"`, `"Document · 3.2"`,
  `"Assignment · 5.2"`, `"Rubric · C4"`.

## Text (pasted in the chat, `.md` or `.txt`)

- There are no slides: **the outline is built by the agent**. Number or use the sections of the
  text and distribute them into scenes, one idea per scene and per step; `data-ref="Document · n"`
  (or the title of the section).
- **Turn it into something presentable**: the prose is turned into short lists, tables, diagrams,
  timelines, tiles and charts; formulas are written and derived step by step; the
  examples, with statement, approach and solution. No long paragraphs on screen.
- **Do not invent**: if the text does not provide a piece of data, a date or a figure, it is not filled in; if something
  essential for structuring is missing, the user is asked.

## Several sources or a mixed source

- Read them all before starting and decide with the user which one rules or how they are combined
  (e.g. notes + teacher's presentation, or text + standalone figures).
- Photos are taken from the source with `images.py`; if a figure is from another source, say so in
  the report.
