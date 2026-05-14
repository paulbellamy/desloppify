# Workflow: scan

Full codebase quality scan — runs linters, performs the subjective review across all 20 dimensions, persists state, and computes scores.

Read `./reference/shared.md` for shared context (state schema, key concepts).

If `.desloppify/state.json` does not exist, initialize it:

```bash
mkdir -p .desloppify && echo '{"version":1,"work_items":{},"dimension_scores":{},"queue":[],"clusters":{},"scan_history":[]}' > .desloppify/state.json
```

## Step 1: Detect Languages and Run Linters

Detect which languages exist in the repo (look for file extensions), then run every available linter. Use `command -v <tool> >/dev/null 2>&1` to check availability. Skip gracefully if missing.

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

Map the project structure. Read key files (entry points, config, main modules) to build understanding. This context feeds the subjective review in Step 3.

## Step 3: Subjective Review

Follow `./reference/workflows/review.md` to run the 4 review batches and produce assessments + findings. **The execution style (parallel subagents vs sequential passes) is specified by the runtime wrapper that invoked this workflow.**

## Step 4: Merge and Score

1. Read existing `.desloppify/state.json`.
2. Merge new linter findings: match by id, update existing, add new, auto-resolve items no longer found (set `status` to `auto_resolved` and `resolved_at` to now).
3. Merge review assessments into `dimension_scores` (one entry per dimension with `score` and `assessed_at`).
4. Convert review findings to work items with `"source": "review"`. Assign tiers based on confidence and scope: high confidence + multi-file = T3-T4, low confidence + single file = T1-T2. Deduplicate by file+dimension.
5. Run scoring: `python ./scripts/score.py`.
6. Append a record to `scan_history` with the date, overall score, strict score, and open item count.
7. Write updated `.desloppify/state.json`.
8. Display the status summary (overall / strict / objective scores, top open items, top clusters if any).
