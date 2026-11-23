"""Run one of the infrastructure analytics pipelines by hand."""

import argparse
from datetime import date
from typing import Any

from zenml.client import Client

from pipelines import (
    asset_health_report,
    cost_forecast_training,
    defect_risk_scoring,
)


def default_inspection_uri() -> str:
    """Return where the seed script publishes the inspection export.

    Returns:
        The CSV location inside the active stack's artifact store.
    """
    artifact_store = Client().active_stack.artifact_store
    return f"{artifact_store.path}/sources/inspections.csv"


def main() -> None:
    """Parse the command line and run the requested pipeline."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    asset = commands.add_parser("asset-report", help="Daily asset health report.")
    asset.add_argument("--business-date", default=date.today().isoformat())
    scoring = commands.add_parser("defect-scoring", help="Defect risk scoring.")
    scoring.add_argument("--source-uri")
    commands.add_parser("cost-training", help="Cost forecast training.")
    for command in commands.choices.values():
        command.add_argument("--run-name")
        command.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    options: dict[str, Any] = {}
    if args.run_name:
        options["run_name"] = args.run_name
    if args.no_cache:
        options["enable_cache"] = False

    if args.command == "asset-report":
        run = asset_health_report.with_options(**options)(
            business_date=args.business_date
        )
    elif args.command == "defect-scoring":
        run = defect_risk_scoring.with_options(**options)(
            source_uri=args.source_uri or default_inspection_uri()
        )
    else:
        run = cost_forecast_training.with_options(**options)()
    print(f"Run {run.name} ({run.id}): {run.status}")


if __name__ == "__main__":
    main()
