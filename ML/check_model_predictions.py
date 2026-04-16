"""
Check if the model can predict all ripeness classes.
"""

import joblib
import pandas as pd
import numpy as np

MODEL_PATH = "shelf_life_regressor.joblib"
artifact = joblib.load(MODEL_PATH)
cls_model = artifact["cls_model"]

RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten"
}

print("=" * 80)
print("MODEL CLASS PREDICTION CHECK")
print("=" * 80)

# Load training data to see what the model was trained on
print("\nLoading training data...")
df = pd.read_csv("newfeed-data-set-avocado-open-only-clean.csv")

# Standardize column names
df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

print(f"Dataset shape: {df.shape}")
print(f"\nColumn names: {df.columns.tolist()}")

# Check if label column exists
if 'label' in df.columns:
    print(f"\nClass distribution in training data:")
    class_counts = df['label'].value_counts().sort_index()
    for cls, count in class_counts.items():
        label = RIPENESS_MAP.get(int(cls), "unknown")
        print(f"  Class {int(cls)} ({label}): {count} samples")
    
    # Get sample data for each class
    print("\n" + "=" * 80)
    print("TESTING PREDICTIONS FOR EACH CLASS")
    print("=" * 80)
    
    for cls in sorted(df['label'].unique()):
        cls_int = int(cls)
        label = RIPENESS_MAP.get(cls_int, "unknown")
        
        # Get a sample from this class
        samples = df[df['label'] == cls]
        if len(samples) > 0:
            sample = samples.iloc[0]
            
            # Extract features
            features = pd.DataFrame([{
                "gas_resistance": sample.get('gas_resistance', 0),
                "co2": sample.get('co2', 0),
                "temperature": sample.get('temperature', 0),
                "humidity": sample.get('humidity', 0),
                "pressure": sample.get('pressure', 0)
            }])
            
            # Predict
            pred_cls = int(cls_model.predict(features)[0])
            pred_label = RIPENESS_MAP.get(pred_cls, "unknown")
            
            match = "✓" if pred_cls == cls_int else "✗"
            
            print(f"\nClass {cls_int} ({label}):")
            print(f"  Input: gas={sample.get('gas_resistance', 0):.2f}, co2={sample.get('co2', 0):.0f}, "
                  f"temp={sample.get('temperature', 0):.1f}, humidity={sample.get('humidity', 0):.1f}, "
                  f"pressure={sample.get('pressure', 0):.1f}")
            print(f"  Predicted: {pred_cls} ({pred_label}) {match}")
else:
    print("\nERROR: 'label' column not found in dataset!")
    print(f"Available columns: {df.columns.tolist()}")

# Test with extreme values to see if we can trigger different classes
print("\n" + "=" * 80)
print("TESTING WITH EXTREME VALUES")
print("=" * 80)

extreme_tests = [
    {
        "name": "Very low gas, high CO2 (should be rotten)",
        "gas_resistance": 50.0,
        "co2": 5000,
        "temperature": 35.0,
        "humidity": 90.0,
        "pressure": 1000.0
    },
    {
        "name": "Very high gas, low CO2 (should be unripe)",
        "gas_resistance": 1000.0,
        "co2": 300,
        "temperature": 20.0,
        "humidity": 50.0,
        "pressure": 1015.0
    },
    {
        "name": "Medium values (should be ripe/near ripe)",
        "gas_resistance": 500.0,
        "co2": 800,
        "temperature": 28.0,
        "humidity": 65.0,
        "pressure": 1012.0
    }
]

for test in extreme_tests:
    features = pd.DataFrame([{
        "gas_resistance": test["gas_resistance"],
        "co2": test["co2"],
        "temperature": test["temperature"],
        "humidity": test["humidity"],
        "pressure": test["pressure"]
    }])
    
    pred_cls = int(cls_model.predict(features)[0])
    pred_label = RIPENESS_MAP.get(pred_cls, "unknown")
    
    print(f"\n{test['name']}:")
    print(f"  Input: gas={test['gas_resistance']}, co2={test['co2']}, "
          f"temp={test['temperature']}, humidity={test['humidity']}, "
          f"pressure={test['pressure']}")
    print(f"  Predicted: {pred_cls} ({pred_label})")

print("\n" + "=" * 80)
