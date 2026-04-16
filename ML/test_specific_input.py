"""
Test the specific input that's showing different results
"""

import joblib
from shelf_life_model import MODEL_PATH, predict_remaining_hours, predict_ripeness_label

print("Testing input: [232.9, 1186.0, 30.0, 67.0, 1004.4]")
print("=" * 80)

# Load the NEW model
artifact = joblib.load(MODEL_PATH)
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]

# Test input: gas, co2, temp, humidity, pressure
features = [232.9, 1186.0, 30.0, 67.0, 1004.4]

raw_hours = predict_remaining_hours(reg_model, features)
pred_class, pred_label = predict_ripeness_label(cls_model, features)

# Apply clamping rule
remaining_hours = 0 if pred_class >= 4 else raw_hours
remaining_days = remaining_hours / 24

print(f"\nInput: {features}")
print(f"Predicted Class: {pred_class}")
print(f"Predicted Label: {pred_label}")
print(f"Raw Shelf Life: {raw_hours:.2f} hours")
print(f"Final Shelf Life: {remaining_hours:.2f} hours ({remaining_days:.2f} days)")

print("\n" + "=" * 80)
print("Expected from app: overripe (class 4)")
print(f"Actual from NEW model: {pred_label} (class {pred_class})")

if pred_class == 4:
    print("✓ MATCH - New model predicts overripe correctly!")
else:
    print("✗ MISMATCH - New model is NOT predicting overripe")
    print("This means the app is using OLD JSON trees!")
