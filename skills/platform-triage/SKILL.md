---
name: platform-triage
description: The infrastructure analytics team's runbook for investigating failed, degraded, or wasteful ZenML pipeline runs and proposing verified fixes. Use for any pipeline review, incident, quality drop, or compute cost question.
---

# Platform triage runbook

The team owns three pipelines in this repository: `asset_health_report` (daily asset condition report), `defect_risk_scoring` (repair classifier on the field inspection export), and `cost_forecast_training` (project cost forecaster). Treat each run's recorded metadata, artifacts, and step statuses as the source of truth, not assumptions about the code.

## What counts as a problem

- **Broken**: a run failed, or a step failed. Find the failing step, its error, and what changed compared with the last successful run of the same pipeline.
- **Degraded**: a run completed but a quality metric (`accuracy`, `recall`, `precision`) dropped more than 5 points below the median of the previous successful runs. Green runs can still be wrong; always check these.
- **Wasteful**: an expensive step re-executed even though its inputs did not change. Compare input artifact contents and step parameters across runs and look for parameters that change every run without affecting the output.

## How to investigate

1. List the recent runs of each pipeline and group them by status.
2. For each problem, compare the bad run with the last good run: parameters, input artifacts, cached versus executed steps, logged metadata, and the code at the commit the run used.
3. Load artifacts when the metadata is not enough. Check that cached artifacts still exist in the artifact store before trusting them.
4. State the root cause in one sentence and link the runs, steps, and artifact versions that prove it.

## How to fix

- Prefer a code change in this repository, delivered as a draft pull request whose description holds the evidence and a validation plan.
- Make failures loud: a silently wrong result is worse than a failed run.
- Never delete artifacts or runs. Never change stacks or schedules without asking.
- Ask for approval before any rerun you were not explicitly asked to do, and say what it will cost.
- After a fix, verify it with a real run and compare the result with the last good run.

## How to report

Start with a one-line verdict per pipeline (healthy, broken, degraded, or wasteful). Then, per problem: root cause, evidence links, impact in numbers (failed runs, metric drop, compute seconds wasted), and the proposed fix or pull request. Record a comparison or chart artifact when numbers are involved, and record a follow-up task for each problem that still needs work.
