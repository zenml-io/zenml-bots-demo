---
name: platform-triage
description: How the infrastructure analytics team investigates failed or misbehaving ZenML pipeline runs and proposes verified fixes. Use for any pipeline failure, quality drop, or compute cost question.
---

# Pipeline triage

1. Start from the failing run: find the failed step, its error, and the last successful run of the same pipeline.
2. Compare the two runs: parameters, input artifacts, which steps ran and which were cached, and the code they ran.
3. Look at everything the failing step read, including inputs reused from the cache.
4. State the root cause in one sentence, with links to the runs, steps, and artifact versions that prove it.
5. Prefer the smallest fix. Never delete runs or artifacts, and never change stacks or schedules.
6. Ask for approval before any rerun you were not asked for, and say what it touches.
7. Verify the fix with a real run, then confirm that the next normal run succeeds too.

Report the verdict first, then the root cause, evidence, fix, and verification.
