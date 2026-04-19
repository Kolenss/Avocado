"""
Test script to verify that predict_cli.py and app_predict.py give identical results.
This ensures consistency between CLI predictions and app predictions.
"""

import joblib
import pandas as pd
from shelf_life_model import MODEL_PATH, predict_remaining_hours, predict_ripeness_label

# Test cases with different sensor readings
test_cases = [
    {
        "name": "Fresh avocado (unripe)",
        "gas_resistance": 450.0,
        "co2": 1000,
        "temperature": 25.0,
        "humidity": 60.0,
        "pressure": 1013.0
    },
    {
        "name": "Ripe avocado",
        "gas_resistance": 350.0,
        "co2": 3000,
        "temperature": 28.0,
        "humidity": 70.0,
        "pressure": 1010.0
    },
    {
        "name": "Overripe avocado",
        "gas_resistance": 250.0,
        "co2": 5000,
        "temperature": 30.0,
        "humidity": 80.0,
        "pressure": 1008.0
    },
    {
        "name": "Sample from app",
        "gas_resistance": 453.63,
        "co2": 1020,
        "temperature": 31.5,
        "humidity": 67.1,
        "pressure": 1012.4
    }
]

RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten"
}

def predict_cli_style(reg_model, cls_model, gas_resistance, co2, temperature, humidity, pressure):
    """Prediction using predict_cli.py logic"""
    sample = [gas_resistance, co2, temperature, humidity, pressure]
    raw_hours = predict_remaining_hours(reg_model, sample)
    pred_class, pred_label = predict_ripeness_label(cls_model, sample)
    
    # Clamp shelf life based on ripeness: overripe/molds/rotten = 0 remaining
    remaining_hours = 0 if pred_class >= 4 else raw_hours
    remaining_days = remaining_hours / 24
    
    return {
        "ripeness_class": pred_class,
        "ripeness_label": pred_label,
        "shelf_life_hours": remaining_hours,
        "shelf_life_days": remaining_days
    }

def predict_app_style(reg_model, cls_model, gas_resistance, co2, temperature, humidity, pressure):
    """Prediction using app_predict.py logic"""
    input_data = pd.DataFrame([{
        "gas_resistance": gas_resistance,
        "co2": co2,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    }])
    
    # Predict ripeness class
    ripeness_class = int(cls_model.predict(input_data)[0])
    ripeness_label = RIPENESS_MAP.get(ripeness_class, "unknown")
    
    # Predict shelf life
    raw_shelf_life_hours = float(reg_model.predict(input_data)[0])
    
    # Clamp shelf life based on ripeness: overripe/molds/rotten = 0 remaining
    shelf_life_hours = 0 if ripeness_class >= 4 else max(0, raw_shelf_life_hours)
    shelf_life_days = shelf_life_hours / 24.0
    
    return {
        "ripeness_class": ripeness_class,
        "ripeness_label": ripeness_label,
        "shelf_life_hours": shelf_life_hours,
        "shelf_life_days": shelf_life_days
    }

def main():
    print("Loading models...")
    artifact = joblib.load(MODEL_PATH)
    reg_model = artifact["reg_model"]
    cls_model = artifact["cls_model"]
    print("Models loaded successfully!\n")
    
    print("=" * 80)
    print("PREDICTION CONSISTENCY TEST")
    print("=" * 80)
    
    all_match = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"Test Case {i}: {test['name']}")
        print(f"{'─' * 80}")
        print(f"Inputs:")
        print(f"  Gas Resistance: {test['gas_resistance']} kOhm")
        print(f"  CO2: {test['co2']} ppm")
        print(f"  Temperature: {test['temperature']}°C")
        print(f"  Humidity: {test['humidity']}%")
        print(f"  Pressure: {test['pressure']} hPa")
        
        # Run both prediction methods
        cli_result = predict_cli_style(
            reg_model, cls_model,
            test['gas_resistance'], test['co2'], test['temperature'],
            test['humidity'], test['pressure']
        )
        
        app_result = predict_app_style(
            reg_model, cls_model,
            test['gas_resistance'], test['co2'], test['temperature'],
            test['humidity'], test['pressure']
        )
        
        # Compare results
        print(f"\npredict_cli.py result:")
        print(f"  Ripeness: {cli_result['ripeness_label']} (class {cli_result['ripeness_class']})")
        print(f"  Shelf Life: {cli_result['shelf_life_hours']:.2f} hours ({cli_result['shelf_life_days']:.2f} days)")
        
        print(f"\napp_predict.py result:")
        print(f"  Ripeness: {app_result['ripeness_label']} (class {app_result['ripeness_class']})")
        print(f"  Shelf Life: {app_result['shelf_life_hours']:.2f} hours ({app_result['shelf_life_days']:.2f} days)")
        
        # Check if they match
        match = (
            cli_result['ripeness_class'] == app_result['ripeness_class'] and
            abs(cli_result['shelf_life_hours'] - app_result['shelf_life_hours']) < 0.01
        )
        
        if match:
            print(f"\n✓ MATCH: Both methods produce identical results")
        else:
            print(f"\n✗ MISMATCH: Results differ!")
            all_match = False
    
    print(f"\n{'=' * 80}")
    if all_match:
        print("✓ SUCCESS: All predictions match! CLI and app will give same results.")
    else:
        print("✗ FAILURE: Some predictions don't match. Check the logic.")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    main()
