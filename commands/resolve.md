---
description: "Mark work items as resolved."
argument-hint: "<pattern> [--fixed|--wontfix|--false-positive]"
---

Read `./reference/shared.md` for shared context (state schema, key concepts).

1. Read `.desloppify/state.json`
2. Match `$ARGUMENTS` pattern against item ids, file paths, or summaries
3. Update matched items: set status, set resolved_at
4. If --wontfix: warn about strict score impact
5. Write state.json
6. Run `python ./scripts/score.py`, show updated scores
