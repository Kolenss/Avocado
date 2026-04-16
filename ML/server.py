"""
Flask API server for avocado shelf life prediction.
Run with: python server.py
Listens on http://0.0.0.0:5000
"""

from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

print("Loading model...")
artifact = joblib.load("shelf_life_regressor.joblib")
rf_reg = artifact["reg_model"]
rf_cls = artifact["cls_model"]
RIPENESS_MAP = artifact.get("ripeness_map", {
    0: "Unripe", 1: "Near Ripe", 2: "Ripe", 3: "Very Ripe",
    4: "Overripe", 5: "Molds", 6: "Rotten"
})
print("Model loaded.")

FEATURE_COLUMNS = ["gas_resistance", "co2", "temperature", "humidity", "pressure"]

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    try:
        row = pd.DataFrame([{
            "gas_resistance": float(data["gas_resistance"]),
            "co2":            float(data["co2"]),
            "temperature":    float(data["temperature"]),
            "humidity":       float(data["humidity"]),
            "pressure":       float(data["pressure"]),
        }])
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

    shelf_life_hours = float(rf_reg.predict(row)[0])
    shelf_life_days  = shelf_life_hours / 24.0
    ripeness_class   = int(rf_cls.predict(row)[0])
    ripeness_label   = RIPENESS_MAP.get(ripeness_class, "Unknown")

    # Human-readable note
    if shelf_life_days <= 0:
        note = "Consume immediately or discard."
    elif shelf_life_days < 1:
        note = f"Will last about {int(shelf_life_hours)} more hours."
    elif shelf_life_days < 2:
        note = "Will be at peak ripeness within 1 day."
    else:
        note = f"Estimated {shelf_life_days:.1f} days of shelf life remaining."

    return jsonify({
        "shelf_life_hours": round(shelf_life_hours, 1),
        "shelf_life_days":  round(shelf_life_days, 2),
        "ripeness_label":   ripeness_label,
        "ripeness_class":   ripeness_class,
        "note":             note,
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
