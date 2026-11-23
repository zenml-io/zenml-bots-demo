"""Defect risk scoring on the field inspection export."""

from typing import Annotated

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from zenml import log_metadata, pipeline, step
from zenml.io import fileio

from .data import INSPECTION_FEATURES
from .settings import DOCKER_SETTINGS


@step(enable_cache=False)
def load_inspections(
    source_uri: str,
) -> Annotated[pd.DataFrame, "inspections"]:
    """Read the latest inspection export.

    Args:
        source_uri: Location of the CSV export, readable by the active stack.

    Returns:
        The raw inspection records.
    """
    with fileio.open(source_uri, "r") as source:
        inspections = pd.read_csv(source)
    log_metadata({"source_uri": source_uri, "row_count": len(inspections)})
    return inspections


@step
def prepare_features(
    inspections: pd.DataFrame,
) -> tuple[Annotated[pd.DataFrame, "features"], Annotated[pd.Series, "labels"]]:
    """Select the model features and the repair label.

    Args:
        inspections: Raw inspection records.

    Returns:
        The feature matrix and the `needs_repair` labels.
    """
    features = inspections.reindex(columns=list(INSPECTION_FEATURES), fill_value=0.0)
    return features, inspections["needs_repair"]


@step
def train_and_evaluate(
    features: pd.DataFrame, labels: pd.Series, random_seed: int
) -> Annotated[dict[str, float], "quality_metrics"]:
    """Train the repair classifier and evaluate it on a held-out split.

    Args:
        features: Feature matrix.
        labels: Repair labels.
        random_seed: Seed for the split and the model.

    Returns:
        Accuracy, precision, and recall on the held-out split.
    """
    x_train, x_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.3, random_state=random_seed, stratify=labels
    )
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predicted)), 4),
        "precision": round(
            float(precision_score(y_test, predicted, zero_division=0)), 4
        ),
        "recall": round(float(recall_score(y_test, predicted, zero_division=0)), 4),
        "flagged_for_repair": int(predicted.sum()),
        "evaluated_inspections": len(y_test),
    }
    log_metadata(metrics)
    return metrics


@pipeline(enable_cache=False, settings={"docker": DOCKER_SETTINGS})
def defect_risk_scoring(source_uri: str, random_seed: int = 7) -> None:
    """Score the inspection export and record model quality.

    Args:
        source_uri: Location of the inspection CSV export.
        random_seed: Seed for the split and the model.
    """
    inspections = load_inspections(source_uri=source_uri)
    features, labels = prepare_features(inspections=inspections)
    train_and_evaluate(features=features, labels=labels, random_seed=random_seed)
