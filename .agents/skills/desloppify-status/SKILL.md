---
name: desloppify-status
description: Show current desloppify scores and progress.
triggers: ["user"]
---

Read `./reference/shared.md` for shared context (state schema, key concepts).

1. Read `.desloppify/state.json`.
2. Run `python ./scripts/score.py`.
3. Display:
   - Overall / strict / objective scores (with delta from last scan if available)
   - Per-dimension scores (subjective)
   - Open item count by source (linter vs review)
   - Wontfix debt (overall - strict gap)
   - Queue length and top 3 clusters
   - Scan history trend (last 5 scans)
