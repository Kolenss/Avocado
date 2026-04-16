"""
Verify that app predictions (using JSON trees) match CLI predictions (using joblib).
This simulates the exact logic used in routes/prediction.ts
"""

import json
import joblib
from shelf_life_model import MODEL_PATH, predict_remaining_hours, predict_ripeness_label

print("=" * 80)
print("VERIFYING APP AND CLI PREDICTIONS MATCH")
print("=" * 80)

# Load joblib model (CLI method)
print("\n[1] Loading joblib model (CLI method)...")
artifact = joblib.load(MODEL_PATH)
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]
print("  ✓ Loaded")

# Load JSON trees (App method)
print("\n[2] Loading JSON trees (App method)...")
with open("reg_trees_compact.json", "r") as f:
    reg_trees = json.load(f)
print(f"  ✓ Loaded {len(reg_trees)} regression trees")

with open("cls_trees_compact.json", "r") as f:
    cls_data = json.load(f)
    cls_trees = cls_data["t"]
    cls_classes = cls_data["c"]
print(f"  ✓ Loaded {len(cls_trees)} classification trees")

# Implement app's prediction logic
def predict_reg_from_json(features):
    """Simulate app's regression prediction using JSON trees."""
    total = 0
    for tree in reg_trees:
        node_idx = len(tree) - 1  # Root is last node (post-order)
        while len(tree[node_idx]) == 4:  # Internal node
            feat_idx, threshold, left, right = tree[node_idx]
            node_idx = left if features[feat_idx] <= threshold else right
        # Leaf node
        total += tree[node_idx][0]
    return total / len(reg_trees)

def predict_cls_from_json(features):
    """Simulate app's classification prediction using JSON trees."""
    votes = {}
    for tree in cls_trees:
        node_idx = len(tree) - 1  # Root is last node (post-order)
        while len(tree[node_idx]) == 4:  # Internal node
            feat_idx, threshold, left, right = tree[node_idx]
            node_idx = left if features[feat_idx] <= threshold else right
        # Leaf node
        cls = int(tree[node_idx][0])
        votes[cls] = votes.get(cls, 0) + 1
    # Return class with most votes
    return max(votes.items(), key=lambda x: x[1])[0]

# Test samples
test_samples = [
    {
        "name": "Sample 1 - Unripe",
        "features": [314.6, 5000, 28.6, 75.3, 1008.5],
    },
    {
        "name": "Sample 2 - Unripe",
        "features": [408.5, 3215, 28.5, 76.4, 1008.7],
    },
    {
        "name": "Sample 3 - Near Ripe",
        "features": [205.9, 4377, 29.8, 88.3, 1006.2],
    },
    {
        "name": "Sample 4 - Ripe",
        "features": [300.0, 4000, 29.5, 80.0, 1007.0],
    },
]

RIPENESS_MAP = {
    0: "Unripe",
    1: "Near Ripe",
    2: "Ripe",
    3: "Very Ripe",
    4: "Overripe",
    5: "Molds",
    6: "Rotten",
}

print("\n[3] Running predictions and comparing...\n")
print("=" * 80)

all_match = True

for sample in test_samples:
    features = sample["features"]
    
    # CLI predictions (joblib)
    cli_hours = predict_remaining_hours(reg_model, features)
    cli_class, _ = predict_ripeness_label(cls_model, features)
    
    # App predictions (JSON)
    app_hours = predict_reg_from_json(features)
    app_class = predict_cls_from_json(features)
    
    # Apply clamping rule
    cli_hours_final = 0 if cli_class >= 4 else cli_hours
    app_hours_final = 0 if app_class >= 4 else app_hours
    
    # Check if they match (allow 0.1 hour tolerance for floating point precision)
    hours_match = abs(cli_hours_final - app_hours_final) < 0.1
    class_match = cli_class == app_class
    
    print(f"\n{sample['name']}")
    print(f"  Input: Gas={features[0]}, CO2={features[1]}, Temp={features[2]}, Hum={features[3]}, Press={features[4]}")
    print(f"\n  CLI (joblib):")
    print(f"    Ripeness: {RIPENESS_MAP[cli_class]} (class {cli_class})")
    print(f"    Shelf Life: {cli_hours_final:.2f} hours ({cli_hours_final/24:.2f} days)")
    print(f"\n  APP (JSON):")
    print(f"    Ripeness: {RIPENESS_MAP[app_class]} (class {app_class})")
    print(f"    Shelf Life: {app_hours_final:.2f} hours ({app_hours_final/24:.2f} days)")
    print(f"\n  Match Status:")
    print(f"    Ripeness: {'✓ MATCH' if class_match else '✗ MISMATCH'}")
    print(f"    Shelf Life: {'✓ MATCH' if hours_match else '✗ MISMATCH'}")
    
    if not (hours_match and class_match):
        all_match = False

print("\n" + "=" * 80)
if all_match:
    print("✓ SUCCESS: All predictions match between CLI and App!")
    print("Your app will produce the same results as predict_cli.py")
else:
    print("✗ WARNING: Some predictions don't match!")
    print("Check the implementation in routes/prediction.ts")
print("=" * 80)
