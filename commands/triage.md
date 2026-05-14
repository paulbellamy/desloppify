---
description: Analyze, cluster, and plan the work queue from scan findings.
---

Follow `./reference/workflows/triage.md`.

Run each of the three stages (Analyze, Plan, Verify) as a separate Agent invocation with `subagent_type: "general-purpose"`, passing the prior stage's JSON output as input to the next. After Stage 3 returns `approved: true`, apply the triage per the "Apply Triage" section of the workflow.
