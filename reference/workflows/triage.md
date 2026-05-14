# Workflow: triage

Three sequential stages that analyze, cluster, and verify the work queue from scan findings. Each stage's output feeds the next.

Read `./reference/shared.md` for shared context (state schema, key concepts).

## Stage 1: Analyze

Read `.desloppify/state.json`. Analyze all `work_items` with `status` "open".

For each item:
1. Read the actual file and line referenced.
2. Verify the issue still exists in the code.
3. Assign a verdict: `genuine` | `false-positive` | `exaggerated` | `not-worth-it`.

Then identify patterns:
- Which files appear in the most items?
- Which dimensions cluster together?
- What root causes recur across items?
- Are there rework loops (items fixed then reopened)?

Produce JSON:
```json
{
  "verdicts": {"item_id": {"verdict": "genuine|false-positive|exaggerated|not-worth-it", "reason": "..."}},
  "patterns": [{"root_cause": "...", "item_ids": ["..."], "files": ["..."]}],
  "focus_dimensions": ["dim1", "dim2"],
  "false_positive_count": 0
}
```

## Stage 2: Plan

Given the Stage 1 analysis and `.desloppify/state.json`:

1. Dismiss false-positives and not-worth-its (mark for status change).
2. Cluster genuine items by root cause (NOT by dimension).
   - Name clusters by what work needs to happen, not what's wrong.
   - Each cluster should be a coherent unit of work.
3. Order clusters by: `(impact * breadth) / effort`.
4. Within clusters, order by dependency (fix A before B if B depends on A).
5. Estimate effort per cluster: `trivial` | `small` | `medium` | `large`.

Produce JSON:
```json
{
  "clusters": {
    "cluster-name": {
      "thesis": "imperative one-liner of what to do",
      "item_ids": ["id1", "id2"],
      "effort": "small",
      "depends_on": []
    }
  },
  "queue": ["cluster-name-1", "cluster-name-2"],
  "dismissed": {"item_id": "reason"}
}
```

## Stage 3: Verify

Verify the Stage 2 plan against `.desloppify/state.json` and the actual code:

1. For each cluster, check that referenced file paths exist.
2. Check no circular dependencies between clusters.
3. Verify effort estimates are realistic (read the files, assess scope).
4. Flag any items appearing in multiple clusters.
5. Flag clusters with >10 items (should they be split?).

Produce JSON:
```json
{
  "corrections": [{"cluster": "name", "issue": "description", "fix": "suggestion"}],
  "approved": true
}
```

If `approved` is false, apply the corrections by adjusting the plan from Stage 2, then re-run Stage 3 against the corrected plan.

## Apply Triage

After all three stages:
1. Update `work_item` statuses for dismissed items (`false_positive`, `wontfix`).
2. Write `clusters` and `queue` to `.desloppify/state.json`.
3. Run `python ./scripts/score.py` to update scores.
4. Display the queue summary.
