"""
Convert shelf_life_regressor.joblib to ONNX format for on-device inference.

Run this once:
    pip install skl2onnx onnx
    python convert_to_onnx.py

Outputs:
    shelf_life_reg.onnx   — regression model (predicts shelf life hours)
    shelf_life_cls.onnx   — classification model (predicts ripeness class)
"""

import joblib
import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

MODEL_PATH = "shelf_life_regressor.joblib"

print("Loading model artifact...")
artifact = joblib.load(MODEL_PATH)
reg_model = artifact["reg_model"]
cls_model = artifact["cls_model"]

# 5 input features: gas_resistance, co2, temperature, humidity, pressure
initial_type = [("float_input", FloatTensorType([None, 5]))]

print("Converting regression model...")
reg_onnx = convert_sklearn(reg_model, initial_types=initial_type, target_opset=12)
with open("shelf_life_reg.onnx", "wb") as f:
    f.write(reg_onnx.SerializeToString())
print("Saved: shelf_life_reg.onnx")

print("Converting classification model...")
cls_onnx = convert_sklearn(cls_model, initial_types=initial_type, target_opset=12)
with open("shelf_life_cls.onnx", "wb") as f:
    f.write(cls_onnx.SerializeToString())
print("Saved: shelf_life_cls.onnx")

# Quick sanity check
import onnxruntime as rt
sample = np.array([[258.7, 4279, 29.6, 84.4, 1008.3]], dtype=np.float32)

reg_sess = rt.InferenceSession("shelf_life_reg.onnx")
reg_out = reg_sess.run(None, {"float_input": sample})
hours = float(reg_out[0].flatten()[0])

cls_sess = rt.InferenceSession("shelf_life_cls.onnx")
cls_out = cls_sess.run(None, {"float_input": sample})
cls_val = int(cls_out[0].flatten()[0])

RIPENESS_MAP = {0: "unripe", 1: "near ripe", 2: "ripe", 3: "very ripe", 4: "overripe", 5: "molds", 6: "rotten"}
print(f"\nSanity check with {sample.tolist()}:")
print(f"  Shelf life: {hours:.2f} hours ({hours/24:.2f} days)")
print(f"  Ripeness:   class {cls_val} ({RIPENESS_MAP.get(cls_val, 'unknown')})")
print("\nDone! Copy shelf_life_reg.onnx and shelf_life_cls.onnx to assets/")
