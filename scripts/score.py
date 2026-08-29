#!/usr/bin/env python3
"""Compute desloppify scores from state.json. No external dependencies."""

import json
import sys
from pathlib import Path

MECHANICAL_WEIGHTS = {
    "file health": 2.0,
    "code quality": 1.0,
    "duplication": 1.0,
    "test health": 1.0,
    "security": 1.0,
}

SUBJECTIVE_WEIGHTS = {
    "high elegance": 22.0,
    "mid elegance": 22.0,
    "low elegance": 12.0,
    "contracts": 12.0,
    "type safety": 12.0,
    "abstraction fit": 8.0,
    "logic clarity": 6.0,
    "structure nav": 5.0,
    "error consistency": 3.0,
    "naming quality": 2.0,
    "ai generated debt": 4.0,
    "test strategy": 4.0,
    "design coherence": 10.0,
}

# Maps review dimension names to subjective scoring dimension names
DIMENSION_MAP = {
    "high_level_elegance": "high elegance",
    "mid_level_elegance": "mid elegance",
    "low_level_elegance": "low elegance",
    "contract_coherence": "contracts",
    "type_safety": "type safety",
    "abstraction_fitness": "abstraction fit",
    "logic_clarity": "logic clarity",
    "package_organization": "structure nav",
    "cross_module_architecture": "structure nav",
    "error_consistency": "error consistency",
    "naming_quality": "naming quality",
    "ai_generated_debt": "ai generated debt",
    "test_strategy": "test strategy",
    "design_coherence": "design coherence",
}

# Maps linter source categories to mechanical dimensions
MECHANICAL_MAP = {
    "smell": "file health",
    "unused": "code quality",
    "complexity": "code quality",
    "duplicate": "duplication",
    "test": "test health",
    "security": "security",
}

TIER_WEIGHTS = {1: 1, 2: 2, 3: 3, 4: 4}
CONFIDENCE_WEIGHTS = {"high": 1.0, "medium": 0.7, "low": 0.3}
LENIENT_OPEN = {"open", "deferred"}
STRICT_OPEN = {"open", "wontfix", "deferred"}


def compute_mechanical(items, open_statuses):
    """Compute mechanical dimension scores from linter work items."""
    dim_failures = {d: 0.0 for d in MECHANICAL_WEIGHTS}
    dim_potential = {d: 0.0 for d in MECHANICAL_WEIGHTS}

    for item in items:
        if item.get("source") != "linter":
            continue
        dim_name = item.get("dimension", "")
        # Try direct match first, then category-based mapping
        mech_dim = None
        if dim_name in MECHANICAL_WEIGHTS:
            mech_dim = dim_name
        else:
            for prefix, mapped in MECHANICAL_MAP.items():
                if dim_name.startswith(prefix) or item.get("detector", "").startswith(prefix):
                    mech_dim = mapped
                    break
        if not mech_dim or mech_dim not in MECHANICAL_WEIGHTS:
            continue

        tier = item.get("tier", 3)
        conf = CONFIDENCE_WEIGHTS.get(item.get("confidence", "medium"), 0.7)
        weight = TIER_WEIGHTS.get(tier, 3) * conf
        dim_potential[mech_dim] += weight

        if item.get("status", "open") in open_statuses:
            dim_failures[mech_dim] += weight

    scores = {}
    total_weight = 0.0
    total_score = 0.0
    for dim, w in MECHANICAL_WEIGHTS.items():
        pot = dim_potential[dim]
        if pot > 0:
            s = max(0.0, 1.0 - dim_failures[dim] / pot) * 100
        else:
            s = 100.0  # No findings = perfect
        scores[dim] = round(s, 1)
        total_weight += w
        total_score += s * w

    overall = round(total_score / total_weight, 1) if total_weight > 0 else 100.0
    return overall, scores


def compute_subjective(dimension_scores):
    """Compute subjective score from dimension assessments."""
    total_weight = 0.0
    total_score = 0.0
    scores = {}

    for review_dim, subj_dim in DIMENSION_MAP.items():
        if review_dim in dimension_scores:
            entry = dimension_scores[review_dim]
            s = entry.get("score", 0) if isinstance(entry, dict) else float(entry)
            w = SUBJECTIVE_WEIGHTS.get(subj_dim, 1.0)
            # Average if multiple review dims map to same subjective dim
            if subj_dim in scores:
                scores[subj_dim] = (scores[subj_dim] + s) / 2
            else:
                scores[subj_dim] = s

    for dim, s in scores.items():
        w = SUBJECTIVE_WEIGHTS.get(dim, 1.0)
        total_weight += w
        total_score += s * w

    overall = round(total_score / total_weight, 1) if total_weight > 0 else None
    return overall, {k: round(v, 1) for k, v in scores.items()}


def main():
    state_path = Path(".desloppify/state.json")
    if not state_path.exists():
        print(json.dumps({"error": "No .desloppify/state.json found"}))
        sys.exit(1)

    state = json.loads(state_path.read_text())
    items = list(state.get("work_items", {}).values())
    dim_scores = state.get("dimension_scores", {})

    # Lenient scores (overall)
    mech_lenient, mech_dims_lenient = compute_mechanical(items, LENIENT_OPEN)
    subj_score, subj_dims = compute_subjective(dim_scores)

    # Strict scores
    mech_strict, mech_dims_strict = compute_mechanical(items, STRICT_OPEN)

    if subj_score is not None:
        overall = round(mech_lenient * 0.25 + subj_score * 0.75, 1)
        strict = round(mech_strict * 0.25 + subj_score * 0.75, 1)
    else:
        overall = mech_lenient
        strict = mech_strict

    result = {
        "overall": overall,
        "strict": strict,
        "objective": mech_lenient,
        "mechanical_dimensions": mech_dims_lenient,
        "subjective_dimensions": subj_dims,
        "subjective_assessed": subj_score is not None,
        "open_items": sum(1 for i in items if i.get("status") in LENIENT_OPEN),
        "total_items": len(items),
        "wontfix_items": sum(1 for i in items if i.get("status") == "wontfix"),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
