# Workflow: review

Subjective review across the 20 quality dimensions, organized into 4 batches.

Read `./reference/shared.md` for shared context (state schema, key concepts).

## Batch Assignment

| Batch | Dimensions |
|-------|-----------|
| **Architecture** | high_level_elegance, mid_level_elegance, cross_module_architecture, package_organization, initialization_coupling |
| **Correctness** | type_safety, contract_coherence, logic_clarity, error_consistency, design_coherence |
| **Code Quality** | naming_quality, abstraction_fitness, ai_generated_debt, convention_outlier, low_level_elegance |
| **External** | dependency_health, test_strategy, api_surface_coherence, authorization_consistency, incomplete_migration |

## Per-Batch Instructions

For each batch, the reviewer must:

1. Read `./reference/dimensions.md` to find the assigned dimensions' definitions.
2. Read `./reference/review-system-prompt.md` for scoring philosophy and calibration anchors.
3. Map project structure and read key files (entry points, core modules, config).
4. Follow the two-phase process from `review-system-prompt.md`: **OBSERVE** all dimensions in the batch first, then **JUDGE** all dimensions in the batch.
5. Be thorough — read enough code to form confident judgments.
6. Return results as a single JSON block:

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

## Execution Style

The runtime wrapper that invoked this workflow specifies whether the 4 batches run **in parallel** (via subagents that share the working directory) or **sequentially** (in the same session). Either way, all 4 batches must complete before merging.

## Merge Results

After all 4 batches complete:

1. Collect assessments — merge into `dimension_scores` in state.json (one entry per dimension with `score` and `assessed_at`).
2. Collect findings — convert to work items with `"source": "review"`. Assign tiers based on confidence and scope: high confidence + multi-file = T3-T4, low confidence + single file = T1-T2.
3. Deduplicate findings by file+dimension combination.
4. Run scoring: `python ./scripts/score.py`.
5. Write updated `.desloppify/state.json`.
6. Display the status summary.
