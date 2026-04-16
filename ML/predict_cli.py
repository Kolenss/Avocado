"""
Interactive predictor for avocado ripeness and shelf life.

Uses model artifact produced by `shelf_life_model.py`:
- shelf_life_regressor.joblib

Prompts the user for 5 inputs:
- temperature
- humidity
- pressure
- gas_resistance
- co2

Outputs: ripeness class, ripeness label, remaining shelf life in hours and days.
"""

from __future__ import annotations

import joblib

from shelf_life_model import MODEL_PATH, predict_remaining_hours, predict_ripeness_label


def ask_float(name: str) -> float:
    """Prompt until a valid float is entered."""
    while True:
        raw = input(f"Enter {name}: ").strip()
        try:
            return float(raw)
        except ValueError:
            print(f"Invalid value '{raw}'. Please enter a numeric value.")


def run() -> None:
    print("Avocado Ripeness & Shelf-Life Predictor (5 inputs)")
    print("Input order: gas_resistance, co2, temperature, humidity, pressure\n")

    artifact = joblib.load(MODEL_PATH)
    reg_model = artifact["reg_model"]
    cls_model = artifact["cls_model"]

    gas_resistance = ask_float("gas_resistance")
    co2 = ask_float("co2")
    temperature = ask_float("temperature")
    humidity = ask_float("humidity")
    pressure = ask_float("pressure")

    sample = [gas_resistance, co2, temperature, humidity, pressure]
<<<<<<< HEAD
    raw_hours = predict_remaining_hours(reg_model, sample)
    pred_class, pred_label = predict_ripeness_label(cls_model, sample)
    
    # Clamp shelf life based on ripeness: overripe/molds/rotten = 0 remaining
    remaining_hours = 0 if pred_class >= 4 else raw_hours
=======
    remaining_hours = predict_remaining_hours(reg_model, sample)
    pred_class, pred_label = predict_ripeness_label(cls_model, sample)
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
    remaining_days = remaining_hours / 24

    print("\n=== Prediction Result ===")
    print(f"Input: {sample}")
    print(f"Predicted Class: {pred_class}")
    print(f"Predicted Label: {pred_label}")
    print(f"Estimated Shelf Life: {remaining_hours:.2f} hours")
    print(f"Estimated Shelf Life: {remaining_days:.2f} days")


if __name__ == "__main__":
    run()
