"""
Test predict_cli.py predictions to verify they match expected values
"""

import joblib
from shelf_life_model import MODEL_PATH, predict_remaining_hours, predict_ripeness_label

print("=" * 80)
print("TESTING CLI PREDICTIONS")
print("=" * 80)

artifact = joblib.load(MODEL_PATH)
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]

# Test samples (same as in retrain script)
test_samples = [
    {
        "name": "Sample 1 - Unripe",
        "gas": 314.6,
        "co2": 5000,
        "temp": 28.6,
        "hum": 75.3,
        "press": 1008.5,
    },
    {
        "name": "Sample 2 - Unripe",
        "gas": 408.5,
        "co2": 3215,
        "temp": 28.5,
        "hum": 76.4,
        "press": 1008.7,
    },
    {
        "name": "Sample 3 - Near Ripe",
        "gas": 205.9,
        "co2": 4377,
        "temp": 29.8,
        "hum": 88.3,
        "press": 1006.2,
    },
    {
        "name": "Sample 4 - Ripe",
        "gas": 300.0,
        "co2": 4000,
        "temp": 29.5,
        "hum": 80.0,
        "press": 1007.0,
    },
]

print("\nRunning predictions (feature order: gas, co2, temp, hum, press):\n")

for sample in test_samples:
    # Feature order: gas_resistance, co2, temperature, humidity, pressure
    features = [sample["gas"], sample["co2"], sample["temp"], sample["hum"], sample["press"]]
    
    raw_hours = predict_remaining_hours(reg_model, features)
    pred_class, pred_label = predict_ripeness_label(cls_model, features)
    
    # Apply clamping rule: overripe/molds/rotten = 0 remaining
    remaining_hours = 0 if pred_class >= 4 else raw_hours
    remaining_days = remaining_hours / 24
    
    print(f"{sample['name']}")
    print(f"  Input: Gas={sample['gas']}, CO2={sample['co2']}, Temp={sample['temp']}, Hum={sample['hum']}, Press={sample['press']}")
    print(f"  Ripeness: {pred_label} (class {pred_class})")
    print(f"  Shelf Life: {remaining_hours:.2f} hours ({remaining_days:.2f} days)")
    print()

print("=" * 80)
print("Use these exact values to test in your app!")
print("The app predictions should match these CLI predictions.")
print("=" * 80)
