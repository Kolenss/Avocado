"""
Merge synthetic_avocado_dataset.csv with newfeed-data-set-avocado-open-only-clean.csv
and retrain the model with the combined dataset.
"""

import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error, r2_score, classification_report

# File paths
CURRENT_CSV = "newfeed-data-set-avocado-open-only-clean.csv"
SYNTHETIC_CSV = "synthetic_avocado_dataset.csv"
MERGED_CSV = "merged_avocado_dataset.csv"
MODEL_PATH = "shelf_life_regressor.joblib"

FEATURE_COLUMNS = ["gas_resistance", "co2", "temperature", "humidity", "pressure"]
RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten",
}

def standardize_columns(df):
    """Standardize column names to lowercase with underscores"""
    rename_map = {
        'Avocado ID': 'avocado_id',
        'Temperature': 'temperature',
        'Humidity': 'humidity',
        'Pressure': 'pressure',
        'Gas Resistance': 'gas_resistance',
        'CO2': 'co2',
        'Day': 'day',
        'Label': 'ripeness_label',
        'Time': 'time_hours',
        'BOX TYPE': 'box_type'
    }
    return df.rename(columns=rename_map)

def merge_datasets():
    """Merge current and synthetic datasets"""
    print("=" * 80)
    print("STEP 1: LOADING DATASETS")
    print("=" * 80)
    
    current = pd.read_csv(CURRENT_CSV)
    synthetic = pd.read_csv(SYNTHETIC_CSV)
    
    print(f"\nCurrent dataset: {len(current)} rows")
    print(f"Synthetic dataset: {len(synthetic)} rows")
    
    # Standardize column names
    current = standardize_columns(current)
    synthetic = standardize_columns(synthetic)
    
    # Add box_type to synthetic if missing (default to 1)
    if 'box_type' not in synthetic.columns:
        synthetic['box_type'] = 1
        print("\nAdded 'box_type' column to synthetic dataset (default=1)")
    
    # Adjust avocado IDs in synthetic to avoid conflicts
    max_id = current['avocado_id'].max()
    synthetic['avocado_id'] = synthetic['avocado_id'] + max_id
    print(f"\nAdjusted synthetic avocado IDs to start from {max_id + 1}")
    
    # Merge datasets
    merged = pd.concat([current, synthetic], ignore_index=True)
    
    print(f"\n{'=' * 80}")
    print(f"MERGED DATASET: {len(merged)} rows")
    print(f"{'=' * 80}")
    
    # Show label distribution
    print("\nLabel distribution:")
    print(merged['ripeness_label'].value_counts().sort_index())
    
    # Save merged dataset
    merged.to_csv(MERGED_CSV, index=False)
    print(f"\nSaved merged dataset to: {MERGED_CSV}")
    
    return merged

def build_remaining_hours_target(df):
    """Build regression target: remaining hours until rotten"""
    grouped = df.groupby('avocado_id', sort=False)
    end_time_map = {}
    
    for avocado_id, g in grouped:
        g_sorted = g.sort_values('time_hours')
        rotten_rows = g_sorted[g_sorted['ripeness_label'] == 6]
        if len(rotten_rows) > 0:
            end_time = float(rotten_rows['time_hours'].iloc[0])
        else:
            end_time = float(g_sorted['time_hours'].max())
        end_time_map[avocado_id] = end_time
    
    df['end_time_hours'] = df['avocado_id'].map(end_time_map)
    df['remaining_hours'] = (df['end_time_hours'] - df['time_hours']).clip(lower=0)
    return df

def train_models(df):
    """Train both regression and classification models"""
    print("\n" + "=" * 80)
    print("STEP 2: TRAINING MODELS")
    print("=" * 80)
    
    # Prepare data
    required = FEATURE_COLUMNS + ['avocado_id', 'ripeness_label', 'time_hours']
    for col in required:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=required).copy()
    df = build_remaining_hours_target(df)
    
    X = df[FEATURE_COLUMNS].copy()
    y_reg = df['remaining_hours'].copy()
    y_cls = df['ripeness_label'].astype(int).copy()
    
    print(f"\nTraining samples: {len(X)}")
    print(f"Features: {FEATURE_COLUMNS}")
    
    # Train-test split
    X_train, X_test, y_train_reg, y_test_reg, y_train_cls, y_test_cls = train_test_split(
        X, y_reg, y_cls,
        test_size=0.2,
        random_state=42,
        stratify=y_cls
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train regression model
    print("\n" + "-" * 80)
    print("Training Regression Model (Shelf Life Prediction)...")
    print("-" * 80)
    
    reg_model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2
    )
    reg_model.fit(X_train, y_train_reg)
    
    reg_preds = reg_model.predict(X_test)
    mae = mean_absolute_error(y_test_reg, reg_preds)
    rmse = float(np.sqrt(mean_squared_error(y_test_reg, reg_preds)))
    r2 = r2_score(y_test_reg, reg_preds)
    
    print(f"\nRegression Results:")
    print(f"  MAE: {mae:.2f} hours")
    print(f"  RMSE: {rmse:.2f} hours")
    print(f"  R²: {r2:.4f}")
    
    # Train classification model
    print("\n" + "-" * 80)
    print("Training Classification Model (Ripeness Prediction)...")
    print("-" * 80)
    
    cls_model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2
    )
    cls_model.fit(X_train, y_train_cls)
    
    cls_preds = cls_model.predict(X_test)
    cls_acc = accuracy_score(y_test_cls, cls_preds)
    
    print(f"\nClassification Results:")
    print(f"  Accuracy: {cls_acc:.4f}")
    
    print("\nClassification Report:")
    report = classification_report(
        y_test_cls, cls_preds,
        labels=list(RIPENESS_MAP.keys()),
        target_names=[RIPENESS_MAP[i] for i in RIPENESS_MAP.keys()],
        zero_division=0
    )
    print(report)
    
    # Save models
    artifact = {
        "reg_model": reg_model,
        "cls_model": cls_model,
        "feature_columns": FEATURE_COLUMNS,
        "ripeness_map": RIPENESS_MAP,
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"\n{'=' * 80}")
    print(f"✓ Models saved to: {MODEL_PATH}")
    print(f"{'=' * 80}")
    
    return reg_model, cls_model

def test_predictions(reg_model, cls_model):
    """Test predictions with sample data"""
    print("\n" + "=" * 80)
    print("STEP 3: TESTING PREDICTIONS")
    print("=" * 80)
    
    test_cases = [
        {"name": "Fresh (Unripe)", "gas": 450, "co2": 1000, "temp": 25, "humid": 60, "press": 1013},
        {"name": "Ripe", "gas": 350, "co2": 3000, "temp": 28, "humid": 70, "press": 1010},
        {"name": "Overripe", "gas": 280, "co2": 4500, "temp": 30, "humid": 80, "press": 1008},
        {"name": "Rotten", "gas": 250, "co2": 5000, "temp": 32, "humid": 85, "press": 1005},
    ]
    
    for test in test_cases:
        sample = pd.DataFrame([{
            "gas_resistance": test['gas'],
            "co2": test['co2'],
            "temperature": test['temp'],
            "humidity": test['humid'],
            "pressure": test['press']
        }])
        
        ripeness_class = int(cls_model.predict(sample)[0])
        ripeness_label = RIPENESS_MAP.get(ripeness_class, "unknown")
        
        raw_hours = float(reg_model.predict(sample)[0])
        shelf_life_hours = 0 if ripeness_class >= 4 else max(0, raw_hours)
        shelf_life_days = shelf_life_hours / 24.0
        
        print(f"\n{test['name']}:")
        print(f"  Sensors: Gas={test['gas']}, CO2={test['co2']}, Temp={test['temp']}°C")
        print(f"  Prediction: {ripeness_label} (class {ripeness_class})")
        print(f"  Shelf Life: {shelf_life_hours:.1f} hours ({shelf_life_days:.2f} days)")

def main():
    print("\n" + "=" * 80)
    print("MERGE DATASETS AND RETRAIN MODEL")
    print("=" * 80)
    
    # Step 1: Merge datasets
    merged_df = merge_datasets()
    
    # Step 2: Train models
    reg_model, cls_model = train_models(merged_df)
    
    # Step 3: Test predictions
    test_predictions(reg_model, cls_model)
    
    print("\n" + "=" * 80)
    print("✓✓✓ COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Test the new model: python predict_cli.py")
    print("2. Export to JSON for app: python export_trees_to_json.py")
    print("3. Copy JSON files to assets/ folder")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
