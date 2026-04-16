"""
Test the prediction logic with actual samples from training data.
This helps verify if the model can predict different ripeness levels.
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

def predict(cls_model, reg_model, gas_resistance, co2, temperature, humidity, pressure):
    """Predict using the same logic as the app"""
    input_data = pd.DataFrame([{
        "gas_resistance": gas_resistance,
        "co2": co2,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    }])
    
    ripeness_class = int(cls_model.predict(input_data)[0])
    ripeness_label = RIPENESS_MAP.get(ripeness_class, "unknown")
    
    raw_hours = float(reg_model.predict(input_data)[0])
    shelf_life_hours = 0 if ripeness_class >= 4 else max(0, raw_hours)
    shelf_life_days = shelf_life_hours / 24.0
    
    return ripeness_class, ripeness_label, shelf_life_hours, shelf_life_days

def main():
    print("Loading models...")
    artifact = joblib.load("shelf_life_regressor.joblib")
    cls_model = artifact["cls_model"]
    reg_model = artifact["reg_model"]
    
    print("Loading training data...")
    df = pd.read_csv("newfeed-data-set-avocado-open-only-clean.csv")
    
    print("\n" + "=" * 80)
    print("TESTING MODEL WITH ACTUAL TRAINING SAMPLES")
    print("=" * 80)
    
    # Test one sample from each ripeness class
    for label in range(7):
        samples = df[df['Label'] == label]
        if len(samples) == 0:
            continue
            
        # Get first sample
        sample = samples.iloc[0]
        
        gas = sample['Gas Resistance']
        co2_val = sample['CO2']
        temp = sample['Temperature']
        humid = sample['Humidity']
        press = sample['Pressure']
        
        pred_class, pred_label, hours, days = predict(
            cls_model, reg_model, gas, co2_val, temp, humid, press
        )
        
        match = "✓" if pred_class == label else "✗"
        
        print(f"\n{match} Actual Label: {label} ({RIPENESS_MAP[label]})")
        print(f"  Predicted: {pred_class} ({pred_label})")
        print(f"  Sensors: Gas={gas:.1f}, CO2={co2_val}, Temp={temp:.1f}°C, Humid={humid:.1f}%, Press={press:.1f}")
        print(f"  Shelf Life: {hours:.1f} hours ({days:.2f} days)")
    
    print("\n" + "=" * 80)
    print("SAMPLES YOU CAN TEST IN THE APP")
    print("=" * 80)
    
    # Provide samples for each class that user can test in the app
    for label in [0, 2, 4, 6]:  # unripe, ripe, overripe, rotten
        samples = df[df['Label'] == label]
        if len(samples) == 0:
            continue
        
        sample = samples.iloc[0]
        print(f"\n{RIPENESS_MAP[label].upper()} sample:")
        print(f"  Temperature: {sample['Temperature']}")
        print(f"  Humidity: {sample['Humidity']}")
        print(f"  Pressure: {sample['Pressure']}")
        print(f"  Gas Resistance: {sample['Gas Resistance']}")
        print(f"  CO2: {sample['CO2']}")
        
        # Show what the model will predict
        pred_class, pred_label, hours, days = predict(
            cls_model, reg_model,
            sample['Gas Resistance'], sample['CO2'], sample['Temperature'],
            sample['Humidity'], sample['Pressure']
        )
        print(f"  → Model will predict: {pred_label} ({days:.2f} days)")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
