---
name: desloppify-scan
description: Run full codebase quality scan (linters + subjective review), persist state, compute scores.
triggers: ["user"]
---

Read `./reference/shared.md` for shared context (state schema, key concepts).

If `.desloppify/state.json` does not exist, initialize it:

```bash
mkdir -p .desloppify && echo '{"version":1,"work_items":{},"dimension_scores":{},"queue":[],"clusters":{},"scan_history":[]}' > .desloppify/state.json
```

## Step 1: Detect Languages and Run Linters

Detect which languages exist (use `find` or your file-search tool for file extensions), then run every available linter. Use `command -v <tool> >/dev/null 2>&1` to check availability. Skip gracefully if missing.

**Python:**
```bash
ruff check . --output-format json 2>/dev/null
python -m bandit -r . -f json 2>/dev/null
python -m pylint --output-format=json . 2>/dev/null
```

**JavaScript/TypeScript:**
```bash
npx eslint . --format json 2>/dev/null
npx knip --reporter json 2>/dev/null
npx tsc --noEmit 2>&1
```

**Go:**
```bash
go vet ./... 2>&1
staticcheck ./... 2>/dev/null
golangci-lint run --out-format json 2>/dev/null
```

**Rust:**
```bash
cargo clippy --message-format json 2>/dev/null
```

**Ruby:**
```bash
rubocop --format json 2>/dev/null
brakeman -f json -q 2>/dev/null
```

**General:**
```bash
shellcheck **/*.sh 2>/dev/null
hadolint Dockerfile 2>/dev/null
```

Parse each linter's JSON output. Convert findings to work items:
```json
{
  "id": "<hash of detector+file+line+summary>",
  "source": "linter",
  "detector": "<tool_name>",
  "dimension": "<mechanical dimension: file health|code quality|duplication|test health|security>",
  "file": "<relative path>",
  "line": 0,
  "tier": 2,
  "confidence": "high",
  "summary": "<linter message>",
  "suggestion": "<fix recommendation>",
  "status": "open",
  "first_seen": "<ISO timestamp>"
}
```

Tier assignment: security findings = T3, unused imports = T1, complexity = T2, style smells = T1, test gaps = T2, architectural = T4.

## Step 2: Read Codebase

Map the project structure (use `find`, `ls`, or your file-listing tool). Read key files (entry points, config, main modules) to build understanding. This context feeds the review passes in Step 3.

## Step 3: Subjective Review (4 sequential passes)

Devin runs without an in-process subagent tool that shares the working directory, so the four review batches run sequentially in this same session. Read these reference files once before starting:

- `./reference/dimensions.md` (the 20 dimension definitions)
- `./reference/review-system-prompt.md` (scoring philosophy, calibration anchors, two-phase OBSERVE-then-JUDGE process)

Then work through the four batches in order. For each batch, follow the two-phase process described in `review-system-prompt.md` — OBSERVE the codebase for all dimensions in the batch first, then JUDGE all dimensions in the batch. Be thorough: read enough code to form confident judgments.

### Batch Assignment

| Batch | Dimensions |
|-------|-----------|
| **Architecture** | high_level_elegance, mid_level_elegance, cross_module_architecture, package_organization, initialization_coupling |
| **Correctness** | type_safety, contract_coherence, logic_clarity, error_consistency, design_coherence |
| **Code Quality** | naming_quality, abstraction_fitness, ai_generated_debt, convention_outlier, low_level_elegance |
| **External** | dependency_health, test_strategy, api_surface_coherence, authorization_consistency, incomplete_migration |

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

### Merge Results

After all 4 batches complete:
1. Collect assessments — merge into `dimension_scores` in state.json (one entry per dimension with `score` and `assessed_at`).
2. Collect findings — convert to work items with `"source": "review"`. Assign tiers based on confidence and scope: high confidence + multi-file = T3-T4, low confidence + single file = T1-T2.
3. Deduplicate findings by file+dimension combination.

## Step 4: Merge and Score

1. Read existing `.desloppify/state.json`.
2. Merge new linter findings: match by id, update existing, add new, auto-resolve items no longer found (set `status` to `auto_resolved` and `resolved_at` to now).
3. Merge review assessments into `dimension_scores`.
4. Run scoring: `python ./scripts/score.py`.
5. Append a record to `scan_history` with the date, overall score, strict score, and open item count.
6. Write updated `.desloppify/state.json`.
7. Display the status summary (overall / strict / objective, top open items, top clusters if any).
