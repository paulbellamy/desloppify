# Workflow: next

Show and work the next item in the triage queue.

Read `./reference/shared.md` for shared context (state schema, key concepts).

1. Read `.desloppify/state.json`.
2. If `queue` is empty, say so and suggest running the `scan` or `triage` workflow.
3. Show the top queue item (or top cluster):
   - Cluster name and thesis
   - Individual items with file, line, summary, suggestion
   - Effort estimate
4. Fix the issues in code. Prefer deleting a bad premise over adding a compensating layer — if a fix wraps, flags off, or post-processes the thing it's fixing, step back and fix the source instead.
5. After fixing, update state: set each item's `status` to `fixed`, set `resolved_at` to now (ISO timestamp).
6. Remove completed items/clusters from `queue`.
7. Run `python ./scripts/score.py` to show updated scores.
8. Move to the next item (repeat from step 2 if the user asked to keep going).
