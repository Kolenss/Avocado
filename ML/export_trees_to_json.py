"""
Export RandomForest trees to JSON for React Native offline inference.
Generates reg_trees_compact.json and cls_trees_compact.json.
"""

import json
import joblib
import numpy as np

MODEL_PATH = "shelf_life_regressor.joblib"

print("Loading model artifact...")
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

print("\nExporting regression trees...")
reg_trees = []
for estimator in reg_model.estimators_:
    tree_data = export_tree(estimator.tree_, is_classifier=False)
    reg_trees.append(tree_data)

with open("reg_trees_compact.json", "w") as f:
    json.dump(reg_trees, f, separators=(',', ':'))
print(f"  Saved: reg_trees_compact.json ({len(reg_trees)} trees)")

print("\nExporting classification trees...")
cls_trees = []
for estimator in cls_model.estimators_:
    tree_data = export_tree(estimator.tree_, is_classifier=True)
    cls_trees.append(tree_data)

# Classification model needs class mapping
cls_classes = cls_model.classes_.tolist()

with open("cls_trees_compact.json", "w") as f:
    json.dump({"t": cls_trees, "c": cls_classes}, f, separators=(',', ':'))
print(f"  Saved: cls_trees_compact.json ({len(cls_trees)} trees)")

print("\nDone! Copy these files to assets/ directory:")
print("  - reg_trees_compact.json")
print("  - cls_trees_compact.json")
