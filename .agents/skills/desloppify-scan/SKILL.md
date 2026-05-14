---
name: desloppify-scan
description: Run full codebase quality scan (linters + subjective review), persist state, compute scores.
triggers: ["user"]
---

Follow `./reference/workflows/scan.md`.

For Step 3 (Subjective Review), execute the 4 batches **sequentially in this session** — Devin's child sessions run on separate VMs and can't share `.desloppify/state.json`, so the parallel-subagent pattern is flattened to a single thorough pass. Work through the batches in order (Architecture → Correctness → Code Quality → External), following the per-batch instructions in `./reference/workflows/review.md` for each. Accumulate the four JSON outputs, then continue with Step 4.
