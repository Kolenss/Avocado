"""
Verify that predict_cli.py logic matches the app (prediction.ts) logic.
Tests the same sensor values through both methods.
"""

import joblib
import pandas as pd
from shelf_life_model import MODEL_PATH, predict_remaining_hours, predict_ripeness_label

RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe",
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten"
}

def predict_cli_method(reg_model, cls_model, gas_resistance, co2, temperature, humidity, pressure):
    """This is EXACTLY how predict_cli.py does it"""
    sample = [gas_resistance, co2, temperature, humidity, pressure]
    raw_hours = predict_remaining_hours(reg_model, sample)
    pred_class, pred_label = predict_ripeness_label(cls_model, sample)
    
    # Clamp shelf life based on ripeness: overripe/molds/rotten = 0 remaining
    remaining_hours = 0 if pred_class >= 4 else raw_hours
    remaining_days = remaining_hours / 24
    
    return {
        "class": pred_class,
        "label": pred_label,
        "hours": remaining_hours,
        "days": remaining_days
    }

def predict_app_method(reg_model, cls_model, gas_resistance, co2, temperature, humidity, pressure):
    """This is EXACTLY how app_predict.py and prediction.ts do it"""
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
        "class": ripeness_class,
        "label": ripeness_label,
        "hours": shelf_life_hours,
        "days": shelf_life_days
    }

def main():
    print("Loading models...")
    artifact = joblib.load(MODEL_PATH)
    reg_model = artifact["reg_model"]
    cls_model = artifact["cls_model"]
    
    # Test cases from training data
    test_cases = [
        {"name": "Unripe", "gas": 314.6, "co2": 5000, "temp": 28.6, "humid": 75.3, "press": 1008.5},
        {"name": "Near Ripe", "gas": 315.3, "co2": 2520, "temp": 28.1, "humid": 76.5, "press": 1007.2},
        {"name": "Ripe", "gas": 312.5, "co2": 3680, "temp": 30.0, "humid": 79.1, "press": 1005.6},
        {"name": "Molds", "gas": 254.6, "co2": 4212, "temp": 32.4, "humid": 72.8, "press": 1003.8},
        {"name": "Rotten", "gas": 334.1, "co2": 3614, "temp": 27.3, "humid": 84.7, "press": 1007.2},
    ]
    
    print("\n" + "=" * 80)
    print("VERIFICATION: predict_cli.py vs app (prediction.ts)")
    print("=" * 80)
    
    all_match = True
    
    for test in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Test: {test['name']}")
        print(f"Sensors: Gas={test['gas']}, CO2={test['co2']}, Temp={test['temp']}°C")
        print(f"{'─' * 80}")
        
        cli_result = predict_cli_method(
            reg_model, cls_model,
            test['gas'], test['co2'], test['temp'], test['humid'], test['press']
        )
        
        app_result = predict_app_method(
            reg_model, cls_model,
            test['gas'], test['co2'], test['temp'], test['humid'], test['press']
        )
        
        print(f"\npredict_cli.py:")
        print(f"  Class: {cli_result['class']} ({cli_result['label']})")
        print(f"  Shelf Life: {cli_result['hours']:.2f} hours ({cli_result['days']:.2f} days)")
        
        print(f"\napp (prediction.ts):")
        print(f"  Class: {app_result['class']} ({app_result['label']})")
        print(f"  Shelf Life: {app_result['hours']:.2f} hours ({app_result['days']:.2f} days)")
        
        # Check if they match
        class_match = cli_result['class'] == app_result['class']
        hours_match = abs(cli_result['hours'] - app_result['hours']) < 0.01
        
        if class_match and hours_match:
            print(f"\n✓ MATCH: Both methods give identical results")
        else:
            print(f"\n✗ MISMATCH:")
            if not class_match:
                print(f"  Class: {cli_result['class']} vs {app_result['class']}")
            if not hours_match:
                print(f"  Hours: {cli_result['hours']:.2f} vs {app_result['hours']:.2f}")
            all_match = False
    
    print(f"\n{'=' * 80}")
    if all_match:
        print("✓✓✓ SUCCESS: predict_cli.py and app give IDENTICAL results!")
        print("You can now use predict_cli.py to test the same predictions as the app.")
    else:
        print("✗✗✗ FAILURE: Results don't match. There's still a difference.")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    main()
