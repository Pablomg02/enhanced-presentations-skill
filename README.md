# Enhanced Presentations

**AI agent skill that turns a PowerPoint, a PDF or a text into an animated, self-contained HTML presentation faithful to the source content.**

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Pablomg02/enhanced-presentations-skill)](https://github.com/Pablomg02/enhanced-presentations-skill/releases)
[![Python 3](https://img.shields.io/badge/python-3-3776AB.svg?logo=python&logoColor=white)](#requirements)

> [!NOTE]
> **Summary.** Starting from a source (a PowerPoint, a PDF with notes, slides or an article, another document
> such as Word, a spreadsheet or a guide, or plain text), the skill generates an animated HTML presentation
> that reproduces its content: every slide, page or section becomes a scene with steps, redrawn diagrams and
> derived formulas. If the source is a presentation, the HTML **mimics its style** (palette, and typography if
> requested) and explains it better; if it is text, it **turns it into something presentable**. `review.py`
> verifies that nothing overlaps, overflows or breaks the style rules. The task is completed with a single
> prompt, with no scene-by-scene instructions.

The skill was initially developed as the HTML presentation system for a university subject and was later
generalized: it is not tied to a specific subject or format, and instead accepts **any starting content**
(presentations, documents or text). The result is a single HTML file with no network dependencies, which opens
in any browser and is presented full screen (keyboard-driven steps, index, help and screenshots for review).

## Contents

- [Overview](#overview)
- [Usage example](#usage-example)
- [How it works](#how-it-works)
- [Compatibility](#compatibility)
- [Requirements](#requirements)
- [Installation](#installation)
- [Repository structure](#repository-structure)
- [Indicative evaluation](#indicative-evaluation)
- [Scope and adaptation](#scope-and-adaptation)
- [Limitations](#limitations)
- [Maintenance and contributions](#maintenance-and-contributions)
- [License](#license)
- [Detailed installation for AI agents](#detailed-installation-for-ai-agents)

## Overview

Converting a source into slides usually poses two problems: the agent summarizes or invents content, and the
result is static or includes animations that add no information. This skill addresses both:

- **Source fidelity.** Before writing a single line, the agent builds an **inventory** of everything
  examinable (data, formulas, lists, figures) and an **outline** of scenes. Each scene indicates its origin
  in `data-ref` (`Slide 5`, `PDF p. 12`, `Document · 3.2`). No content missing from the source is added, and
  no examinable content is omitted.
- **Animation with explanatory value.** Step engine (`data-in`, `data-out`, `data-go`, `data-hl`), SVG
  diagrams assembled step by step, formulas that are derived (substitution, crossing out, solving for) and
  charts recalculated with the source formulas.
- **Component catalog.** Lists, diagrams, derivations, examples (approach and solution), charts,
  comparisons, cards, tiles, phases, bars, camera for classifications and questions. `component.py` inserts
  each component into the scene and into `ORDER` in one go.
- **Automatic review.** `review.py` walks through all steps in headless Chrome and detects JavaScript errors,
  badly written formulas, overlaps, overflows, text that invades the frame, font sizes that are too small,
  steps with no changes and style warnings. The review ends with `OK` or `PROBLEMS FOUND`.
- **Self-contained deliverable with no network dependencies.** The final HTML bundles styles, engine,
  formulas (STIX Two subsets) and photographs in base64.

## Usage example

Once installed, it is enough to attach the source and state the prompt:

> Turn this class PDF into an animated HTML presentation.

or

> Convert this PowerPoint into an HTML presentation, with the same content and its same style, to present it.

or

> Turn this Word document into an HTML presentation to present it in class.

The agent reads the complete source (images of all slides or pages, not just the extracted text), prepares the
inventory and the outline, creates the HTML with `new.py`, builds each scene with `component.py`, reviews it
with `review.py` and delivers:

1. The self-contained `.html` file, in the indicated location.
2. A brief report: scenes and steps, review result, elements that are not literal from the source, content
   omitted as decorative and aspects that were not verified.

It also makes it possible to present a project or document (assignment statement, rubric, guide), following
the rules in `reference/documents.md`, and to **review or extend** an existing presentation.

## How it works

| Phase | Description |
|---|---|
| 1. Source reading | `source_to_images.sh` converts any document (PPTX, ODP, PDF, DOCX, ODT…) into one image per slide or page, contact sheets, text and photographs. Plain text is read directly. If the source is a presentation, `theme.py` detects its palette and its font. |
| 2. Inventory | One row per slide, page or section: everything examinable and its destination scene. |
| 3. Outline | Scenes, component, steps and references; explanatory scenes are added (objective, approach, previews, recaps). |
| 4. Construction | `new.py` creates the HTML; `component.py` inserts each component with its position in `ORDER`; each scene is reviewed and its screenshots are checked when it is finished. |
| 5. Final review | Complete `review.py` run until `OK`, screenshots of all steps and report to the user. |

## Compatibility

| Platform | Installation | Status |
|---|---|---|
| **Claude Code** (terminal, IDE, desktop) | Plugin from the marketplace or link in `~/.claude/skills/` | Documented (Agent Skills format) |
| **Codex CLI** | user or project `.agents/skills/` | Documented (Agent Skills format) |
| **OpenCode** | `.opencode/skills/`, `~/.config/opencode/skills/` or `~/.claude/skills/` | Documented (Agent Skills format) |
| **claude.ai / Claude app** | Upload of the `.skill` file | Documented (requires code execution) |
| **ChatGPT** | Workspace Skills or ZIP in a Project | Partial: the alternative without Skills does not run scripts |
| **Gemini CLI, Cursor, GitHub Copilot** | `.agents/skills/` (and `.claude/skills/`, depending on the tool) | Not verified in this repository |

## Requirements

- **Python 3** with **Pillow** (`images.py` and the contact sheets).
- **`pdftoppm`, `pdftotext` and `pdfimages`** (poppler-utils) to read PDFs, to convert PPTX files and to
  extract the photos of the non-presentation formats (PDF, DOCX, ODT…).
- **LibreOffice** (`soffice`) to convert any document to PDF (`.pptx`, `.odp`, `.docx`, `.odt`…).
- **`unzip`** (optional) to extract the original photos from PPTX/ODP; without it, `source_to_images.sh`
  warns and continues without those photos.
- **Chrome or Chromium** in headless mode to complete `review.py` and for `screenshots.sh` (it can be forced
  with `CHROME=/path`). Without it, the browser review does not run and the review ends in `PROBLEMS FOUND`
  (exit 1) with an environment message, never a false `OK`.
- **`fonttools` and `brotli`** only to regenerate the formula fonts (`fonts.py --generate`).
- **No network needed** to create or use the presentations.

## Installation

### Claude Code

```bash
claude plugin marketplace add Pablomg02/enhanced-presentations-skill
claude plugin install enhanced-presentations@enhanced-presentations-skill
```

Manual alternative: clone the repository and link `skills/enhanced-presentations` into
`~/.claude/skills/enhanced-presentations`.

### Codex CLI

```bash
git clone https://github.com/Pablomg02/enhanced-presentations-skill ~/enhanced-presentations-skill
mkdir -p ~/.agents/skills
ln -s ~/enhanced-presentations-skill/skills/enhanced-presentations ~/.agents/skills/enhanced-presentations
```

### OpenCode

```bash
git clone https://github.com/Pablomg02/enhanced-presentations-skill ~/enhanced-presentations-skill
mkdir -p ~/.config/opencode/skills
ln -s ~/enhanced-presentations-skill/skills/enhanced-presentations ~/.config/opencode/skills/enhanced-presentations
```

### claude.ai / Claude app

Download `enhanced-presentations.skill` from the latest release and upload it in **Customize → Skills →
"Upload a skill"**. Enable "Code execution and file creation". No network access is needed.

### ChatGPT

If the plan includes Skills: **Skills → Create → Upload from your computer**. Otherwise, attach the release
ZIP in a Project and paste the contents of `SKILL.md` as instructions (without running the scripts, the agent
will have to write the HTML by hand).

## Repository structure

```
.
├── skills/enhanced-presentations/      # Skill
│   ├── SKILL.md                        # Entry point and agent instructions
│   ├── template.html                   # Engine, styles and one example of each component
│   ├── tools/                          # new.py, component.py, review.py, source_to_images.sh, theme.py…
│   │   └── fonts/                      # STIX Two subset for the formulas (woff2)
│   └── reference/                      # style, components, formulas, diagrams, charts, documents
├── LICENSE · NOTICE.md · OFL.txt       # MIT license, third-party notice and SIL OFL 1.1 text
├── tools/                              # Skill packaging (not distributed with it)
├── .claude-plugin/                     # Plugin and marketplace manifest
└── .github/                            # CI, release and issue template
```

The repository does not include a `benchmarks/` folder or an evaluation harness. The comparison below is
indicative only.

## Indicative evaluation

Informal test, with no harness and no repetitions (it is not a certified measurement): the same task, a
complete presentation from a source, was requested **without the skill** and **with the skill**.

| Aspect | Without the skill | With the skill |
|---|---|---|
| Task completion | With lightweight models (for example, **DeepSeek V4.1 Flash**) a complete presentation was not obtained | A lightweight model (**DeepSeek V4.1 Flash**) completes it from start to finish |
| Prompt | **Extensive**: scene-by-scene instructions and corrections over several turns | **Brief**: "turn this PDF/PPT/text into an animated HTML presentation" |
| Turns | Several, until the result was adjusted | One |
| Source fidelity | The source was not fully followed: pages were omitted and content was summarized or added | The content is reproduced: inventory and `data-ref` per scene, with no additions or omissions |
| Output format | Static HTML or loose slides | Animated, self-contained HTML, with steps and diagrams |
| Review | Manual, with no defined criteria | `review.py`: overlaps, overflows, style and formulas, until `OK` |

> [!WARNING]
> These are usage impressions, not a reproducible evaluation: there is no `benchmarks/`, no judge, no
> repetitions and no metrics. The formal comparison is pending.

## Scope and adaptation

The skill is general: it works with any subject, course or document. Its structure (a template with a step
engine, a component catalog, creation and review tools, and guides) can be reused as is. If the source is a
presentation, `theme.py` adapts the accent color (and the typography, if requested) to its visual identity;
the template keeps the default green. For a custom style (colors, typography, brand) it is enough to modify
`template.html` and `reference/style.md`; the thematic examples in `reference/diagrams.md` and `charts.md`
are patterns, not a closed catalog.

## Limitations

- **The agent must review the source images**, not just the extracted text: equations and text included in
  figures do not appear in `text.txt`. The skill requires this, but cannot guarantee it.
- **`review.py` does not evaluate whether a diagram is clear or correct**: that can only be seen in the
  screenshots.
- **Browser review requires Chrome or Chromium**; without them, `review.py` cannot complete the review: it
  reports the environment problem and ends in `PROBLEMS FOUND` (exit 1) instead of giving a false `OK`.
- **Very long sources** are split into parts by decision of the agent and the user.
- The generated HTML is a visual aid; **the original source remains the reference** and is not modified.

## Maintenance and contributions

- Bugs or improvements: [`CONTRIBUTING.md`](CONTRIBUTING.md) and the repository issue template.
- Skill packaging: `python3 tools/package.py` (generates `dist/enhanced-presentations.skill`).

## License

The code and instructions of the skill are under the MIT license ([`LICENSE`](LICENSE)). The `EP Math` and
`EP Sym` fonts are subsets of STIX Two, under the SIL Open Font License 1.1 (see [`NOTICE.md`](NOTICE.md);
the full license text is in [`OFL.txt`](OFL.txt)).

## Detailed installation for AI agents

This section contains everything needed to install the skill without reading the rest of the document. The
skill lives in [`skills/enhanced-presentations/`](skills/enhanced-presentations/) and its entry point is
`SKILL.md`. The `git clone` commands and the remote marketplace require the repository to be published on
GitHub; if it is not, replace `https://github.com/Pablomg02/enhanced-presentations-skill` with the local path
of the checkout (in Claude Code, `claude plugin marketplace add /path/to/checkout` works). After installing,
the usual check is to ask "Which skills do you have available?" and confirm that `enhanced-presentations`
appears (with the Claude Code plugin, `enhanced-presentations:enhanced-presentations`).

### Claude Code

```bash
claude plugin marketplace add Pablomg02/enhanced-presentations-skill
claude plugin install enhanced-presentations@enhanced-presentations-skill
claude plugin list
```

Manual alternative:

```bash
git clone https://github.com/Pablomg02/enhanced-presentations-skill ~/enhanced-presentations-skill
mkdir -p ~/.claude/skills
ln -s ~/enhanced-presentations-skill/skills/enhanced-presentations ~/.claude/skills/enhanced-presentations
```

Check: in a new session, `/skills` lists it as `enhanced-presentations`
(or `claude -p "Which skills do you have available?"`).

### Codex CLI

```bash
git clone https://github.com/Pablomg02/enhanced-presentations-skill ~/enhanced-presentations-skill
mkdir -p ~/.agents/skills
ln -s ~/enhanced-presentations-skill/skills/enhanced-presentations ~/.agents/skills/enhanced-presentations
```

Check: `codex exec --skip-git-repo-check "Which skills do you have available? Reply only with the list of names." < /dev/null` must include `enhanced-presentations`.

### OpenCode

```bash
git clone https://github.com/Pablomg02/enhanced-presentations-skill ~/enhanced-presentations-skill
mkdir -p ~/.config/opencode/skills
ln -s ~/enhanced-presentations-skill/skills/enhanced-presentations ~/.config/opencode/skills/enhanced-presentations
```

Check: `opencode run "Which skills do you have available?"` must include `enhanced-presentations`.

### claude.ai / Claude app

1. Download `enhanced-presentations.skill` from the release (or generate it with `python3 tools/package.py`).
2. **Customize → Skills → "+" → "+ Create skill" → "Upload a skill"** and upload the `.skill` (it is a ZIP
   with the skill folder inside).
3. In **Settings → Capabilities**, enable "Code execution and file creation". No network is required.
4. Check: the skill appears in Customize → Skills; when a presentation from a source is requested, it must
   use its scripts.

### Other agents compatible with Agent Skills

Gemini CLI, Cursor and GitHub Copilot use the same format. It is enough to clone the repository and link
`skills/enhanced-presentations` into the corresponding skills path.
