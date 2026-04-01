---
description: Run subjective review only (4 parallel subagents scoring 20 quality dimensions).
---

Read `./reference/shared.md` for shared context (state schema, key concepts).

Launch 4 parallel subagents. Each reads `./reference/dimensions.md` and `./reference/review-system-prompt.md`, explores the codebase, and scores its assigned dimensions.

## Batch Assignment

| Batch | Dimensions |
|-------|-----------|
| **Architecture** | high_level_elegance, mid_level_elegance, cross_module_architecture, package_organization, initialization_coupling |
| **Correctness** | type_safety, contract_coherence, logic_clarity, error_consistency, design_coherence |
| **Code Quality** | naming_quality, abstraction_fitness, ai_generated_debt, convention_outlier, low_level_elegance |
| **External** | dependency_health, test_strategy, api_surface_coherence, authorization_consistency, incomplete_migration |

## Subagent Prompt Template

For each batch, launch an Agent with `subagent_type: "general-purpose"`:

```
You are a code quality reviewer for the {batch_name} batch.

Read these reference files first:
- ./reference/dimensions.md (find your assigned dimensions)
- ./reference/review-system-prompt.md (scoring philosophy and rules)

You are reviewing the codebase at: {cwd}
Score these dimensions: {dimension_list}

Instructions:
1. Use Glob to understand project structure
2. Read key files — entry points, core modules, config
3. Follow the two-phase process: OBSERVE all dimensions first, then JUDGE all
4. Be thorough — read enough code to form confident judgments
5. Return your results as a single JSON block:

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

After all 4 subagents complete:
1. Collect assessments from each — merge into `dimension_scores` in state.json
2. Collect findings — convert to work items with `"source": "review"`, assign tiers based on confidence and scope (high confidence + multi-file = T3-T4, low confidence + single file = T1-T2)
3. Deduplicate findings by file+dimension combination
4. Run scoring: `python ./scripts/score.py`
5. Write updated state.json
6. Display status summary
