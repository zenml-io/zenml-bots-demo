"""Daily asset health report built on a cached asset registry."""

from typing import Annotated

import pandas as pd
from zenml import log_metadata, pipeline, step

from .data import generate_asset_registry, simulate_daily_readings
from .settings import DOCKER_SETTINGS


@step
def load_asset_registry(
    asset_count: int, registry_version: str
) -> Annotated[pd.DataFrame, "asset_registry"]:
    """Load the asset registry for a published registry version.

    Args:
        asset_count: Number of assets in the registry.
        registry_version: Published registry version, e.g. `2026-Q4`.

    Returns:
        The asset registry.
    """
    seed = sum(ord(char) for char in registry_version)
    registry = generate_asset_registry(asset_count, seed)
    log_metadata({"asset_count": len(registry), "registry_version": registry_version})
    return registry


@step(enable_cache=False)
def compute_daily_condition(
    registry: pd.DataFrame, business_date: str
) -> Annotated[pd.DataFrame, "daily_condition"]:
    """Score each asset's condition for one business day.

    Args:
        registry: The asset registry.
        business_date: ISO date of the report.

    Returns:
        Per-asset readings and alert flags for the day.
    """
    readings = simulate_daily_readings(registry, business_date)
    log_metadata(
        {
            "business_date": business_date,
            "assets_reporting": len(readings),
            "assets_in_alert": int(readings["alert"].sum()),
            "max_condition_ratio": float(readings["condition_ratio"].max()),
        }
    )
    return readings


@pipeline(enable_cache=True, settings={"docker": DOCKER_SETTINGS})
def asset_health_report(
    business_date: str,
    asset_count: int = 400,
    registry_version: str = "2026-Q4",
) -> None:
    """Produce the daily asset health report.

    The registry only changes once per quarter, so its loading step is cached
    and every daily run reuses the stored registry artifact.

    Args:
        business_date: ISO date of the report.
        asset_count: Number of assets in the registry.
        registry_version: Published registry version.
    """
    registry = load_asset_registry(
        asset_count=asset_count, registry_version=registry_version
    )
    compute_daily_condition(registry=registry, business_date=business_date)
