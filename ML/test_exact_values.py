"""
Test the exact values from the user's app to see what the model predicts
"""

import joblib
import pandas as pd

RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten"
}

def main():
    print("Loading current model...")
    artifact = joblib.load("shelf_life_regressor.joblib")
    cls_model = artifact["cls_model"]
    reg_model = artifact["reg_model"]
    
    # User's values from predict_cli.py
    # Input: [gas_resistance, co2, temperature, humidity, pressure]
    gas_resistance = 187.0
    co2 = 2847.0
    temperature = 31.2
    humidity = 75.8
    pressure = 1004.2
    
    print("\n" + "=" * 80)
    print("TESTING USER'S EXACT SENSOR VALUES")
    print("=" * 80)
    
    print(f"\nInput values:")
    print(f"  Gas Resistance: {gas_resistance}")
    print(f"  CO2: {co2}")
    print(f"  Temperature: {temperature}")
    print(f"  Humidity: {humidity}")
    print(f"  Pressure: {pressure}")
    
    # Create input dataframe
    input_data = pd.DataFrame([{
        "gas_resistance": gas_resistance,
        "co2": co2,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    }])
    
    # Predict ripeness
    ripeness_class = int(cls_model.predict(input_data)[0])
    ripeness_label = RIPENESS_MAP.get(ripeness_class, "unknown")
    
    # Predict shelf life
    raw_hours = float(reg_model.predict(input_data)[0])
    shelf_life_hours = 0 if ripeness_class >= 4 else max(0, raw_hours)
    shelf_life_days = shelf_life_hours / 24.0
    
    print(f"\n{'=' * 80}")
    print("PREDICTION FROM CURRENT MODEL (shelf_life_regressor.joblib)")
    print("=" * 80)
    print(f"  Ripeness Class: {ripeness_class}")
    print(f"  Ripeness Label: {ripeness_label}")
    print(f"  Raw Hours: {raw_hours:.2f}")
    print(f"  Shelf Life Hours: {shelf_life_hours:.2f}")
    print(f"  Shelf Life Days: {shelf_life_days:.2f}")
    
    print(f"\n{'=' * 80}")
    print("USER'S APP SHOWED")
    print("=" * 80)
    print(f"  Ripeness: unripe")
    print(f"  Shelf Life: 58 hours (2.4 days)")
    
    print(f"\n{'=' * 80}")
    if ripeness_class == 0 and abs(shelf_life_hours - 58) < 5:
        print("✓ MATCH: Model and app predictions are close!")
        print("The app is using the correct model.")
    else:
        print("✗ MISMATCH: Model and app predictions are different!")
        print("\nPossible causes:")
        print("1. App is using cached old JSON files")
        print("2. App needs to be restarted/rebuilt")
        print("3. JSON files weren't copied correctly")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
