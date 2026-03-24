"""
TensorFlow multi-class classification project for avocado ripeness.

Requirements covered:
- CSV loading with pandas
- Data inspection (info/head/columns) and missing value handling
- Feature preprocessing (scaling + train/test split)
- Keras Sequential model for 7-class classification
- Training with validation split
- Evaluation (accuracy, confusion matrix, classification report)
- Prediction function for new single-row input
- Model saving and loading with inference example
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# -----------------------------
# Configuration
# -----------------------------
CSV_PATH = r"C:\Users\Hans\Downloads\data-set-avocado-cleanbago.csv"  # User-requested dataset path
MODEL_SAVE_PATH = "avocado_ripeness_model.keras"
RANDOM_STATE = 42
TEST_SIZE = 0.2
EPOCHS = 30
BATCH_SIZE = 16
VALIDATION_SPLIT = 0.2

# Features and target as requested
FEATURE_COLUMNS = [
    "gas_resistance",
    "co2",
    "temperature",
    "humidity",
    "pressure",
]
TARGET_COLUMN = "ripeness_label"

# Ripeness class mapping
RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten",
}

# Estimated shelf life in days by predicted ripeness class.
SHELF_LIFE_DAYS_MAP = {
    0: 7,
    1: 5,
    2: 3,
    3: 2,
    4: 1,
    5: 0,
    6: 0,
}


def load_and_inspect_data(csv_path: str) -> pd.DataFrame:
    """Load CSV, print basic inspection, and handle missing values."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found at '{csv_path}'. "
            "Update CSV_PATH in the script to your dataset file."
        )

    df = pd.read_csv(path)

    # Some spreadsheets exported to CSV include an extra row where the real
    # headers are stored as row values (with columns named Unnamed:*).
    # Detect and promote that row before normal processing.
    lower_cols = [str(c).strip().lower() for c in df.columns]
    if all(c.startswith("unnamed:") or c == "" for c in lower_cols):
        header_row_idx = None
        for i in range(min(len(df), 10)):
            row_vals = [str(v).strip().lower() for v in df.iloc[i].tolist()]
            joined = " ".join(row_vals)
            if ("avocado id" in joined and "temperature" in joined and "label" in joined):
                header_row_idx = i
                break
        if header_row_idx is not None:
            new_columns = [str(v).strip() for v in df.iloc[header_row_idx].tolist()]
            df = df.iloc[header_row_idx + 1 :].reset_index(drop=True)
            df.columns = new_columns

    # Normalize headers and remove empty/placeholder columns.
    cleaned_columns = [str(c).strip() for c in df.columns]
    df.columns = cleaned_columns
    keep_cols = [
        c
        for c in df.columns
        if c
        and c.lower() not in {"nan", "none"}
        and not c.lower().startswith("unnamed:")
    ]
    df = df[keep_cols]

    # If duplicate headers exist, keep first occurrence.
    df = df.loc[:, ~df.columns.duplicated()]

    # Convert numeric-looking text columns to numeric.
    for col in df.columns:
        if df[col].dtype == object:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() >= max(1, int(0.8 * len(df))):
                df[col] = converted

    print("\n=== Dataset Head ===")
    print(df.head())

    print("\n=== Dataset Info ===")
    # df.info() already prints useful information
    df.info()

    print("\n=== Column Names ===")
    print(df.columns.tolist())

    # Check missing values
    print("\n=== Missing Values (Before Handling) ===")
    print(df.isnull().sum())

    # Handle missing values:
    # - Numeric columns -> median imputation
    # - Non-numeric columns (if any) -> mode imputation
    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                mode_vals = df[col].mode()
                fill_value = mode_vals.iloc[0] if not mode_vals.empty else "unknown"
                df[col] = df[col].fillna(fill_value)

    print("\n=== Missing Values (After Handling) ===")
    print(df.isnull().sum())

    # Standardize column names to make the pipeline resilient to real-world CSV naming.
    # Example mappings handled:
    # "Temperature" -> "temperature", "CO2" -> "co2".
    normalized_to_original = {
        str(col).strip().lower().replace(" ", "_"): col for col in df.columns
    }
    alias_map = {
        "temperature": ["temperature", "temp"],
        "humidity": ["humidity", "humidity_"],
        "pressure": ["pressure"],
        "gas_resistance": ["gas_resistance", "gas_resistance_", "gasresistance"],
        "co2": ["co2", "co_2"],
        "ripeness_label": ["ripeness_label", "label", "target"],
    }

    rename_dict = {}
    for canonical_name, aliases in alias_map.items():
        for alias in aliases:
            if alias in normalized_to_original:
                rename_dict[normalized_to_original[alias]] = canonical_name
                break

    df = df.rename(columns=rename_dict)
    return df


def preprocess_data(
    df: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
    """Prepare X/y, split train-test, and scale features."""
    # Ensure required columns are present
    required_cols = set(FEATURE_COLUMNS + [TARGET_COLUMN])
    missing_required = required_cols - set(df.columns)
    if missing_required:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing_required)}")

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].astype(int).values

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y if len(np.unique(y)) > 1 else None,
    )

    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def build_model(input_dim: int) -> tf.keras.Model:
    """Build and compile Keras Sequential model."""
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(7, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_model(
    model: tf.keras.Model,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> tf.keras.callbacks.History:
    """Train model and return history."""
    history = model.fit(
        X_train,
        y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        verbose=1,
    )
    return history


def evaluate_model(
    model: tf.keras.Model,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> None:
    """Evaluate on test set and print sklearn metrics."""
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print("\n=== Test Evaluation ===")
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")

    y_prob = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)

    cm = confusion_matrix(y_test, y_pred, labels=list(RIPENESS_MAP.keys()))
    print("\n=== Confusion Matrix ===")
    print(cm)

    report = classification_report(
        y_test,
        y_pred,
        labels=list(RIPENESS_MAP.keys()),
        target_names=[RIPENESS_MAP[i] for i in RIPENESS_MAP.keys()],
        zero_division=0,
    )
    print("\n=== Classification Report ===")
    print(report)


def predict_ripeness(
    model: tf.keras.Model,
    scaler: StandardScaler,
    input_row: Sequence[float],
) -> Tuple[int, str, int, np.ndarray]:
    """
    Predict ripeness for one sample.

    input_row order:
    [gas_resistance, co2, temperature, humidity, pressure]
    """
    if len(input_row) != len(FEATURE_COLUMNS):
        raise ValueError(f"input_row must have exactly {len(FEATURE_COLUMNS)} values.")

    sample = np.array(input_row, dtype=float).reshape(1, -1)
    sample_scaled = scaler.transform(sample)
    probs = model.predict(sample_scaled, verbose=0)[0]
    pred_class = int(np.argmax(probs))
    pred_label = RIPENESS_MAP.get(pred_class, "unknown")
    shelf_life_days = SHELF_LIFE_DAYS_MAP.get(pred_class, 0)
    return pred_class, pred_label, shelf_life_days, probs


def save_model(model: tf.keras.Model, save_path: str) -> None:
    """Save trained model to disk."""
    model.save(save_path)
    print(f"\nModel saved to: {save_path}")


def load_model(model_path: str) -> tf.keras.Model:
    """Load model from disk."""
    loaded = tf.keras.models.load_model(model_path)
    print(f"Model loaded from: {model_path}")
    return loaded


def print_training_history(history: tf.keras.callbacks.History) -> None:
    """Print final epoch training and validation metrics."""
    hist = history.history
    if not hist:
        return

    final_epoch = len(hist.get("loss", []))
    if final_epoch == 0:
        return

    print("\n=== Final Epoch Metrics ===")
    print(f"Epochs trained: {final_epoch}")
    print(f"Train Loss: {hist['loss'][-1]:.4f}")
    print(f"Train Accuracy: {hist['accuracy'][-1]:.4f}")
    if "val_loss" in hist and "val_accuracy" in hist:
        print(f"Val Loss: {hist['val_loss'][-1]:.4f}")
        print(f"Val Accuracy: {hist['val_accuracy'][-1]:.4f}")


def main() -> None:
    # Make TensorFlow behavior reproducible as much as possible
    tf.random.set_seed(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)

    # 1) Load and inspect
    df = load_and_inspect_data(CSV_PATH)

    # 2) Preprocess
    X_train, X_test, y_train, y_test, scaler = preprocess_data(df)

    # 3-4) Build and compile model
    model = build_model(input_dim=X_train.shape[1])

    # 5) Train
    history = train_model(model, X_train, y_train)
    print_training_history(history)

    # 6) Evaluate
    evaluate_model(model, X_test, y_test)

    # 8) Save model
    save_model(model, MODEL_SAVE_PATH)

    # 8) Load model and run inference
    loaded_model = load_model(MODEL_SAVE_PATH)

    # 7) Prediction example with 5 values
    # [gas_resistance, co2, temperature, humidity, pressure]
    new_sample = [391.0, 5000.0, 27.4, 85.3, 1009.5]
    pred_class, pred_label, shelf_life_days, pred_probs = predict_ripeness(
        loaded_model, scaler, new_sample
    )

    print("\n=== Single Sample Prediction ===")
    print(f"Input Row: {new_sample}")
    print(f"Predicted Class: {pred_class}")
    print(f"Predicted Label: {pred_label}")
    print(f"Estimated Shelf Life (days): {shelf_life_days}")
    print(f"Class Probabilities: {np.round(pred_probs, 4)}")


if __name__ == "__main__":
    main()
