"""
Test script to verify that predict_cli.py and the app's JSON-based prediction
produce the same results for the same input values.
"""

import json
import joblib
import numpy as np

# Load the joblib model
MODEL_PATH = "shelf_life_regressor.joblib"
artifact = joblib.load(MODEL_PATH)
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]

# Load the JSON trees
with open("cls_trees_compact.json", "r") as f:
    cls_data = json.load(f)
    cls_trees = cls_data["t"]
    cls_classes = cls_data["c"]

with open("reg_trees_compact.json", "r") as f:
    reg_trees = json.load(f)

# Test cases with same values
test_cases = [
    {
        "name": "Test 1 - Ripe avocado",
        "gas_resistance": 453.63,
        "co2": 1020,
        "temperature": 31.5,
        "humidity": 67.1,
        "pressure": 1012.4
    },
    {
        "name": "Test 2 - Unripe avocado",
        "gas_resistance": 800.0,
        "co2": 400,
        "temperature": 25.0,
        "humidity": 60.0,
        "pressure": 1013.0
    },
    {
        "name": "Test 3 - Overripe avocado",
        "gas_resistance": 200.0,
        "co2": 2000,
        "temperature": 30.0,
        "humidity": 75.0,
        "pressure": 1010.0
    }
]

def predict_with_json_tree(tree, features):
    """Traverse a single tree to get prediction."""
    node_idx = len(tree) - 1  # Start from root (last node)
    
    while len(tree[node_idx]) > 1:  # Not a leaf
        feature_idx, threshold, left_idx, right_idx = tree[node_idx]
        if features[int(feature_idx)] <= threshold:
            node_idx = left_idx
        else:
            node_idx = right_idx
    
    return tree[node_idx][0]  # Return leaf value

def predict_regression_json(features):
    """Predict using JSON regression trees."""
    predictions = [predict_with_json_tree(tree, features) for tree in reg_trees]
    return np.mean(predictions)

def predict_classification_json(features):
    """Predict using JSON classification trees."""
    predictions = [predict_with_json_tree(tree, features) for tree in cls_trees]
    # Get most common prediction
    counts = {}
    for pred in predictions:
        pred_int = int(pred)
        counts[pred_int] = counts.get(pred_int, 0) + 1
    return max(counts, key=counts.get)

print("=" * 80)
print("PREDICTION COMPARISON TEST")
print("=" * 80)

for test in test_cases:
    print(f"\n{test['name']}")
    print("-" * 80)
    
    # Prepare features in correct order
    features = [
        test["gas_resistance"],
        test["co2"],
        test["temperature"],
        test["humidity"],
        test["pressure"]
    ]
    
    print(f"Input: gas_resistance={test['gas_resistance']}, co2={test['co2']}, "
          f"temp={test['temperature']}, humidity={test['humidity']}, "
          f"pressure={test['pressure']}")
    
    # Predict with joblib model (predict_cli.py method)
    import pandas as pd
    sample_df = pd.DataFrame([features], columns=["gas_resistance", "co2", "temperature", "humidity", "pressure"])
    
    joblib_reg = float(reg_model.predict(sample_df)[0])
    joblib_cls = int(cls_model.predict(sample_df)[0])
    
    # Predict with JSON trees (app method)
    json_reg = predict_regression_json(features)
    json_cls = predict_classification_json(features)
    
    # Compare results
    print(f"\nJoblib Model (predict_cli.py):")
    print(f"  Classification: {joblib_cls}")
    print(f"  Regression: {joblib_reg:.2f} hours")
    
    print(f"\nJSON Trees (app):")
    print(f"  Classification: {json_cls}")
    print(f"  Regression: {json_reg:.2f} hours")
    
    print(f"\nMatch Status:")
    cls_match = joblib_cls == json_cls
    reg_diff = abs(joblib_reg - json_reg)
    reg_match = reg_diff < 0.01  # Allow tiny floating point differences
    
    print(f"  Classification Match: {'✓ YES' if cls_match else '✗ NO'}")
    print(f"  Regression Match: {'✓ YES' if reg_match else f'✗ NO (diff: {reg_diff:.4f})'}")
    
    if cls_match and reg_match:
        print(f"  Overall: ✓ PREDICTIONS MATCH")
    else:
        print(f"  Overall: ✗ PREDICTIONS DO NOT MATCH")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
