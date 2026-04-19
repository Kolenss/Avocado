"""
Check if the JSON files in assets match the current model
"""

import json
import joblib

print("Checking JSON files in assets folder...")

# Load the current model
artifact = joblib.load("shelf_life_regressor.joblib")
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]

print(f"\nCurrent model:")
print(f"  Regression trees: {len(reg_model.estimators_)}")
print(f"  Classification trees: {len(cls_model.estimators_)}")

# Load JSON files
with open("../assets/reg_trees_compact.json", "r") as f:
    reg_json = json.load(f)

with open("../assets/cls_trees_compact.json", "r") as f:
    cls_json = json.load(f)

print(f"\nJSON files in assets:")
print(f"  Regression trees: {len(reg_json)}")
print(f"  Classification trees: {len(cls_json['t'])}")
print(f"  Classes: {cls_json['c']}")

if len(reg_json) == len(reg_model.estimators_):
    print("\n✓ Regression JSON matches model")
else:
    print("\n✗ Regression JSON DOES NOT match model!")

if len(cls_json['t']) == len(cls_model.estimators_):
    print("✓ Classification JSON matches model")
else:
    print("✗ Classification JSON DOES NOT match model!")

print("\n" + "=" * 80)
print("Testing prediction with JSON trees (simulating app behavior)")
print("=" * 80)

# Simulate what the app does
def predict_cls_from_json(features):
    """Simulate app's classification prediction"""
    votes = {}
    for tree in cls_json['t']:
        node = len(tree) - 1  # root is last node
        while len(tree[node]) == 4:
            feat, thr, left, right = tree[node]
            node = left if features[feat] <= thr else right
        cls = tree[node][0]
        votes[cls] = votes.get(cls, 0) + 1
    return max(votes, key=votes.get)

def predict_reg_from_json(features):
    """Simulate app's regression prediction"""
    total = 0
    for tree in reg_json:
        node = len(tree) - 1
        while len(tree[node]) == 4:
            feat, thr, left, right = tree[node]
            node = left if features[feat] <= thr else right
        total += tree[node][0]
    return total / len(reg_json)

# Test with user's values
# [gas_resistance, co2, temperature, humidity, pressure]
features = [239.4, 1158.0, 31.3, 74.6, 1004.0]

print(f"\nTest values: {features}")

cls_pred = predict_cls_from_json(features)
reg_pred = predict_reg_from_json(features)
shelf_life = 0 if cls_pred >= 4 else max(0, reg_pred)

RIPENESS_MAP = {0: "unripe", 1: "near ripe", 2: "ripe", 3: "very ripe", 4: "overripe", 5: "molds", 6: "rotten"}

print(f"\nPrediction from JSON (what app should show):")
print(f"  Ripeness: {RIPENESS_MAP[cls_pred]} (class {cls_pred})")
print(f"  Shelf Life: {shelf_life:.2f} hours ({shelf_life/24:.2f} days)")

print(f"\nUser's app shows:")
print(f"  Ripeness: unripe")
print(f"  Shelf Life: 68 hours (2.8 days)")

if cls_pred == 0 and abs(shelf_life - 68) < 5:
    print("\n✗ JSON files match what app shows - OLD MODEL!")
    print("The JSON files in assets/ are still the OLD model.")
elif cls_pred == 4:
    print("\n✓ JSON files are NEW MODEL!")
    print("The app is not loading these files correctly.")
