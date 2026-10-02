# Presentation style

Style rules of the skill, valid for any source (presentation, document or text). `review.py`
automatically checks what is marked with ⚙ (section "Style" and acronyms of its output).

Philosophy: attendees want to see the formulas they are going to have to use, understand where they come
from and what they are for. The presentation is more explanatory than the source, **without lengthening it** and **without changing the order** of the
source unless it is necessary to tell it better. If the source is a presentation, its accent (and, if
requested, its typography) is adopted with `theme.py`, but the conventions of this guide and the semantic
colors do not change.

## 1. Say beforehand what is going to be done

- **Introduction**: what will be seen and why it matters (not just a list of parts).
- **After the scene that presents each part**: "Preview: toolbox for Part N" (component
  `toolbox`): the formulas that are going to be obtained and what they are for.
- **Before a long derivation**: `objective` scene (Result boxed · Usefulness · Procedure
  in 2-4 steps). In short ones, one `<div class="sub obj">` line under the title. ⚙
- **Before solving an example**: `approach` scene with the formulas boxed just as in the
  theory, which unknown each one gives and why it can be used.
- **At the end of a part**: "Recap: toolbox" (component `toolbox`).

## 2. Explain step by step

- One operation per row; the note on the right (green line) must be **specific**: what is substituted, what is
  simplified and why. It must be possible to read it row by row.

  | Bad | Good |
  |---|---|
  | "It is operated" | "c<sub>p</sub> = γR/(γ−1) is substituted and R is simplified" |
  | "Useful relation" | "It links T and P between the chamber (1) and the exit (2) because the expansion is isentropic" |

- Dense formula with several meanings: bracket with a label under each term (`\ub[k]{…}{…}`) instead of
  several highlight colors with no explanation.
- Charts whose curves appear click by click: a brief sentence that explains each curve and is replaced by the
  next one (`data-in="k" data-out="k+1"`). Say what is represented; legible axes, no cryptic formulas.

## 3. Mark what matters

- The formula as it appears in the source, and every "formula-sheet" formula, in a green box (`\bx{}`, `.res`).
  Only the final formula: do not repeat the whole chain of equalities in the box.
- Bold only on the key word (one or two per point).

## 4. Practice in blue

- Statement, approach and solution of examples and exercises: `class="scene pr"`. ⚙
- Titles "Example: …", "Approach: …", "Solution: …"; never "Application: …". ⚙

## 5. Register: academic, serious and impersonal ⚙

| Bad | Good |
|---|---|
| "We are going to solve for T", "I solve for", "I substitute", "we know that" | "T is solved for", "is substituted", "it is known that" |
| "We assume isentropic flow" (even if the source says so) | "Isentropic flow is considered" |
| "What is this about…?", "Why it matters", "comes out", "goes away", "does not matter" | "Objective:", "Relevance:", "is obtained", "cancels out", "is irrelevant" |

- Short sentences. No em dash (—) as punctuation. ⚙
- Number and unit with a non-breaking space (`1.5&nbsp;MN`); decimal point. ⚙

## 6. Titles that say what is done ⚙

| Bad | Good |
|---|---|
| "From thrust to the rocket" | "Thrust and the rocket equation" |
| "From the desired pressure to the contour" | "Nozzle design from the pressure distribution" |
| "Nozzle designed → flow" | "Flow in an already designed nozzle" |

## 7. Source references only at the bottom right ⚙

- Never "slide 3", "p. 12", "as in the slide…" in the text, nor in the toolboxes. Attendees do not have to
  go to the source to understand it. The reference goes in `data-ref` / `data-refs`
  ("Slide 3", "PDF p. 12", "Document · 3.2").
- The source is not cited in the recap scenes either.

## 8. Acronyms at the top right ⚙

- Each scene that uses acronyms or abbreviated subscripts (MFP, C-D, PL, bo, sp…) explains them with
  `data-acronyms`; not proper names or organizations (NASA, ESA…). Format:
  `data-acronyms="<b>MFP</b>: <i>Mass Flow Parameter</i> (mass flow parameter) · <b>C-D</b>: convergent-divergent"`.

## 9. Everything must fit ⚙

- Nothing goes outside its box, the canvas or the safe area; nothing steps on the footer, the closing line or the acronyms;
  no line of a diagram crosses a label. `review.py` flags it; if something does not fit, **it is fixed by
  hand** (split into steps or scenes, `.s`/`.xs`, move): there is no automatic adjustment. `?debug` in the URL
  marks overflowing boxes in red and draws the safe area.
- Even when `review.py` reports `OK`, look at the screenshots: only there can it be seen whether a diagram is understood.
