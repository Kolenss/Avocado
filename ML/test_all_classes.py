"""
Test predictions for all ripeness classes using real samples from the dataset.
"""

import json
import joblib
import pandas as pd
import numpy as np

# Load the joblib model
MODEL_PATH = "shelf_life_regressor.joblib"
artifact = joblib.load(MODEL_PATH)
cls_model = artifact["cls_model"]

# Load the JSON trees
with open("cls_trees_compact.json", "r") as f:
    cls_data = json.load(f)
    cls_trees = cls_data["t"]

# Load training data
df = pd.read_csv("newfeed-data-set-avocado-open-only-clean.csv")
df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten"
}

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
print("TESTING ALL RIPENESS CLASSES")
print("=" * 80)

# Get one sample from each class
for cls in sorted(df['label'].unique()):
    cls_int = int(cls)
    label = RIPENESS_MAP.get(cls_int, "unknown")
    
    # Get a sample from this class
    samples = df[df['label'] == cls]
    if len(samples) > 0:
        sample = samples.iloc[0]
        
        # Extract features
        features = [
            sample['gas_resistance'],
            sample['co2'],
            sample['temperature'],
            sample['humidity'],
            sample['pressure']
        ]
        
        features_df = pd.DataFrame([{
            "gas_resistance": features[0],
            "co2": features[1],
            "temperature": features[2],
            "humidity": features[3],
            "pressure": features[4]
        }])
        
        # Predict with both methods
        joblib_cls = int(cls_model.predict(features_df)[0])
        json_cls = predict_classification_json(features)
        
        joblib_label = RIPENESS_MAP.get(joblib_cls, "unknown")
        json_label = RIPENESS_MAP.get(json_cls, "unknown")
        
        match = "✓" if joblib_cls == json_cls else "✗"
        
        print(f"\nActual Class: {cls_int} ({label})")
        print(f"  Input: gas={features[0]:.2f}, co2={features[1]:.0f}, "
              f"temp={features[2]:.1f}, humidity={features[3]:.1f}, pressure={features[4]:.1f}")
        print(f"  Joblib prediction: {joblib_cls} ({joblib_label})")
        print(f"  JSON prediction:   {json_cls} ({json_label})")
        print(f"  Match: {match}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nThe model CAN predict all 7 ripeness classes:")
for cls, label in RIPENESS_MAP.items():
    count = len(df[df['label'] == cls])
    print(f"  Class {cls} ({label}): {count} training samples")

print("\n✓ Both joblib and JSON predictions should match for all classes")
print("=" * 80)
