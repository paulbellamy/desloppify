# Scoring Reference

## Overall Formula

```
overall = mechanical_score * 0.25 + subjective_score * 0.75
```

- **strict**: same formula, but wontfix items count as open (penalized)
- **objective**: mechanical_score only (100% weight)

## Tier Weights

| Tier | Weight | Description |
|------|--------|-------------|
| T1   | 1      | Auto-fixable (unused imports, formatting) |
| T2   | 2      | Quick manual fix (rename, add type annotation) |
| T3   | 3      | Judgment call (refactor function, restructure module) |
| T4   | 4      | Major refactor (architectural change, rewrite subsystem) |

## Mechanical Dimensions (25% of overall)

Scored from linter findings. Each dimension: `score = 1 - (weighted_failures / potential)` where weighted_failures = sum of tier weights for open items.

| Dimension    | Weight | Detectors |
|-------------|--------|-----------|
| file health  | 2.0    | smells, concerns |
| code quality | 1.0    | complexity, unused |
| duplication  | 1.0    | duplicates |
| test health  | 1.0    | test_coverage |
| security     | 1.0    | security, bandit |

Mechanical score = weighted average of dimension scores.

## Subjective Dimensions (75% of overall)

Direct 0-100 scores from review assessments.

| Dimension         | Weight | Maps from |
|-------------------|--------|-----------|
| high elegance     | 22.0   | high_level_elegance |
| mid elegance      | 22.0   | mid_level_elegance |
| low elegance      | 12.0   | low_level_elegance |
| contracts         | 12.0   | contract_coherence |
| type safety       | 12.0   | type_safety |
| abstraction fit   | 8.0    | abstraction_fitness |
| logic clarity     | 6.0    | logic_clarity |
| structure nav     | 5.0    | package_organization + cross_module_architecture |
| error consistency | 3.0    | error_consistency |
| naming quality    | 2.0    | naming_quality |
| ai generated debt | 4.0    | ai_generated_debt |
| test strategy     | 4.0    | test_strategy |
| design coherence  | 10.0   | design_coherence |
| init coupling     | 1.0    | initialization_coupling |
| convention drift  | 1.0    | convention_outlier |
| dep health        | 1.0    | dependency_health |
| api coherence     | 1.0    | api_surface_coherence |
| auth consistency  | 1.0    | authorization_consistency |
| stale migration   | 1.0    | incomplete_migration |

Subjective score = weighted average of assessed dimension scores (0-100 each). Every assessed dimension counts: one missing from the table above still scores under its own name at the default weight of 1.0 (upstream desloppify semantics — dimensions are never silently dropped).

Dimensions not yet assessed are excluded from the average (weight redistributed). This means subjective score starts undefined until first review.

## Confidence Weights

Applied to finding severity when computing mechanical scores:
- high: 1.0
- medium: 0.7
- low: 0.3

## Strict Score

Same formula, but items with status "wontfix" are treated as "open" (they count as failures). This penalizes dismissing issues without fixing them. The gap between overall and strict is your wontfix debt.
