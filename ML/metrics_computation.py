"""
Metrics computation utilities for model evaluation.

This module provides functions to compute:
- Regression metrics: MAE, RMSE, R²
- Classification metrics: Accuracy

These metrics can be used to evaluate model performance
without cluttering the main model training code.
"""

from typing import Dict, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def compute_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, float]:
    """
    Compute regression evaluation metrics.
    
    Args:
        y_true: Ground truth target values
        y_pred: Predicted target values
        
    Returns:
        Dictionary containing:
        - mae: Mean Absolute Error
        - rmse: Root Mean Squared Error
        - r2: R-squared (coefficient of determination)
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_true, y_pred)
    
    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, float]:
    """
    Compute classification evaluation metrics.
    
    Args:
        y_true: Ground truth class labels
        y_pred: Predicted class labels
        
    Returns:
        Dictionary containing:
        - accuracy: Classification accuracy
    """
    accuracy = accuracy_score(y_true, y_pred)
    
    return {
        "accuracy": accuracy,
    }


def print_regression_metrics(
    metrics: Dict[str, float],
    title: str = "Regression Metrics",
    hours_unit: bool = True,
    show_computation: bool = False,
    y_true: np.ndarray = None,
    y_pred: np.ndarray = None,
) -> None:
    """
    Print regression metrics in a formatted way.
    
    Args:
        metrics: Dictionary with mae, rmse, r2 keys
        title: Title to display
        hours_unit: If True, display MAE/RMSE with "(hours)" label
        show_computation: If True, show detailed computation steps
        y_true: Ground truth values (needed if show_computation=True)
        y_pred: Predicted values (needed if show_computation=True)
    """
    unit_label = " (hours)" if hours_unit else ""
    print(f"\n=== {title} ===")
    
    if show_computation and y_true is not None and y_pred is not None:
        n = len(y_true)
        print(f"\nNumber of samples: {n}")
        
        # MAE computation
        print(f"\n--- MAE (Mean Absolute Error) ---")
        print(f"Formula: MAE = (1/n) × Σ|y_true - y_pred|")
        abs_errors = np.abs(y_true - y_pred)
        print(f"Sum of absolute errors: {np.sum(abs_errors):.2f}")
        print(f"MAE = {np.sum(abs_errors):.2f} / {n} = {metrics['mae']:.2f}{unit_label}")
        
        # RMSE computation
        print(f"\n--- RMSE (Root Mean Squared Error) ---")
        print(f"Formula: RMSE = √[(1/n) × Σ(y_true - y_pred)²]")
        squared_errors = (y_true - y_pred) ** 2
        print(f"Sum of squared errors: {np.sum(squared_errors):.2f}")
        print(f"Mean squared error: {np.sum(squared_errors):.2f} / {n} = {np.mean(squared_errors):.2f}")
        print(f"RMSE = √{np.mean(squared_errors):.2f} = {metrics['rmse']:.2f}{unit_label}")
        
        # R² computation
        print(f"\n--- R² (Coefficient of Determination) ---")
        print(f"Formula: R² = 1 - (SS_res / SS_tot)")
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        print(f"SS_res (residual sum of squares): {ss_res:.2f}")
        print(f"SS_tot (total sum of squares): {ss_tot:.2f}")
        print(f"R² = 1 - ({ss_res:.2f} / {ss_tot:.2f}) = {metrics['r2']:.4f}")
        print(f"Interpretation: Model explains {metrics['r2']*100:.2f}% of variance")
    else:
        print(f"MAE{unit_label}: {metrics['mae']:.2f}")
        print(f"RMSE{unit_label}: {metrics['rmse']:.2f}")
        print(f"R²: {metrics['r2']:.4f}")


def print_classification_metrics(
    metrics: Dict[str, float],
    title: str = "Classification Metrics",
    show_computation: bool = False,
    y_true: np.ndarray = None,
    y_pred: np.ndarray = None,
) -> None:
    """
    Print classification metrics in a formatted way.
    
    Args:
        metrics: Dictionary with accuracy key
        title: Title to display
        show_computation: If True, show detailed computation steps
        y_true: Ground truth labels (needed if show_computation=True)
        y_pred: Predicted labels (needed if show_computation=True)
    """
    print(f"\n=== {title} ===")
    
    if show_computation and y_true is not None and y_pred is not None:
        n = len(y_true)
        print(f"\nNumber of samples: {n}")
        
        print(f"\n--- Accuracy Computation ---")
        print(f"Formula: Accuracy = (Number of correct predictions) / (Total predictions)")
        correct = np.sum(y_true == y_pred)
        print(f"Correct predictions: {correct}")
        print(f"Total predictions: {n}")
        print(f"Accuracy = {correct} / {n} = {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    else:
        print(f"Accuracy: {metrics['accuracy']:.4f}")


def compute_and_print_all_metrics(
    y_true_reg: np.ndarray,
    y_pred_reg: np.ndarray,
    y_true_cls: np.ndarray,
    y_pred_cls: np.ndarray,
    reg_title: str = "Shelf-Life Regression Evaluation",
    cls_title: str = "Ripeness Classification Evaluation",
    show_computation: bool = False,
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Compute and print both regression and classification metrics.
    
    Args:
        y_true_reg: Ground truth regression targets
        y_pred_reg: Predicted regression values
        y_true_cls: Ground truth classification labels
        y_pred_cls: Predicted classification labels
        reg_title: Title for regression metrics
        cls_title: Title for classification metrics
        show_computation: If True, show detailed computation steps with actual numbers
        
    Returns:
        Tuple of (regression_metrics, classification_metrics)
    """
    reg_metrics = compute_regression_metrics(y_true_reg, y_pred_reg)
    cls_metrics = compute_classification_metrics(y_true_cls, y_pred_cls)
    
    print_regression_metrics(
        reg_metrics, 
        title=reg_title,
        show_computation=show_computation,
        y_true=y_true_reg,
        y_pred=y_pred_reg,
    )
    print_classification_metrics(
        cls_metrics, 
        title=cls_title,
        show_computation=show_computation,
        y_true=y_true_cls,
        y_pred=y_pred_cls,
    )
    
    return reg_metrics, cls_metrics


if __name__ == "__main__":
    """
    Demo using the actual merged_avocado_dataset.csv
    Uses the same training logic as shelf_life_model.py
    """
    import pandas as pd
    from pathlib import Path
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from typing import Dict
    
    print("=" * 80)
    print("SHELF-LIFE MODEL METRICS COMPUTATION - Using Real Dataset")
    print("=" * 80)
    
    # Constants (same as shelf_life_model.py)
    CSV_PATH = "merged_avocado_dataset.csv"
    FEATURE_COLUMNS = ["gas_resistance", "co2", "temperature", "humidity", "pressure"]
    ID_COLUMN = "avocado_id"
    LABEL_COLUMN = "ripeness_label"
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    
    # Load CSV
    csv_path = Path(CSV_PATH)
    if not csv_path.exists():
        print(f"\nError: {CSV_PATH} not found!")
        print("Please run this script from the ML directory.")
        exit(1)
    
    print(f"\nLoading dataset: {CSV_PATH}")
    df = pd.read_csv(csv_path)
    
    # Standardize columns (simplified version)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Convert to numeric
    for col in FEATURE_COLUMNS + ["time_hours", LABEL_COLUMN]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Build remaining_hours target (same logic as shelf_life_model.py)
    print("\nBuilding remaining_hours target...")
    required = [ID_COLUMN, "time_hours", LABEL_COLUMN] + FEATURE_COLUMNS
    df = df.dropna(subset=required).copy()
    
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
    
    print(f"Dataset shape after processing: {df.shape}")
    
    # Prepare features and targets
    X = df[FEATURE_COLUMNS].copy()
    y_reg = df["remaining_hours"].copy()
    y_cls = df[LABEL_COLUMN].astype(int).copy()
    
    # Split data (same as shelf_life_model.py)
    X_train, X_test, y_train_reg, y_test_reg, y_train_cls, y_test_cls = train_test_split(
        X, y_reg, y_cls,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_cls,
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train regression model (shelf-life prediction)
    print("\nTraining shelf-life regression model...")
    reg_model = RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    reg_model.fit(X_train, y_train_reg)
    reg_preds = reg_model.predict(X_test)
    
    # Train classification model (ripeness prediction)
    print("Training ripeness classification model...")
    cls_model = RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    cls_model.fit(X_train, y_train_cls)
    cls_preds = cls_model.predict(X_test)
    
    # Show ALL test data predictions
    print("\n" + "=" * 80)
    print(f"ALL {len(X_test)} TEST SAMPLES - PREDICTIONS")
    print("=" * 80)
    print("\nREGRESSION (Remaining Hours):")
    print(f"{'#':<5} {'True (hrs)':<12} {'Pred (hrs)':<12} {'Error (hrs)':<12}")
    print("-" * 45)
    for i in range(len(y_test_reg)):
        error = abs(y_test_reg.iloc[i] - reg_preds[i])
        print(f"{i+1:<5} {y_test_reg.iloc[i]:<12.2f} {reg_preds[i]:<12.2f} {error:<12.2f}")
    
    print("\n" + "=" * 80)
    print("\nCLASSIFICATION (Ripeness Label):")
    print(f"{'#':<5} {'True':<8} {'Pred':<8} {'Match':<8}")
    print("-" * 30)
    for i in range(len(y_test_cls)):
        match = "✓" if y_test_cls.iloc[i] == cls_preds[i] else "✗"
        print(f"{i+1:<5} {y_test_cls.iloc[i]:<8} {cls_preds[i]:<8} {match:<8}")
    
    # Show metrics WITH detailed computation
    print("\n" + "=" * 80)
    print("DETAILED METRICS COMPUTATION")
    print("=" * 80)
    reg_metrics, cls_metrics = compute_and_print_all_metrics(
        y_test_reg.values,
        reg_preds,
        y_test_cls.values,
        cls_preds,
        show_computation=True,
    )
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Regression - MAE: {reg_metrics['mae']:.2f} hours, RMSE: {reg_metrics['rmse']:.2f} hours, R²: {reg_metrics['r2']:.4f}")
    print(f"Classification - Accuracy: {cls_metrics['accuracy']:.4f} ({cls_metrics['accuracy']*100:.2f}%)")
    print("=" * 80)
