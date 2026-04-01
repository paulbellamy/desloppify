# Desloppify

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin for systematic codebase quality scanning with persistent scoring across 20 dimensions.

Inspired by [peteromallet/desloppify](https://github.com/peteromallet/desloppify).

## Install

```sh
# Add the marketplace
/plugin marketplace add https://github.com/paulbellamy/desloppify

# Install the plugin
/plugin install desloppify
```

## Commands

| Command | Description |
|---------|-------------|
| `/desloppify:scan` | Full scan (linters + subjective review) |
| `/desloppify:review` | Subjective review only (4 parallel subagents) |
| `/desloppify:triage` | Analyze, cluster, and plan work queue |
| `/desloppify:next` | Show and work next queue item |
| `/desloppify:status` | Show scores and progress |
| `/desloppify:resolve <pattern> [--fixed\|--wontfix\|--false-positive]` | Mark items as resolved |

## How it works

Main cycle: **scan -> triage -> execute -> rescan**.

**Scan** runs mechanical linters (ruff, eslint, clippy, etc.) and launches 4 parallel review subagents that score the codebase across 20 quality dimensions. Results are persisted to `.desloppify/state.json`.

**Scoring** combines 25% mechanical (linter findings) + 75% subjective (review assessments). The **strict score** penalizes wontfix items -- the gap between overall and strict is your wontfix debt.

**Triage** analyzes findings, clusters them by root cause, and builds an ordered work queue.

**Execute** (`next`) works through the queue one cluster at a time, fixing issues and updating scores.

## Dimensions

20 quality dimensions across four batches:

- **Architecture**: high/mid-level elegance, cross-module architecture, package organization, initialization coupling
- **Correctness**: type safety, contract coherence, logic clarity, error consistency, design coherence
- **Code Quality**: naming quality, abstraction fitness, AI-generated debt, convention outliers, low-level elegance
- **External**: dependency health, test strategy, API surface coherence, authorization consistency, incomplete migrations

## License

MIT
