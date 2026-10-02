# Project, assignment or document presentations

To present in class or at a meeting a project, an assignment, a proposal or any document
(assignment, rubric, guide, report, write-up). The source is not a finished presentation but
the documents that describe the work.

## What changes compared to a content presentation

- **Source of truth**: the documents (assignment `.tex/.pdf`, rubric `.ods/.xlsx`, guide, report).
  Read them in full before starting. `source_to_images.sh` converts with LibreOffice anything that is
  not PDF (`.docx`, `.odt`, `.xlsx`…) and leaves one image per page. Spreadsheets to read figures:
  `soffice --headless --convert-to csv` or `python3` with `pandas`/`odfpy` if available. If a format
  cannot be read, ask the user to export it.
- **Do not invent**: dates, grades, weights, group sizes, material to be submitted, places… only what
  the documents or the user say. If a fact is missing, ask for it; do not fill it in.
- `data-ref` says where each scene comes from: `"Assignment · 5.2 Scope"`, `"Rubric · C4 and CE2"`,
  `"Course guide · Dates"`, `"PDF p. 3"`.
- File: where the user says (for example `YYYYMMDD_Presentation_<name>.html`). Create with
  `new.py` (see `SKILL.md`, step 4) and `--brand` with the entity or subject.
- Usually without formulas: delete the "Green box" sentence from the help (`review.py` warns about it).

## Style criteria for these presentations

- **Formal, serious register**: no colloquialisms, preferably impersonal ("Each group submits…",
  "It is assessed…").
- **Do not overwhelm**: few words per step; each rubric criterion in **one simple sentence** that says
  what is assessed (no lists with colons or subcriteria). If a table does not add value, remove it.
- **Visual before table**: the grade as a block bar with its weight; the grade formula large and
  explained; dates in a timeline.
- **Non-threatening tone**: the conditions to fail or not pass are stated neutrally.
- **The practical and concrete at the end**: what must be done now and in the next sessions (cards
  "Today" / "Next session"), which group it affects and the deadlines.
- Suggestions that are not mandatory are presented as suggestions ("it can be…"), not as rules.

## Typical outline

| Scene | Component |
|---|---|
| Cover: project or document name, context, parts | cover (`new.py --parts`) |
| What it consists of, with key figures (group, weight in the grade, date) | `tiles` with `.lead.big` |
| What is given and what is done | `diagram` (the object, process or system, colored by steps) + `.cols3` |
| What must be done, in order | `phases` (+ `.band` with the cross-cutting content) |
| How it is assessed | block bar / `compare` with one sentence per criterion |
| Special cases (what happens if…) | `cards` |
| Dates | timeline or `tiles` |
| Next steps | `cards two` |

Review and submit like a content presentation: `review.py` until `OK`, screenshots checking each
step, a short report (without the "not literal from the source" part; instead, which data were taken from
which document and which were missing).
