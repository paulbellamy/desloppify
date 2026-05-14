---
description: Run full codebase quality scan (linters + subjective review), persist state, compute scores.
---

Follow `./reference/workflows/scan.md`.

For Step 3 (Subjective Review), launch the 4 batches **in parallel** via the Agent tool with `subagent_type: "general-purpose"`. Use this prompt for each batch:

```
You are a code quality reviewer for the {batch_name} batch.

Read these reference files first:
- ./reference/dimensions.md (find your assigned dimensions)
- ./reference/review-system-prompt.md (scoring philosophy and rules)

You are reviewing the codebase at: {cwd}
Score these dimensions: {dimension_list}

Follow the per-batch instructions and output format in
./reference/workflows/review.md. Return your results as a single JSON block.
```

Then merge the 4 subagent outputs per the "Merge Results" section of `./reference/workflows/review.md` and continue with Step 4.
