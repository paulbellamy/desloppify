# Workflow: resolve

Mark work items as resolved. Takes a pattern argument and an optional status flag (`--fixed` | `--wontfix` | `--false-positive`; default `--fixed`).

Read `./reference/shared.md` for shared context (state schema, key concepts).

1. Read `.desloppify/state.json`.
2. Match the pattern argument against item ids, file paths, or summaries.
3. Update matched items: set `status` (honor the flag if present, otherwise `fixed`), set `resolved_at` to now (ISO timestamp).
4. If `--wontfix`: warn about the strict score impact (wontfix items count as open in the strict score).
5. Write `.desloppify/state.json`.
6. Run `python ./scripts/score.py` and show updated scores.
