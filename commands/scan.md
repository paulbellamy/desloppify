---
description: Run full codebase quality scan (linters + subjective review), persist state, compute scores.
---

Read `./reference/shared.md` for shared context (state schema, key concepts).

## Step 1: Detect Languages and Run Linters

Detect which languages exist (Glob for file extensions), then run every available linter. Use `command -v <tool> >/dev/null 2>&1` to check availability. Skip gracefully if missing.

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

Use Glob to map the project structure. Read key files (entry points, config, main modules) to build understanding. This context feeds the review subagents.

## Step 3: Subjective Review (parallel subagents)

Launch 4 subagents in parallel via the Agent tool. Each reviews a themed batch of dimensions. See the [review command](#) for details on batch assignment and subagent prompts — or invoke `/desloppify:review` inline.

### Batch Assignment

| Batch | Dimensions |
|-------|-----------|
| **Architecture** | high_level_elegance, mid_level_elegance, cross_module_architecture, package_organization, initialization_coupling |
| **Correctness** | type_safety, contract_coherence, logic_clarity, error_consistency, design_coherence |
| **Code Quality** | naming_quality, abstraction_fitness, ai_generated_debt, convention_outlier, low_level_elegance |
| **External** | dependency_health, test_strategy, api_surface_coherence, authorization_consistency, incomplete_migration |

### Subagent Prompt Template

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

### Merge Results

After all 4 subagents complete:
1. Collect assessments from each — merge into `dimension_scores` in state.json
2. Collect findings — convert to work items with `"source": "review"`, assign tiers based on confidence and scope (high confidence + multi-file = T3-T4, low confidence + single file = T1-T2)
3. Deduplicate findings by file+dimension combination

## Step 4: Merge and Score

1. Read existing `.desloppify/state.json` if it exists
2. Merge new linter findings: match by id, update existing, add new, auto-resolve items no longer found
3. Merge review assessments into `dimension_scores`
4. Run scoring: `python ./scripts/score.py`
5. Append to `scan_history`
6. Write updated state.json
7. Display status summary
