# Desloppify

## Mission

Maximise the **strict score** honestly. Main cycle: **scan -> triage -> execute -> rescan**.

Don't be lazy. Do large refactors and small detailed fixes with equal energy. If it takes touching 20 files, touch 20 files.

## Commands

| Command | Description |
|---------|-------------|
| `/desloppify:scan` | Full scan (linters + subjective review) |
| `/desloppify:review` | Subjective review only (4 parallel subagents) |
| `/desloppify:triage` | Analyze, cluster, and plan work queue |
| `/desloppify:next` | Show & work next queue item |
| `/desloppify:status` | Show scores and progress |
| `/desloppify:resolve` | Mark items as resolved |

## State Schema

Persisted at `.desloppify/state.json`:

```json
{
  "version": 1,
  "last_scan": "2024-01-15T10:30:00Z",
  "scores": {
    "overall": 0,
    "strict": 0,
    "objective": 0
  },
  "dimension_scores": {
    "<dimension_name>": {
      "score": 0,
      "assessed_at": "ISO"
    }
  },
  "work_items": {
    "<id>": {
      "source": "linter|review",
      "detector": "ruff|eslint|review",
      "dimension": "",
      "file": "relative/path",
      "line": 0,
      "tier": 3,
      "confidence": "high|medium|low",
      "summary": "",
      "suggestion": "",
      "status": "open|fixed|wontfix|false_positive|auto_resolved",
      "first_seen": "ISO",
      "resolved_at": null
    }
  },
  "queue": ["cluster-name-1", "cluster-name-2"],
  "clusters": {
    "<name>": {
      "thesis": "",
      "item_ids": [],
      "effort": "trivial|small|medium|large",
      "depends_on": []
    }
  },
  "scan_history": [
    {
      "date": "ISO",
      "overall": 0,
      "strict": 0,
      "item_count": 0
    }
  ]
}
```

Initialize with `mkdir -p .desloppify && echo '{"version":1,"work_items":{},"dimension_scores":{},"queue":[],"clusters":{},"scan_history":[]}' > .desloppify/state.json` if it doesn't exist.

## Key Concepts

- **Tiers**: T1 auto-fix -> T2 quick manual -> T3 judgment call -> T4 major refactor
- **Strict score**: wontfix items count as open. The gap between overall and strict is wontfix debt.
- **Scoring**: 25% mechanical (linters) + 75% subjective (review). See [scoring reference](./scoring.md).
- **Clusters**: groups of related items sharing a root cause. Fix together for coherence.
- **Queue**: ordered list of clusters/items to work through. Triage sets the order.
- **Scan history**: enables trajectory tracking. Score dips after fixes are normal (cascade effects).

## Reference Files

- [Dimension definitions](./dimensions.md) — what each of the 20 quality dimensions means, what to look for, what to skip
- [Review system prompt](./review-system-prompt.md) — scoring philosophy, calibration anchors, output format for review subagents
- [Scoring formula](./scoring.md) — exact weights and computation for mechanical + subjective scores
