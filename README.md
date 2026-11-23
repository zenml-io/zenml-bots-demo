# Infrastructure analytics pipelines

ZenML pipelines of the infrastructure analytics team.

| Pipeline | Schedule | What it does |
| --- | --- | --- |
| `asset_health_report` | Daily | Scores every monitored asset's sensor readings against its baseline and flags assets in alert. The asset registry changes once per quarter, so its loading step is cached. |
| `defect_risk_scoring` | Daily | Trains and evaluates the repair classifier on the latest field inspection export. |
| `cost_forecast_training` | Nightly | Trains the project cost forecaster on the published monthly cost history. |

## Setup

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt s3fs boto3 "kubernetes>=21.7,<26" pygithub
zenml login <workspace>
zenml project set infra-analytics
zenml stack set kubernetes
```

## Run

```bash
python run.py asset-report --business-date 2026-11-24
python run.py defect-scoring
python run.py cost-training
```

`--run-name` names the run and `--no-cache` disables step caching. The inspection export is read from `<artifact store>/sources/inspections.csv` unless `--source-uri` is given.

The team's triage runbook lives in `skills/platform-triage`.
