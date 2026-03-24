"""
Convert avocado models -> TFLite + C header for ESP32.

Generates avocado_ripeness_model_data.h containing:
  - SCALER_MEAN / SCALER_STD        (StandardScaler for both models)
  - REG_Y_MIN / REG_Y_MAX            (denormalization constants)
  - avocado_ripeness_model_data[]   (classifier: predicts ripeness class 0-6)
  - avocado_shelf_life_model_data[] (regressor:  predicts remaining hours)

The shelf-life regressor is a small Keras net trained to mimic the
RandomForest regressor in shelf_life_regressor.joblib, so ESP32 predictions
match predict_cli.py output.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

KERAS_CLS_PATH  = "avocado_ripeness_model.keras"
JOBLIB_PATH     = "shelf_life_regressor.joblib"
TFLITE_CLS_PATH = "avocado_ripeness.tflite"
TFLITE_REG_PATH = "avocado_shelf_life.tflite"
HEADER_PATH     = "avocado_ripeness_model_data.h"
CSV_PATH        = "data-set-avocado-open-box-only.csv"

FEATURE_COLUMNS = ["gas_resistance", "co2", "temperature", "humidity", "pressure"]
RANDOM_STATE    = 42

RIPENESS_MAP = {0: "unripe", 1: "near ripe", 2: "ripe", 3: "very ripe",
                4: "overripe", 5: "molds", 6: "rotten"}

# ── 1. Load CSV ──────────────────────────────────────────────────────────────
print("Loading CSV...")
df = pd.read_csv(CSV_PATH)
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

col_map = {}
for feat in FEATURE_COLUMNS:
    matches = [c for c in df.columns if feat in c]
    if not matches:
        raise ValueError(f"Column '{feat}' not found. Available: {list(df.columns)}")
    col_map[feat] = matches[0]

X_raw = df[[col_map[f] for f in FEATURE_COLUMNS]].apply(pd.to_numeric, errors="coerce")
valid = X_raw.notna().all(axis=1)
X_raw = X_raw[valid].values
print(f"  {len(X_raw)} valid rows")

# ── 2. Fit one shared scaler for both models ────────────────────────────────
print("Fitting scaler...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)
print(f"  mean : {scaler.mean_}")
print(f"  std  : {scaler.scale_}")

# ── 3. Load RF regressor and generate training targets ───────────────────────
print("\nLoading RF regressor from joblib...")
artifact = joblib.load(JOBLIB_PATH)
rf_reg   = artifact["reg_model"]

# RF was trained on gas_resistance in kOhm (CSV mean ~289 kOhm)
# X_raw already has gas in kOhm from the CSV — pass directly
print("Generating RF predictions as regression targets...")
y_reg = rf_reg.predict(
    pd.DataFrame(X_raw, columns=FEATURE_COLUMNS)
).astype(np.float32)
print(f"  RF prediction range: {y_reg.min():.1f} - {y_reg.max():.1f} hours")

# ── 4. Train small Keras regressor to mimic RF ──────────────────────────────
print("\nTraining small Keras regressor to mimic RF...")

# Normalize targets to [0,1] for stable training
y_min = float(y_reg.min())
y_max = float(y_reg.max())
y_norm = (y_reg - y_min) / (y_max - y_min)
print(f"  Target range: {y_min:.1f} - {y_max:.1f} hours (normalized to 0-1)")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_norm, test_size=0.2, random_state=RANDOM_STATE)

# Small network to fit ~24 KB arena (ESP32 RAM constraint)
# 5 -> 32 -> 16 -> 1
# Parameters: ~700 weights = ~3 KB model, ~24 KB arena after TFLite
reg_model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(5,)),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dense(1,  activation="sigmoid")
])

reg_model.compile(
    optimizer=tf.keras.optimizers.Adam(0.001),
    loss="mse",
    metrics=["mae"]
)

cb_es = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=30, restore_best_weights=True, verbose=0)

print("  Training...")
reg_model.fit(
    X_train, y_train,
    epochs=200,
    batch_size=32,
    validation_split=0.15,
    callbacks=[cb_es],
    verbose=0
)

_, mae_norm = reg_model.evaluate(X_test, y_test, verbose=0)
mae_hours = mae_norm * (y_max - y_min)
print(f"  Final MAE: {mae_hours:.2f} hours ({mae_hours/24:.2f} days)")

# ── 5. Convert both models to TFLite ────────────────────────────────────────
print("\nConverting to TFLite...")
def to_tflite(keras_model, path):
    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
    tflite_bytes = converter.convert()
    with open(path, "wb") as f:
        f.write(tflite_bytes)
    print(f"  {path}: {len(tflite_bytes)/1024:.1f} KB")
    return tflite_bytes

cls_model  = tf.keras.models.load_model(KERAS_CLS_PATH)
tflite_cls = to_tflite(cls_model, TFLITE_CLS_PATH)
tflite_reg = to_tflite(reg_model, TFLITE_REG_PATH)

# ── 6. Sanity check ──────────────────────────────────────────────────────────
print("\nSanity check...")
raw_sample = np.array([[453.63, 1020.0, 31.5, 67.1, 1012.4]])  # gas in kOhm (matches CSV)

def run_tflite(model_bytes, inp):
    interp = tf.lite.Interpreter(model_content=model_bytes)
    interp.allocate_tensors()
    interp.set_tensor(interp.get_input_details()[0]['index'], inp.astype(np.float32))
    interp.invoke()
    return interp.get_tensor(interp.get_output_details()[0]['index'])

cls_out   = run_tflite(tflite_cls, scaler.transform(raw_sample))
reg_out   = run_tflite(tflite_reg, scaler.transform(raw_sample))
pred_cls  = int(np.argmax(cls_out[0]))
pred_norm = float(reg_out[0][0])
pred_hrs  = pred_norm * (y_max - y_min) + y_min   # denormalize

rf_hrs = float(rf_reg.predict(
    pd.DataFrame(raw_sample, columns=FEATURE_COLUMNS))[0])

print(f"  Ripeness  : class {pred_cls} ({RIPENESS_MAP[pred_cls]})")
print(f"  Keras reg : {pred_hrs:.2f} hrs ({pred_hrs/24:.2f} days)")
print(f"  RF reg    : {rf_hrs:.2f} hrs ({rf_hrs/24:.2f} days)  <- predict_cli.py reference")

# ── 7. Generate C header ─────────────────────────────────────────────────────
print(f"\nGenerating {HEADER_PATH}...")

def to_hex(data):
    return ", ".join(f"0x{b:02x}" for b in data)

def to_c_float_array(arr, name):
    vals = ", ".join(f"{v:.8f}f" for v in arr)
    return f"static const float {name}[5] = {{ {vals} }};"

header = f"""\
// Auto-generated - do not edit manually
// Classifier : {len(tflite_cls)} bytes ({len(tflite_cls)/1024:.1f} KB)
// Regressor  : {len(tflite_reg)} bytes ({len(tflite_reg)/1024:.1f} KB)
// Input order: gas_resistance(kOhm), co2, temperature, humidity, pressure
//
// Classifier uses SCALER_MEAN / SCALER_STD
// Regressor  uses SCALER_MEAN / SCALER_STD (same scaler)

#ifndef AVOCADO_RIPENESS_MODEL_DATA_H
#define AVOCADO_RIPENESS_MODEL_DATA_H

// Shared scaler for both models
{to_c_float_array(scaler.mean_,  "SCALER_MEAN")}
{to_c_float_array(scaler.scale_, "SCALER_STD")}

// Regressor denormalization: hours = output * (REG_Y_MAX - REG_Y_MIN) + REG_Y_MIN
#define REG_Y_MIN {y_min:.4f}f
#define REG_Y_MAX {y_max:.4f}f

// Ripeness classifier (output: softmax[7], class 0-6)
const unsigned char avocado_ripeness_model_data[] = {{
  {to_hex(tflite_cls)}
}};
const unsigned int avocado_ripeness_model_data_len = {len(tflite_cls)};

// Shelf-life regressor (output: float[1], remaining hours)
const unsigned char avocado_shelf_life_model_data[] = {{
  {to_hex(tflite_reg)}
}};
const unsigned int avocado_shelf_life_model_data_len = {len(tflite_reg)};

#endif  // AVOCADO_RIPENESS_MODEL_DATA_H
"""

with open(HEADER_PATH, "w", encoding="utf-8") as f:
    f.write(header)

print("Done.")
print(f"  {TFLITE_CLS_PATH}")
print(f"  {TFLITE_REG_PATH}")
print(f"  {HEADER_PATH}")
