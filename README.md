# Desloppify

Systematic codebase quality scanning with persistent scoring across 20 dimensions. Ships as both a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin and a set of [Devin](https://devin.ai) skills, sharing the same reference material and scoring script.

Inspired by [peteromallet/desloppify](https://github.com/peteromallet/desloppify).

## Install — Claude Code

```sh
# Add the marketplace
/plugin marketplace add https://github.com/paulbellamy/desloppify

# Install the plugin
/plugin install desloppify
```

Invoke commands as `/desloppify:<name>`.

## Install — Devin

Devin auto-discovers skills under `.agents/skills/` in the repository. Once this repo is connected to your Devin workspace, the skills are available as `desloppify-scan`, `desloppify-review`, `desloppify-triage`, `desloppify-next`, `desloppify-status`, and `desloppify-resolve`. Invoke them by name or `@skills:<name>`.

The Devin skills are functionally equivalent to the Claude Code commands but run the four review batches **sequentially** (Devin's child sessions run on separate VMs and can't share `.desloppify/state.json`, so the parallel-subagent pattern is flattened to a single thorough pass). Scoring, state schema, and dimension definitions are identical.

## Commands

| Claude Code | Devin Skill | Description |
|-------------|-------------|-------------|
| `/desloppify:scan` | `desloppify-scan` | Full scan (linters + subjective review) |
| `/desloppify:review` | `desloppify-review` | Subjective review only |
| `/desloppify:triage` | `desloppify-triage` | Analyze, cluster, and plan work queue |
| `/desloppify:next` | `desloppify-next` | Show and work next queue item |
| `/desloppify:status` | `desloppify-status` | Show scores and progress |
| `/desloppify:resolve <pattern> [--fixed\|--wontfix\|--false-positive]` | `desloppify-resolve` | Mark items as resolved |

## How it works

Main cycle: **scan -> triage -> execute -> rescan**.

**Scan** runs mechanical linters (ruff, eslint, clippy, etc.) and reviews the codebase across 20 quality dimensions — as 4 parallel subagents under Claude Code, or as 4 sequential batches under Devin. Results are persisted to `.desloppify/state.json`.

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
