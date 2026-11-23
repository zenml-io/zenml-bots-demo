"""Data sources for the infrastructure analytics pipelines.

The sources are simulated and deterministic for a given seed, so repeated
runs over the same inputs produce identical artifacts.
"""

from datetime import date
from hashlib import sha256

import numpy as np
import pandas as pd

ASSET_TYPES = ("bridge", "culvert", "pump_station", "retaining_wall", "tunnel")
REGIONS = ("north", "south", "east", "west")
INSPECTION_FEATURES = (
    "crack_width_mm",
    "corrosion_pct",
    "age_years",
    "load_ratio",
    "moisture_index",
)


def generate_asset_registry(asset_count: int, seed: int) -> pd.DataFrame:
    """Create a fixed registry of monitored infrastructure assets.

    Args:
        asset_count: Number of assets in the registry.
        seed: Seed for the registry attributes.

    Returns:
        One row per asset with its type, region, age, and sensor baselines.
    """
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "asset_id": [f"AST-{i:04d}" for i in range(1, asset_count + 1)],
            "asset_type": rng.choice(ASSET_TYPES, asset_count),
            "region": rng.choice(REGIONS, asset_count),
            "install_year": rng.integers(1962, 2021, asset_count),
            "baseline_vibration_mm_s": rng.uniform(0.8, 3.5, asset_count),
            "baseline_strain_ue": rng.uniform(120, 480, asset_count),
            "alert_threshold": rng.uniform(1.6, 2.2, asset_count),
        }
    )


def simulate_daily_readings(registry: pd.DataFrame, business_date: str) -> pd.DataFrame:
    """Simulate one day of sensor readings and condition flags per asset.

    Args:
        registry: Asset registry produced by `generate_asset_registry`.
        business_date: ISO date the readings represent.

    Returns:
        Daily readings with a condition ratio and an alert flag per asset.
    """
    day = date.fromisoformat(business_date)
    seed = int.from_bytes(sha256(day.isoformat().encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    count = len(registry)
    age = day.year - registry["install_year"]
    wear = 1 + age / 120
    vibration = (
        registry["baseline_vibration_mm_s"] * wear * rng.uniform(0.7, 1.9, count)
    )
    strain = registry["baseline_strain_ue"] * wear * rng.uniform(0.8, 1.5, count)
    ratio = vibration / registry["baseline_vibration_mm_s"]
    return pd.DataFrame(
        {
            "business_date": business_date,
            "asset_id": registry["asset_id"],
            "asset_type": registry["asset_type"],
            "region": registry["region"],
            "vibration_mm_s": vibration.round(3),
            "strain_ue": strain.round(1),
            "condition_ratio": ratio.round(3),
            "alert": ratio > registry["alert_threshold"],
        }
    )


def generate_inspections(count: int, seed: int) -> pd.DataFrame:
    """Create an inspection export as delivered by the field inspection system.

    Args:
        count: Number of inspection records.
        seed: Seed for the records.

    Returns:
        Inspection records with the engineer's final `needs_repair` decision.
    """
    rng = np.random.default_rng(seed)
    crack = rng.gamma(2.0, 0.45, count)
    corrosion = rng.uniform(0, 80, count)
    age = rng.integers(3, 70, count)
    load = rng.uniform(0.3, 1.1, count)
    moisture = rng.uniform(0, 1, count)
    needs_repair = (crack > 1.3) | ((corrosion > 65) & (age > 45))
    return pd.DataFrame(
        {
            "inspection_id": [f"INS-{i:05d}" for i in range(1, count + 1)],
            "asset_type": rng.choice(ASSET_TYPES, count),
            "crack_width_mm": crack.round(2),
            "corrosion_pct": corrosion.round(1),
            "age_years": age,
            "load_ratio": load.round(3),
            "moisture_index": moisture.round(3),
            "needs_repair": needs_repair.astype(int),
        }
    )


def generate_cost_history(month: str, project_count: int = 30000) -> pd.DataFrame:
    """Create the monthly project cost history used for cost forecasting.

    Args:
        month: Snapshot month in YYYY-MM format; also the generator seed.
        project_count: Number of historical projects.

    Returns:
        Project features with the realized final cost in thousands.
    """
    seed = int(month.replace("-", ""))
    rng = np.random.default_rng(seed)
    length = rng.uniform(0.2, 12, project_count)
    spans = rng.integers(1, 9, project_count)
    duration = rng.uniform(3, 48, project_count)
    steel = rng.uniform(0.6, 1.6, project_count)
    labor = rng.uniform(0.7, 1.5, project_count)
    complexity = rng.integers(1, 6, project_count)
    urban = rng.integers(0, 2, project_count)
    cost = (
        length * 900 * steel
        + spans * 350
        + duration * 40 * labor
        + complexity**2 * 120
        + urban * 600
    ) * rng.lognormal(0, 0.12, project_count)
    return pd.DataFrame(
        {
            "length_km": length.round(3),
            "span_count": spans,
            "duration_months": duration.round(1),
            "steel_index": steel.round(3),
            "labor_index": labor.round(3),
            "complexity": complexity,
            "urban": urban,
            "final_cost_k": cost.round(1),
        }
    )
