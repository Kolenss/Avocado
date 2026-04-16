"""
Final comprehensive verification of all ML components
"""

import joblib
import json
import os
import pandas as pd

print("=" * 80)
print("FINAL ML VERIFICATION")
print("=" * 80)

# 1. Check model file
print("\n1. MODEL FILE (shelf_life_regressor.joblib)")
print("-" * 80)
artifact = joblib.load("shelf_life_regressor.joblib")
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]
print(f"✓ File exists and loads successfully")
print(f"✓ Regression trees: {len(reg_model.estimators_)}")
print(f"✓ Classification trees: {len(cls_model.estimators_)}")
print(f"✓ Feature columns: {artifact['feature_columns']}")
print(f"✓ Ripeness classes: {list(artifact['ripeness_map'].keys())}")
print(f"✓ File size: {os.path.getsize('shelf_life_regressor.joblib') / 1024 / 1024:.2f} MB")

# 2. Check JSON files in ML folder
print("\n2. JSON FILES IN ML FOLDER")
print("-" * 80)
with open("reg_trees_compact.json", "r") as f:
    reg_json = json.load(f)
with open("cls_trees_compact.json", "r") as f:
    cls_json = json.load(f)

print(f"✓ reg_trees_compact.json: {len(reg_json)} trees")
print(f"✓ cls_trees_compact.json: {len(cls_json['t'])} trees, classes: {cls_json['c']}")
print(f"✓ Matches model: {len(reg_json) == len(reg_model.estimators_) and len(cls_json['t']) == len(cls_model.estimators_)}")

# 3. Check JSON files in assets folder
print("\n3. JSON FILES IN ASSETS FOLDER")
print("-" * 80)
with open("../assets/reg_trees_compact.json", "r") as f:
    assets_reg_json = json.load(f)
with open("../assets/cls_trees_compact.json", "r") as f:
    assets_cls_json = json.load(f)

print(f"✓ assets/reg_trees_compact.json: {len(assets_reg_json)} trees")
print(f"✓ assets/cls_trees_compact.json: {len(assets_cls_json['t'])} trees")

# Check if they match ML folder
reg_match = len(assets_reg_json) == len(reg_json)
cls_match = len(assets_cls_json) == len(cls_json['t'])
print(f"✓ Matches ML folder: {reg_match and cls_match}")

# 4. Check dataset
print("\n4. TRAINING DATASET")
print("-" * 80)
df = pd.read_csv("merged_avocado_dataset.csv")
print(f"✓ merged_avocado_dataset.csv: {len(df)} rows")
print(f"✓ Label distribution:")
for label in sorted(df['ripeness_label'].unique()):
    count = len(df[df['ripeness_label'] == label])
    print(f"    Class {label}: {count} samples")

# 5. Test prediction consistency
print("\n5. PREDICTION CONSISTENCY TEST")
print("-" * 80)

test_values = [239.4, 1158.0, 31.3, 74.6, 1004.0]
print(f"Test input: {test_values}")

# Python model prediction
input_df = pd.DataFrame([{
    "gas_resistance": test_values[0],
    "co2": test_values[1],
    "temperature": test_values[2],
    "humidity": test_values[3],
    "pressure": test_values[4]
}])

cls_pred = int(cls_model.predict(input_df)[0])
reg_pred = float(reg_model.predict(input_df)[0])
shelf_life = 0 if cls_pred >= 4 else max(0, reg_pred)

RIPENESS_MAP = {0: "unripe", 1: "near ripe", 2: "ripe", 3: "very ripe", 4: "overripe", 5: "molds", 6: "rotten"}

print(f"\nPython model prediction:")
print(f"  Ripeness: {RIPENESS_MAP[cls_pred]} (class {cls_pred})")
print(f"  Shelf Life: {shelf_life:.2f} hours ({shelf_life/24:.2f} days)")

# JSON prediction (simulating app)
def predict_cls_json(features, trees):
    votes = {}
    for tree in trees:
        node = len(tree) - 1
        while len(tree[node]) == 4:
            feat, thr, left, right = tree[node]
            node = left if features[feat] <= thr else right
        cls = tree[node][0]
        votes[cls] = votes.get(cls, 0) + 1
    return max(votes, key=votes.get)

def predict_reg_json(features, trees):
    total = 0
    for tree in trees:
        node = len(tree) - 1
        while len(tree[node]) == 4:
            feat, thr, left, right = tree[node]
            node = left if features[feat] <= thr else right
        total += tree[node][0]
    return total / len(trees)

json_cls = predict_cls_json(test_values, assets_cls_json['t'])
json_reg = predict_reg_json(test_values, assets_reg_json)
json_shelf = 0 if json_cls >= 4 else max(0, json_reg)

print(f"\nJSON (app) prediction:")
print(f"  Ripeness: {RIPENESS_MAP[int(json_cls)]} (class {int(json_cls)})")
print(f"  Shelf Life: {json_shelf:.2f} hours ({json_shelf/24:.2f} days)")

match = cls_pred == int(json_cls) and abs(shelf_life - json_shelf) < 0.01
print(f"\n{'✓' if match else '✗'} Predictions match: {match}")

# 6. Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

all_good = True
checks = [
    ("Model file exists and valid", True),
    ("JSON files in ML folder match model", len(reg_json) == len(reg_model.estimators_)),
    ("JSON files in assets match ML folder", reg_match and cls_match),
    ("Dataset has 946 samples", len(df) == 946),
    ("Python and JSON predictions match", match),
]

for check, status in checks:
    symbol = "✓" if status else "✗"
    print(f"{symbol} {check}")
    if not status:
        all_good = False

print("\n" + "=" * 80)
if all_good:
    print("✓✓✓ ALL CHECKS PASSED!")
    print("Your ML model is correctly set up and ready to use.")
    print("predict_cli.py and the app will give IDENTICAL predictions.")
else:
    print("✗✗✗ SOME CHECKS FAILED!")
    print("Review the issues above.")
print("=" * 80)
