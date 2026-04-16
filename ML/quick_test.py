"""
Quick test script to compare predictions with custom sensor values.
Usage: python quick_test.py
"""

import joblib
import pandas as pd
from shelf_life_model import MODEL_PATH

RIPENESS_MAP = {
    0: "unripe",
    1: "near ripe", 
    2: "ripe",
    3: "very ripe",
    4: "overripe",
    5: "molds",
    6: "rotten"
}

def predict(reg_model, cls_model, gas_resistance, co2, temperature, humidity, pressure):
    """Run prediction with both models"""
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
    
    # Clamp if overripe/molds/rotten
    shelf_life_hours = 0 if ripeness_class >= 4 else max(0, raw_hours)
    shelf_life_days = shelf_life_hours / 24.0
    
    return {
        "ripeness_class": ripeness_class,
        "ripeness_label": ripeness_label,
        "shelf_life_hours": shelf_life_hours,
        "shelf_life_days": shelf_life_days,
        "raw_hours": raw_hours
    }

def main():
    print("Loading models...")
    artifact = joblib.load(MODEL_PATH)
    reg_model = artifact["reg_model"]
    cls_model = artifact["cls_model"]
    print("Models loaded!\n")
    
    print("=" * 60)
    print("QUICK PREDICTION TEST")
    print("=" * 60)
    print("\nEnter sensor values (or press Enter for default test):\n")
    
    # Get inputs
    try:
        gas_str = input("Gas Resistance (kOhm) [453.63]: ").strip()
        gas_resistance = float(gas_str) if gas_str else 453.63
        
        co2_str = input("CO2 (ppm) [1020]: ").strip()
        co2 = float(co2_str) if co2_str else 1020
        
        temp_str = input("Temperature (°C) [31.5]: ").strip()
        temperature = float(temp_str) if temp_str else 31.5
        
        humid_str = input("Humidity (%) [67.1]: ").strip()
        humidity = float(humid_str) if humid_str else 67.1
        
        press_str = input("Pressure (hPa) [1012.4]: ").strip()
        pressure = float(press_str) if press_str else 1012.4
        
    except ValueError:
        print("Invalid input! Using default values.")
        gas_resistance, co2, temperature, humidity, pressure = 453.63, 1020, 31.5, 67.1, 1012.4
    
    # Run prediction
    result = predict(reg_model, cls_model, gas_resistance, co2, temperature, humidity, pressure)
    
    # Display results
    print("\n" + "=" * 60)
    print("PREDICTION RESULT")
    print("=" * 60)
    print(f"\nInputs:")
    print(f"  Gas Resistance: {gas_resistance} kOhm")
    print(f"  CO2: {co2} ppm")
    print(f"  Temperature: {temperature}°C")
    print(f"  Humidity: {humidity}%")
    print(f"  Pressure: {pressure} hPa")
    
    print(f"\nPrediction:")
    print(f"  Ripeness: {result['ripeness_label']} (class {result['ripeness_class']})")
    print(f"  Shelf Life: {result['shelf_life_hours']:.2f} hours")
    print(f"  Shelf Life: {result['shelf_life_days']:.2f} days")
    
    if result['ripeness_class'] >= 4:
        print(f"\n  Note: Shelf life clamped to 0 (overripe/molds/rotten)")
        print(f"  Raw prediction was: {result['raw_hours']:.2f} hours")
    
    print("\n" + "=" * 60)
    print("\nTo test in app, use these values in your sensor or test screen.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
