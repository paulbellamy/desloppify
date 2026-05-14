---
name: desloppify-resolve
description: Mark work items as resolved.
argument-hint: "<pattern> [--fixed|--wontfix|--false-positive]"
triggers: ["user"]
---

Read `./reference/shared.md` for shared context (state schema, key concepts).

1. Read `.desloppify/state.json`.
2. Match the user's pattern argument against item ids, file paths, or summaries.
3. Update matched items: set `status` (default `fixed`; honor `--fixed`, `--wontfix`, or `--false-positive` flags if present), set `resolved_at` to now (ISO timestamp).
4. If `--wontfix`: warn about the strict score impact (wontfix items count as open in the strict score).
5. Write `.desloppify/state.json`.
6. Run `python ./scripts/score.py` and show updated scores.
