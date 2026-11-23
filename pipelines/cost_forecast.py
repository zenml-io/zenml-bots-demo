"""Nightly project cost forecast training."""

import time
from datetime import datetime, timezone
from typing import Annotated

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from zenml import log_metadata, pipeline, step

from .data import generate_cost_history
from .settings import DOCKER_SETTINGS

FEATURES = [
    "length_km",
    "span_count",
    "duration_months",
    "steel_index",
    "labor_index",
    "complexity",
    "urban",
]


@step
def load_cost_history(
    snapshot_month: str,
) -> Annotated[pd.DataFrame, "cost_history"]:
    """Load the published monthly project cost history.

    Args:
        snapshot_month: Published snapshot in YYYY-MM format.

    Returns:
        Historical projects with their realized cost.
    """
    history = generate_cost_history(snapshot_month)
    log_metadata({"snapshot_month": snapshot_month, "project_count": len(history)})
    return history


@step
def train_cost_model(
    history: pd.DataFrame, trained_at: str, n_estimators: int = 300
) -> Annotated[GradientBoostingRegressor, "cost_model"]:
    """Train the project cost forecaster.

    Args:
        history: Project cost history.
        trained_at: Timestamp recorded with the model.
        n_estimators: Number of boosting stages.

    Returns:
        The fitted cost model.
    """
    started = time.perf_counter()
    x_train, x_test, y_train, y_test = train_test_split(
        history[FEATURES], history["final_cost_k"], test_size=0.2, random_state=0
    )
    model = GradientBoostingRegressor(
        n_estimators=n_estimators, max_depth=4, random_state=0
    )
    model.fit(x_train, y_train)
    log_metadata(
        {
            "trained_at": trained_at,
            "mae_k": round(
                float(mean_absolute_error(y_test, model.predict(x_test))), 2
            ),
            "training_seconds": round(time.perf_counter() - started, 1),
        }
    )
    return model


@pipeline(enable_cache=True, settings={"docker": DOCKER_SETTINGS})
def cost_forecast_training(snapshot_month: str = "2026-11") -> None:
    """Retrain the project cost forecaster every night.

    Args:
        snapshot_month: Published cost history snapshot to train on.
    """
    history = load_cost_history(snapshot_month=snapshot_month)
    train_cost_model(history=history, trained_at=datetime.now(timezone.utc).isoformat())
