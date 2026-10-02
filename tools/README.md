# Maintenance

This directory contains the maintenance tools that are **not distributed** with the installed skill: the
packager.

**Requirements:** python3 (standard library).

## Packaging for the Claude app

```bash
python3 tools/package.py   # generates dist/enhanced-presentations.skill
```

The package includes the complete skill (including the formula fonts) and the license files (`LICENSE`,
`NOTICE.md` and `OFL.txt`). It is uploaded from claude.ai → Customize → Skills → "Upload a skill".

## Checks

Before packaging, with a real presentation:

```bash
python3 skills/enhanced-presentations/tools/review.py <pres.html>   # must end in OK
```

The repository CI generates a test presentation, inserts a component and packages the skill.
