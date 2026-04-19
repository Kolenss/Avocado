"""
Complete retraining pipeline with merged_avocado_dataset1.csv

Steps:
1. Train model with new dataset
2. Export trees to JSON
3. Copy JSON files to assets/
4. Run test predictions to verify
"""

import os
import shutil
from pathlib import Path

print("=" * 80)
print("RETRAINING WITH merged_avocado_dataset1.csv")
print("=" * 80)

# Step 1: Train the model
print("\n[1/4] Training model...")
from shelf_life_model import train
reg_model, cls_model, feature_columns, df = train()

# Step 2: Export trees to JSON
print("\n[2/4] Exporting trees to JSON...")
import json
import joblib
import numpy as np

MODEL_PATH = "shelf_life_regressor.joblib"

artifact = joblib.load(MODEL_PATH)
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]

def export_tree(tree, is_classifier=False):
    """Convert sklearn tree to compact JSON format."""
    nodes = []
    
    def traverse(node_id):
        if tree.feature[node_id] == -2:  # Leaf node
            if is_classifier:
                value = float(np.argmax(tree.value[node_id].flatten()))
            else:
                value = tree.value[node_id].flatten()[0]
            nodes.append([float(value)])
            return len(nodes) - 1
        
        # Internal node: [feature_index, threshold, left_child_id, right_child_id]
        left_id = traverse(tree.children_left[node_id])
        right_id = traverse(tree.children_right[node_id])
        
        nodes.append([
            int(tree.feature[node_id]),
            float(tree.threshold[node_id]),
            left_id,
            right_id
        ])
        return len(nodes) - 1
    
    traverse(0)
    return nodes

print("  Exporting regression trees...")
reg_trees = []
for estimator in reg_model.estimators_:
    tree_data = export_tree(estimator.tree_, is_classifier=False)
    reg_trees.append(tree_data)

with open("reg_trees_compact.json", "w") as f:
    json.dump(reg_trees, f, separators=(',', ':'))
print(f"    ✓ Saved: reg_trees_compact.json ({len(reg_trees)} trees)")

print("  Exporting classification trees...")
cls_trees = []
for estimator in cls_model.estimators_:
    tree_data = export_tree(estimator.tree_, is_classifier=True)
    cls_trees.append(tree_data)

cls_classes = cls_model.classes_.tolist()

with open("cls_trees_compact.json", "w") as f:
    json.dump({"t": cls_trees, "c": cls_classes}, f, separators=(',', ':'))
print(f"    ✓ Saved: cls_trees_compact.json ({len(cls_trees)} trees)")

# Step 3: Copy to assets/
print("\n[3/4] Copying JSON files to assets/...")
assets_dir = Path("../assets")
if not assets_dir.exists():
    print(f"  Warning: {assets_dir} not found, skipping copy")
else:
    shutil.copy("reg_trees_compact.json", assets_dir / "reg_trees_compact.json")
    shutil.copy("cls_trees_compact.json", assets_dir / "cls_trees_compact.json")
    print("    ✓ Copied to assets/")

# Step 4: Test predictions
print("\n[4/4] Testing predictions...")
from shelf_life_model import predict_remaining_hours, predict_ripeness_label

# Test with sample values
test_samples = [
    {
        "name": "Sample 1 (from dataset)",
        "values": [314.6, 5000, 28.6, 75.3, 1008.5],  # gas, co2, temp, hum, press
    },
    {
        "name": "Sample 2 (from dataset)",
        "values": [408.5, 3215, 28.5, 76.4, 1008.7],
    },
    {
        "name": "Sample 3 (from dataset)",
        "values": [205.9, 4377, 29.8, 88.3, 1006.2],
    },
]

print("\n  Test Predictions:")
print("  " + "-" * 76)
for sample in test_samples:
    values = sample["values"]
    pred_hours = predict_remaining_hours(reg_model, values)
    pred_class, pred_label = predict_ripeness_label(cls_model, values)
    pred_days = pred_hours / 24
    
    # Apply clamping rule: overripe/molds/rotten = 0 remaining
    if pred_class >= 4:
        pred_hours = 0
        pred_days = 0
    
    print(f"  {sample['name']}")
    print(f"    Input: Gas={values[0]}, CO2={values[1]}, Temp={values[2]}, Hum={values[3]}, Press={values[4]}")
    print(f"    Ripeness: {pred_label} (class {pred_class})")
    print(f"    Shelf Life: {pred_hours:.2f} hours ({pred_days:.2f} days)")
    print()

print("=" * 80)
print("RETRAINING COMPLETE!")
print("=" * 80)
print("\nNext steps:")
print("1. Test with predict_cli.py to verify CLI predictions")
print("2. Rebuild your React Native app to use new JSON trees")
print("3. Test app predictions match CLI predictions")
