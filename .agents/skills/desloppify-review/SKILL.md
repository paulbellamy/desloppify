---
name: desloppify-review
description: Run subjective review only (sequential passes scoring 20 quality dimensions).
triggers: ["user"]
---

Read `./reference/shared.md` for shared context (state schema, key concepts).

Devin runs without an in-process subagent tool that shares the working directory, so the four review batches run sequentially in this same session. Read these reference files once before starting:

- `./reference/dimensions.md` (the 20 dimension definitions)
- `./reference/review-system-prompt.md` (scoring philosophy, calibration anchors, two-phase OBSERVE-then-JUDGE process)

Then work through the four batches in order. For each batch, follow the two-phase process described in `review-system-prompt.md` — OBSERVE the codebase for all dimensions in the batch first, then JUDGE all dimensions in the batch. Be thorough: read enough code (entry points, core modules, config) to form confident judgments.

## Batch Assignment

| Batch | Dimensions |
|-------|-----------|
| **Architecture** | high_level_elegance, mid_level_elegance, cross_module_architecture, package_organization, initialization_coupling |
| **Correctness** | type_safety, contract_coherence, logic_clarity, error_consistency, design_coherence |
| **Code Quality** | naming_quality, abstraction_fitness, ai_generated_debt, convention_outlier, low_level_elegance |
| **External** | dependency_health, test_strategy, api_surface_coherence, authorization_consistency, incomplete_migration |

## Per-Batch Output Format

For each batch, accumulate results in this shape:

```json
{
  "assessments": {"dimension_name": score_0_to_100},
  "findings": [
    {
      "dimension": "dimension_name",
      "identifier": "short_id",
      "summary": "One-line (< 120 chars)",
      "related_files": ["path/to/file"],
      "evidence": ["what you observed"],
      "suggestion": "concrete fix",
      "confidence": "high|medium|low"
    }
  ]
}
```

## Merge Results

After all 4 batches complete:
1. Collect assessments — merge into `dimension_scores` in state.json (one entry per dimension with `score` and `assessed_at`).
2. Collect findings — convert to work items with `"source": "review"`. Assign tiers based on confidence and scope: high confidence + multi-file = T3-T4, low confidence + single file = T1-T2.
3. Deduplicate findings by file+dimension combination.
4. Run scoring: `python ./scripts/score.py`.
5. Write updated `.desloppify/state.json`.
6. Display the status summary.
