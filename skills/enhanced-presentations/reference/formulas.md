# Formulas and derivations

## How they are written

```html
<span class="m" data-tex="T_t = T + \fr{V^2}{2c_p}"></span>
```
On load, script block 1 converts `data-tex` into HTML (offline: STIX Two font embedded
by `new.py`; in old files, `tools/fonts.py pres.html`). If a command does not exist, the
formula comes out as "⚠ …" and `review.py` gives the error.

Sizes: `class="m l"` 40 px · `m` 34 · `m s` 30 · `m xs` 26 · `m xxs` 23 (inside `.nt`, 23 only).
`class="m res"` = the whole formula in a green box (the formula as it appears in the source).

| Input | Output | Notes |
|---|---|---|
| `a^{2}` `a_{t}` `a_{t}^{2}` | power, subscript, both | without braces only one character: `a^2` |
| `T_{\rm{s}}` | T with upright subscript "s" | subscripts that are words or labels: `\rm{}` |
| `\fr{a}{b}` | fraction | nestable |
| `\sq{a}` | root | |
| `\pa{a}` `\bk{a}` `\br{a}` | ( ) [ ] { } that stretch | plain parentheses `( )` do not stretch |
| `\md` `\dot{x}` | ṁ, ẋ | |
| `\gamma \rho \pi \varepsilon \eta \tau \omega …` | italic Greek letters | also `\partial` ∂ |
| `\Delta \Gamma \Pi \Sigma \Omega \nabla` | upright capitals | |
| `\cdot \times \approx \to \Rightarrow \iff \le \ge \ne \ll \gg \pm \equiv \propto \sim` | · × ≈ → ⇒ ⇔ ≤ ≥ ≠ ≪ ≫ ± ≡ ∝ ∼ | |
| `\int_{t_0}^{t_{bo}}` `\sum` `\prod` | ∫ ∑ ∏ | |
| `\ln \exp \sin \cos \tan \log \max` | upright functions | |
| `\ab{a}` `\ovl{a}` | absolute value, overline | |
| `\, \; \quad \qquad` | spaces | |
| `\rm{kPa}` `\tx{si}` | upright text; small normal text | units with `\,\rm{kPa}` |
| `0.5` `1.4` | numbers with a decimal point | the point between digits is decimal |
| `\bx{a}` | green box | **the formula as it appears in the source** |

Step commands (k = the same step number as `data-in`):

| Input | What it does |
|---|---|
| `\in[k]{a}` | `a` appears in step k |
| `\io[k,l]{a}` | `a` is visible from step k to l−1 |
| `\cx[k]{a}` | in step k, `a` is crossed out in red (and lightened) |
| `\cz[k]{a}` | it is crossed out and marked with a "0" (term equal to zero) |
| `\ha[r]{a}` `\hb[r]{a}` `\hc[r]{a}` | green / orange / blue background in steps r: `2`, `2-4`, `1,3-4` |
| `\ca{a}` `\cb{a}` `\cc{a}` | fixed green / orange / blue color (group terms that go together) |
| `\ub[k]{a}{label}` | underbrace below `a` with a short label (what that term means); it appears in step k (`\ub{a}{…}` always visible). The label accepts HTML: `<i>V</i>` |

**Dense formula that means several things** (e.g. a sum of terms with different origins): one `\ub`
under each term with what it represents, instead of several highlight colors without explanation. Labels of
1-4 words; they reserve their space below (the row grows).
```html
<span class="m" data-tex="F = \ub[1]{\md\,V_e}{momentum} + \ub[2]{\pa{P_e - P_a}A_e}{pressure term}"></span>
```

They do not exist (they give an error): `\phantom`, `\frac` (it is `\fr`), `\left( \right)` (it is `\pa{}`), `\mathrm` (it is `\rm`),
`\text` (it is `\tx`), `\sqrt` (it is `\sq`), `\dot m` without braces works, `\in` as "belongs to" (it is `\elem`).

**Standalone variables in the text** (no `data-tex` needed): `<span class="v">P<sub>e</sub></span>`;
upright subscript: `<sub class="r">s</sub>`. In SVG: `<text class="vr">T<tspan class="r" baseline-shift="sub" font-size="15">s</tspan></text>`.

## How a derivation is presented

Criterion: "do not put the equations in without explanation; make clear where the formulas come from,
how things are solved for, how they are crossed out…", faithful to the source. And: "do not develop
equations without knowing, from the beginning, what is being done".

0. **Before starting, what is going to be obtained and what for.** Long derivation (more than one scene):
   `objective` scene before (Boxed result · Usefulness · Procedure in 2-4 steps). Short derivation:
   `<div class="sub obj">` under the title ("Objective: express … in terms of …").
1. **Starting point**: the equation or the hypotheses from the source (first row, often with `res`).
2. **One operation per row**: substitute, simplify, solve for, multiply exponents… The note (`.nt`)
   says what has been done, in a few words: "c<sub>p</sub> = γR/(γ−1) is substituted", "R is simplified",
   "The exponents are added", "T is solved for". Bold on the key word.
3. **What is simplified is crossed out** (`\cx`), in the step after its appearance, and the note says so.
   A term equal to zero, with `\cz` and the reason in the note ("in (s) the air stops: V = 0").
4. **Highlight** with `\ha` what is going to be used in the next row, or what two rows have in common
   (same color in both). To group terms of a different nature, `\ca \cb \cc` (and say it in the note).
5. **Result**: the source formula in a green box (`\bx{}`), only the final formula (not the whole
   chain of equalities), and the main idea in `.punch`. The "formula sheet" formulas, the ones used
   in the exercises, always boxed.
6. **Concrete notes, to read row by row**: what is substituted, what is simplified and why. No
   vague notes ("operations are performed", "it is rearranged").
7. Reminders of something seen before: in the note, without citing the source ("Reminder:
   c<sub>p</sub> = γR/(γ−1)"). The reference goes only in `data-ref` (bottom right).

The intermediate steps are not literal from the source: they are noted down for the final report.

## Full example (scene with three rows and four steps)

```html
<section class="scene" id="mach" data-section="Mach number" data-ref="Slide 7">
  <h2>Relations with the Mach number</h2>
  <div class="sub obj">Express the temperature in terms of the Mach number and the total temperature</div>
  <div class="dv">
    <div class="rw up" data-in="0">
      <div class="e"><span class="lab">Mach:</span>
        <span class="m" data-tex="M = \fr{V}{a} \;\Rightarrow\; \bx{M^2 = \ha[2]{\fr{V^2}{\gamma R T}}}"></span></div>
      <div class="nt">Definition of <b>Mach number</b></div>
    </div>
    <div class="rw up" data-in="1">
      <div class="e"><span class="m" data-tex="\fr{T_t}{T} = 1 + \fr{V^2}{2c_p T} = 1 + \fr{\gamma-1}{2}\,\ha[2]{\fr{V^2}{\gamma R T}}"></span></div>
      <div class="nt"><span class="nl"><span class="v">T<sub>t</sub></span> is divided by <span class="v">T</span></span>
        <span class="nl" data-in="2">and <b><span class="v">M</span><sup>2</sup></b> appears</span></div>
    </div>
    <div class="rw up" data-in="3">
      <div class="e"><span class="m" data-tex="\bx{\fr{T}{T_t} = \pa{1 + \fr{\gamma-1}{2}M^2}^{-1}}"></span></div>
      <div class="nt">The quotient is inverted: exponent −1</div>
    </div>
  </div>
</section>
```

## Typical problems
- **Row too wide**: the formula invades the note → `review.py` gives "they overlap". Solutions: `m s`
  or `m xs`; split into two rows; `class="rw w"` (no note) and the note in the next row.
- **Subscripts that look like superscripts**: always braces in subscripts of more than one character: `T_{t0}`.
- **Formula in a table cell or in a card**: it works the same (`<span class="m xs" data-tex="…">`).
- **The green box in all rows**: no; only in the formula as the source gives it.
- If the content has no formulas, delete the "Green box" sentence from the help (`#help`).
