---
name: desloppify-review
description: Run subjective review only (sequential passes scoring 20 quality dimensions).
triggers: ["user"]
---

Follow `./reference/workflows/review.md`.

Execute the 4 batches **sequentially in this session** — Devin's child sessions run on separate VMs and can't share state, so the parallel-subagent pattern is flattened to a single thorough pass. Work through the batches in order (Architecture → Correctness → Code Quality → External), following the per-batch instructions in the workflow for each. Accumulate the four JSON outputs, then merge per the "Merge Results" section.
