# SVG diagrams

The value of the HTML lies in redrawing the source diagrams, cleaner and assembled by steps.
They are drawn by hand in SVG with the template classes; here are the rules and tested pieces.

The pieces in this document are **examples** from a specific domain (fluid and machine systems):
they serve as a pattern. Adapt the shapes and colors to the content of each presentation (section 3 of
`SKILL.md`).

## Rules

1. **1:1 scale**: the on-screen size of the `<svg>` equal to its `viewBox`, so the font sizes are
   the real ones:
   `<svg class="fig sk" style="left:80px;top:190px;width:1440px;height:520px" viewBox="0 0 1440 520" aria-label="What it is">`.
   Inside `.split`, `.cols2` or `.cards` the SVG takes the width of its slot: choose the `viewBox` with that
   width (560 in `.split`, 640 in `.cols2`).
2. **First draw on paper**: place the pieces on a grid (x from 0 to width, y downward)
   and note their coordinates before writing. Leave ≥ 30 px between pieces and ≥ 40 px of margin.
3. **Drawing order** (the last one stays on top): pipes `.pp` → flows `.fl` → pieces → flames and
   jets → labels → highlights.
4. **Labels**: `class="lb"` (19 px) or `class="lm"` (16 px, secondary); centered with
   `text-anchor="middle"` below or above the piece; if they do not fit, to one side with a `.ld` callout.
   Never on top of a line or another label (`review.py` detects overlapping texts, but not texts
   on top of lines: check it in the screenshot). Label over a background with a drawing: `style="paint-order:stroke;stroke:#fff;stroke-width:6px"`.
5. **Steps**: wrap in `<g data-in="k">` what enters together; `data-out` for what is no longer needed afterwards.
6. **Semantic colors** (always the same): fuel `tk-fu` / `fl fu` (red), oxidizer
   `tk-ox` / `fl ox` (blue), gas or pressurant `tk-gs` / `fl gs` (gray), hot gas `fl hg` (green),
   electrical `fl el`, flame `.flame` / `--warm`, highlights `.hl` (green). Black for the pieces.
7. **Animate only what explains**: flow direction (`.fl`), engine on (flame, `.glow`, jet
   `.pf`), something that runs out (`.once` + `.drain` / `.stop` with `data-go`), something that alternates (`.alt`).
8. Source figure too complex to redraw (photo, real cutaway, map): use the photo
   (`images.py`) and draw only the callouts on top.

## Stroke classes

| Class | What |
|---|---|
| `cp` | piece: white fill, black 2.2 stroke |
| `ln` | black line without fill |
| `ld` | thin gray callout line |
| `dh` | gray dashed line (planes, levels, stations) |
| `ax` | axis · `axl` symmetry axis (dash-dot) · `dimline` dimension line |
| `wall` | thick wall · `hat` hatched wall (`fill:url(#hatch)`) |
| `pp` | pipe (light gray, 10 px) · `fl` animated flow on top (same `d`) |
| `hl` | green highlight box · `dot` green dot |
| `jet` | jet area (flame color, semi-transparent) |
| `grain` | solid propellant grain |
| `lb` `lm` `vr` | label 19 · secondary 16 · italic variable 22 |

Arrows: `marker-end="url(#mk-g)"` green (thrust, key idea), `mk-k` gray, `mk-i` black (velocity),
`mk-f` red, `mk-o` blue, `mk-h` light green. Example:
`<line x1="980" y1="470" x2="760" y2="470" stroke="#4f7d1e" stroke-width="4" marker-end="url(#mk-g)"/>`.

## Pieces (place with `transform="translate(x y)"`)

```html
<!-- Tank (origin: top-left corner). tk-fu fuel · tk-ox oxidizer · tk-gs gas -->
<g transform="translate(40 40)"><rect class="tk-fu" width="120" height="160" rx="18"/>
  <text x="60" y="86" text-anchor="middle" style="font-size:20px;fill:#c0392b">RP-1</text>
  <text class="lb" x="60" y="190" text-anchor="middle">Fuel</text></g>

<!-- Pressurized gas bottle (origin: center) -->
<g transform="translate(420 110)"><circle class="tk-gs" r="52"/>
  <text y="7" text-anchor="middle" style="font-size:20px">He</text>
  <text class="lb" y="84" text-anchor="middle">Pressurant</text></g>

<!-- Pipe with flow + valve (valve origin: its center, on the horizontal pipe;
     on a vertical pipe: translate(x y) rotate(90)) -->
<path class="pp" d="M520 110 H700"/><path class="fl ox" d="M520 110 H700"/>
<g transform="translate(610 110)"><path class="cp" d="M-16 -14 L16 14 V-14 L-16 14 Z"/></g>

<!-- Filter (origin: corner) · manometer (origin: center) · regulator / shut-off valve: rect cp 32×32 -->
<g transform="translate(760 94)"><rect width="32" height="32" fill="url(#check)" stroke="#1f1f1f" stroke-width="2.2"/></g>
<g transform="translate(860 110)"><circle class="cp" r="18"/><text y="7" text-anchor="middle" style="font-size:18px">P</text></g>

<!-- Turbopump: turbine on top, shaft, pump below (origin: center of the pump) -->
<g transform="translate(1040 150)">
  <line class="ln" x1="0" y1="-80" x2="0" y2="-28" style="stroke-width:4"/>
  <path class="cp" d="M-24 -118 L24 -106 V-82 L-24 -70 Z"/>
  <circle class="cp" r="28"/><text y="7" text-anchor="middle" style="font-size:20px">B</text>
  <text class="lb" x="34" y="-88">Turbine</text><text class="lb" x="36" y="6">Pump</text></g>

<!-- Injector plate (origin: top-left corner) -->
<g transform="translate(1220 70)"><rect class="cp" width="20" height="120"/>
  <path class="ln" d="M20 30 h24 M20 60 h24 M20 90 h24" style="stroke-width:2"/></g>

<!-- Chamber + horizontal nozzle, lit (origin: center of the left face of the chamber).
     The flame, the glow and the jet go in a <g data-in="k"> if ignition is a step. -->
<g transform="translate(60 400)">
  <path class="cp" d="M0 -60 H140 L190 -20 L340 -90 V90 L190 20 L140 60 H0 Z"/>
  <rect class="glow" x="8" y="-50" width="124" height="100" fill="#f4bf7f"/>
  <path class="flame h" d="M340 -84 Q520 0 340 84 Z"/>
  <g class="pf" style="--dx:170px;--dy:0px"><circle cx="350" r="9"/>
    <circle cx="350" cy="-16" r="6" style="animation-delay:-.3s"/><circle cx="350" cy="16" r="7" style="animation-delay:-.6s"/></g>
  <line x1="260" y1="140" x2="60" y2="140" stroke="#4f7d1e" stroke-width="4" marker-end="url(#mk-g)"/>
  <text class="lb" x="280" y="147">Thrust</text></g>

<!-- Solid motor in cutaway (origin: top-left corner of the casing) -->
<g transform="translate(700 320)">
  <rect class="cp" width="360" height="160" rx="10"/>
  <rect class="grain" x="10" y="10" width="330" height="140"/>
  <rect x="10" y="66" width="330" height="28" fill="#fff" stroke="#b9a887" stroke-width="1.5"/>
  <path class="cp" d="M360 50 L420 20 V140 L360 110 Z"/>
  <text class="lb" x="180" y="190" text-anchor="middle">Propellant grain</text></g>

<!-- Label with callout (origin: the pointed-at point) -->
<g transform="translate(1180 360)"><circle class="dot" r="6"/><path class="ld" d="M0 0 L60 -60 H120"/>
  <text class="lb" x="66" y="-68">Label with callout</text></g>

<!-- Nozzle with smooth profile and hatched wall (drawn by the FIGURES block; see charts.md) -->
<g class="noz" data-noz="1120 1400 560 60 24 70 1180 1260 1"></g>
```

Vertical flame (rocket standing up, nozzle below): `<path class="flame" d="M246 468 Q280 590 314 468 Z"/>`
(grows downward from y = 468) and jet `<g class="pf" style="--dy:130px">…</g>`.

## Ready-made animations

| What | How |
|---|---|
| Flow through a pipe | `<path class="pp" d="…"/><path class="fl fu" d="…"/>` (same `d`) |
| Engine on | `.glow` in the chamber + `.flame` / `.flame h` + jet `.pf` |
| Tank that empties and engine that shuts down | `<g class="once" data-go="3"><rect class="drain" …/></g>` and the flame inside `<g class="once" data-go="3"><g class="stop">…</g></g>` |
| Valve that opens and closes in a loop | `<g class="alt"><g class="fa">open…</g><g class="fb">closed…</g></g>` |
| Particle that travels along a straight path | `<circle class="part" cx="…" cy="…" r="6" style="--dx:400px;--t:3s"/>` (`.part.slows`: arrives slowing down) |
| Highlight a piece in some steps | `<g data-in="2" data-out="3"><rect class="hl" …/></g>` or `<g class="hlg" data-hl="2-3">` |

Elements that animate their opacity (`.glow`, `.stop`, `.alt .fa/.fb`) cannot carry `data-in`:
wrap them in `<g data-in="k">`.

Check an animation with a mid-point end: `AT=1500 screenshots.sh theme.html 8` (by default, 7500 ms = final state).
