"""
Shelf-life regression model using CSV Time progression.

This model predicts remaining shelf life in HOURS.
Target engineering:
- For each avocado_id, find the first time it becomes rotten (label == 6).
- If rotten is never observed for that avocado_id, use its last recorded time.
- remaining_hours = target_end_time - current_time (clipped at >= 0).

Features used for prediction (5 inputs):
- gas_resistance
- co2
- temperature
- humidity
- pressure
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split


CSV_PATH = r"merged_avocado_dataset.csv"
MODEL_PATH = "shelf_life_regressor.joblib"
RANDOM_STATE = 42
TEST_SIZE = 0.2

FEATURE_COLUMNS = [
    "gas_resistance",
    "co2",
    "temperature",
    "humidity",
    "pressure",
]
ID_COLUMN = "avocado_id"
LABEL_COLUMN = "ripeness_label"
RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten",
}


def load_csv_with_header_fix(csv_path: str) -> pd.DataFrame:
    """Load CSV and fix exported-sheet header issues."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(path)

    lower_cols = [str(c).strip().lower() for c in df.columns]
    if all(c.startswith("unnamed:") or c == "" for c in lower_cols):
        header_row_idx = None
        for i in range(min(len(df), 10)):
            row_vals = " ".join(str(v).strip().lower() for v in df.iloc[i].tolist())
            if "avocado id" in row_vals and "temperature" in row_vals and "label" in row_vals:
                header_row_idx = i
                break
        if header_row_idx is not None:
            new_columns = [str(v).strip() for v in df.iloc[header_row_idx].tolist()]
            df = df.iloc[header_row_idx + 1 :].reset_index(drop=True)
            df.columns = new_columns

    df.columns = [str(c).strip() for c in df.columns]
    keep_cols = [
        c
        for c in df.columns
        if c
        and c.lower() not in {"nan", "none"}
        and not c.lower().startswith("unnamed:")
    ]
    df = df[keep_cols]
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename incoming columns to canonical names expected by training."""
    normalized_to_original = {
        str(col).strip().lower().replace(" ", "_"): col for col in df.columns
    }
    alias_map = {
        "avocado_id": ["avocado_id", "avocadoid"],
        "time_hours": ["time_hours", "time", "hours"],
        "temperature": ["temperature", "temp"],
        "humidity": ["humidity", "humidity_"],
        "pressure": ["pressure"],
        "gas_resistance": ["gas_resistance", "gasresistance", "gas_resistance_"],
        "co2": ["co2", "co_2"],
        "box_type": ["box_type", "boxtype", "box_type_", "box"],
        "ripeness_label": ["ripeness_label", "label", "target"],
    }

    rename_map: Dict[str, str] = {}
    for canonical, aliases in alias_map.items():
        for alias in aliases:
            if alias in normalized_to_original:
                rename_map[normalized_to_original[alias]] = canonical
                break

    df = df.rename(columns=rename_map)
    return df


def to_numeric_inplace(df: pd.DataFrame, cols: List[str]) -> None:
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")


def build_remaining_hours_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build regression target: remaining hours until rotten (label==6),
    or remaining hours until last observation if rotten never appears.
    """
    required = [ID_COLUMN, "time_hours", LABEL_COLUMN]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for target engineering: {missing}")

    grouped = df.groupby(ID_COLUMN, sort=False)
    end_time_map: Dict[float, float] = {}

    for avocado_id, g in grouped:
        g_sorted = g.sort_values("time_hours")
        rotten_rows = g_sorted[g_sorted[LABEL_COLUMN] == 6]
        if len(rotten_rows) > 0:
            end_time = float(rotten_rows["time_hours"].iloc[0])
        else:
            end_time = float(g_sorted["time_hours"].max())
        end_time_map[avocado_id] = end_time

    df["end_time_hours"] = df[ID_COLUMN].map(end_time_map)
    df["remaining_hours"] = (df["end_time_hours"] - df["time_hours"]).clip(lower=0)
    return df


def train() -> Tuple[RandomForestRegressor, RandomForestClassifier, List[str], pd.DataFrame]:
    df = load_csv_with_header_fix(CSV_PATH)
    df = standardize_columns(df)

    # Keep time_hours and ripeness_label for target engineering, even if
    # they are not part of the model's 5 input features.
    required = FEATURE_COLUMNS + [ID_COLUMN, LABEL_COLUMN, "time_hours"]
    missing_required = [c for c in required if c not in df.columns]
    if missing_required:
        raise ValueError(f"Dataset missing required columns: {missing_required}")

    to_numeric_inplace(df, required)
    df = df.dropna(subset=required).copy()
    df = build_remaining_hours_target(df)

    X = df[FEATURE_COLUMNS].copy()
    y_reg = df["remaining_hours"].copy()
    y_cls = df[LABEL_COLUMN].astype(int).copy()

    X_train, X_test, y_train_reg, y_test_reg, y_train_cls, y_test_cls = train_test_split(
        X,
        y_reg,
        y_cls,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_cls,
    )

    reg_model = RandomForestRegressor(
        n_estimators=300,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    reg_model.fit(X_train, y_train_reg)

    reg_preds = reg_model.predict(X_test)
    mae = mean_absolute_error(y_test_reg, reg_preds)
    rmse = float(np.sqrt(mean_squared_error(y_test_reg, reg_preds)))
    r2 = r2_score(y_test_reg, reg_preds)

    print("\n=== Shelf-Life Regression Evaluation ===")
    print(f"Rows used: {len(df)}")
    print(f"MAE (hours): {mae:.2f}")
    print(f"RMSE (hours): {rmse:.2f}")
    print(f"R^2: {r2:.4f}")

    cls_model = RandomForestClassifier(
        n_estimators=300,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    cls_model.fit(X_train, y_train_cls)
    cls_preds = cls_model.predict(X_test)
    cls_acc = accuracy_score(y_test_cls, cls_preds)
    print("\n=== Ripeness Classification Evaluation ===")
    print(f"Accuracy: {cls_acc:.4f}")

    artifact = {
        "reg_model": reg_model,
        "cls_model": cls_model,
        "feature_columns": FEATURE_COLUMNS,
        "ripeness_map": RIPENESS_MAP,
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"Saved model artifact: {MODEL_PATH}")
    return reg_model, cls_model, FEATURE_COLUMNS, df


def predict_remaining_hours(
    model: RandomForestRegressor,
    input_row: List[float],
) -> float:
    if len(input_row) != len(FEATURE_COLUMNS):
        raise ValueError(f"Expected {len(FEATURE_COLUMNS)} input values.")
    sample = pd.DataFrame([input_row], columns=FEATURE_COLUMNS)
    pred_hours = float(model.predict(sample)[0])
    return max(0.0, pred_hours)


def predict_ripeness_label(
    model: RandomForestClassifier,
    input_row: List[float],
) -> Tuple[int, str]:
    if len(input_row) != len(FEATURE_COLUMNS):
        raise ValueError(f"Expected {len(FEATURE_COLUMNS)} input values.")
    sample = pd.DataFrame([input_row], columns=FEATURE_COLUMNS)
    pred_class = int(model.predict(sample)[0])
    return pred_class, RIPENESS_MAP.get(pred_class, "unknown")


def main() -> None:
    reg_model, cls_model, _, _ = train()

    # Example inference input:
    # [gas_resistance, co2, temperature, humidity, pressure]
    demo = [258.7, 4279, 29.6, 84.4, 1008.3]
    pred_hours = predict_remaining_hours(reg_model, demo)
    pred_class, pred_label = predict_ripeness_label(cls_model, demo)
    print("\n=== Demo Prediction ===")
    print(f"Input: {demo}")
    print(f"Predicted ripeness: class {pred_class} ({pred_label})")
    print(f"Predicted remaining shelf life: {pred_hours:.2f} hours ({pred_hours/24:.2f} days)")


if __name__ == "__main__":
    main()
