---
name: desloppify-triage
description: Analyze, cluster, and plan the work queue from scan findings.
triggers: ["user"]
---

Follow `./reference/workflows/triage.md`.

Run the three stages (Analyze, Plan, Verify) sequentially in this session, passing each stage's JSON output as input to the next. After Stage 3 returns `approved: true`, apply the triage per the "Apply Triage" section.
