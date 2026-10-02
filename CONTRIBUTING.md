# How to contribute

The most useful contributions are reports of presentations that fail (an unreadable diagram, an overlap not
detected by `review.py`, an ambiguous instruction) and improvements to the template or the guides.

## Reporting a problem

Open an issue with the **[Problem with a presentation](.github/ISSUE_TEMPLATE/bug_report.yml)** template,
stating which source was used, what was requested and what went wrong. If possible, attach a screenshot of the
problematic step (`screenshots.sh`) and the output of `review.py`.

## Proposing an improvement

1. If the proposal affects the template or the tools, test it with a real presentation:
   `python3 skills/enhanced-presentations/tools/review.py <pres.html>` must end in `OK`.
2. If it affects the instructions (`SKILL.md` or `reference/`), keep the tone and format of the sections.
3. Package before finishing: `python3 tools/package.py`.

## Adapting to another style or subject

The structure is general. If the source is a presentation, `skills/enhanced-presentations/tools/theme.py` adopts its palette (and its
typography, with `--fonts`, for PPTX/ODP; on a PDF it applies only the palette and warns) in the generated HTML. For a custom style, modify `template.html` (colors,
typography, brand) and `reference/style.md`; the thematic examples in `reference/diagrams.md` and
`charts.md` are patterns that adapt to the content, not a closed catalog.

For questions or help with adaptation: [pablomagarinos.es](https://pablomagarinos.es).
