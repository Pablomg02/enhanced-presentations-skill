#!/usr/bin/env python3
"""Prepare the version to upload to the Claude app (claude.ai): creates dist/enhanced-presentations.skill.

The package contains the whole skill (SKILL.md, template.html, tools/ with the formula fonts
and reference/), plus LICENSE, NOTICE.md and OFL.txt. The app accepts up to 30 MB uncompressed; this package
is under 1 MB. Run it after every change.
"""
import sys, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "enhanced-presentations"
MAX_BYTES = 30_000_000

if not (SKILL / "SKILL.md").is_file():
    sys.exit(f"Skill not found in {SKILL}")

files = {}
for p in sorted(SKILL.rglob("*")):
    if p.is_file() and "__pycache__" not in p.parts:
        files[str(p.relative_to(SKILL))] = p.read_bytes()
for n in ("LICENSE", "NOTICE.md", "OFL.txt"):
    if (REPO / n).is_file():
        files[n] = (REPO / n).read_bytes()

total = sum(len(v) for v in files.values())
paths = [k for k, v in files.items() if str(REPO).encode() in v]
if paths:
    sys.exit("There are absolute paths from your computer in: " + ", ".join(paths))
if total > MAX_BYTES:
    sys.exit(f"The package exceeds the app limit ({MAX_BYTES / 1e6:.0f} MB uncompressed)")
out = REPO / "dist" / f"{SKILL.name}.skill"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for k, v in sorted(files.items()):
        z.writestr(f"{SKILL.name}/{k}", v)
print(f"{len(files)} files, {total / 1e6:.1f} MB uncompressed")
print(f"Done: {out} ({out.stat().st_size / 1e6:.1f} MB compressed). Upload it at claude.ai → Customize → Skills → \"Upload a skill\".")
