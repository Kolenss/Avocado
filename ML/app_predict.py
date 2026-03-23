"""
App-side prediction using full RandomForest model.
Receives sensor data from ESP32 and runs accurate predictions.

Usage:
  python app_predict.py --serial COM3           # Read from serial port
  python app_predict.py --json '{"temperature":31.5,...}'  # Single prediction
"""

import argparse
import json
import joblib
import pandas as pd
import serial
import time

# Load the full RandomForest model
print("Loading RandomForest model...")
artifact = joblib.load("shelf_life_regressor.joblib")
rf_model = artifact["reg_model"]
print(f"  Model loaded: {type(rf_model).__name__}")

# Ripeness labels
RIPENESS_MAP = {0: "unripe", 1: "near ripe", 2: "ripe", 3: "very ripe",
                4: "overripe", 5: "molds", 6: "rotten"}

def predict_from_sensors(temp, humidity, pressure, gas_kohm, co2):
    """
    Run RandomForest prediction on sensor data.
    
    Args:
        temp: Temperature in Celsius
        humidity: Relative humidity in %
        pressure: Atmospheric pressure in hPa
        gas_kohm: Gas resistance in kOhm
        co2: CO2 concentration in ppm
    
    Returns:
        dict with shelf_life_hours and shelf_life_days
    """
    # Create input dataframe (RF expects these column names)
    input_data = pd.DataFrame([{
        "temperature": temp,
        "humidity": humidity,
        "pressure": pressure,
        "gas_resistance": gas_kohm,
        "co2": co2
    }])
    
    # Predict shelf life
    shelf_life_hours = float(rf_model.predict(input_data)[0])
    shelf_life_days = shelf_life_hours / 24.0
    
    return {
        "shelf_life_hours": shelf_life_hours,
        "shelf_life_days": shelf_life_days
    }

def read_from_serial(port, baudrate=115200):
    """
    Read sensor data from ESP32 via serial port.
    Looks for JSON lines starting with "JSON: "
    """
    print(f"\nConnecting to {port} at {baudrate} baud...")
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Wait for connection
    print("Connected. Waiting for data...\n")
    
    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # Look for JSON output
            if line.startswith("JSON: "):
                json_str = line[6:]  # Remove "JSON: " prefix
                try:
                    data = json.loads(json_str)
                    
                    # Extract sensor values
                    temp = data["temperature"]
                    humidity = data["humidity"]
                    pressure = data["pressure"]
                    gas_kohm = data["gas_resistance"]
                    co2 = data["co2"]
                    
                    # Run prediction
                    result = predict_from_sensors(temp, humidity, pressure, gas_kohm, co2)
                    
                    # Display results
                    print("─" * 50)
                    print(f"Temp: {temp:.1f}°C | Humidity: {humidity:.1f}% | Pressure: {pressure:.1f} hPa")
                    print(f"Gas: {gas_kohm:.2f} kOhm | CO2: {co2} ppm")
                    print(f"Shelf Life: {result['shelf_life_hours']:.1f} hours ({result['shelf_life_days']:.2f} days)")
                    print()
                    
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Invalid JSON: {e}")
                except KeyError as e:
                    print(f"[ERROR] Missing field: {e}")
            
            # Also print other lines (for debugging)
            elif line and not line.startswith("──"):
                print(f"[ESP32] {line}")
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        ser.close()

def predict_from_json(json_str):
    """
    Run prediction from JSON string.
    """
    data = json.loads(json_str)
    
    temp = data["temperature"]
    humidity = data["humidity"]
    pressure = data["pressure"]
    gas_kohm = data["gas_resistance"]
    co2 = data["co2"]
    
    result = predict_from_sensors(temp, humidity, pressure, gas_kohm, co2)
    
    print("\n" + "─" * 50)
    print("Input:")
    print(f"  Temp: {temp:.1f}°C")
    print(f"  Humidity: {humidity:.1f}%")
    print(f"  Pressure: {pressure:.1f} hPa")
    print(f"  Gas: {gas_kohm:.2f} kOhm")
    print(f"  CO2: {co2} ppm")
    print("\nPrediction:")
    print(f"  Shelf Life: {result['shelf_life_hours']:.1f} hours")
    print(f"  Shelf Life: {result['shelf_life_days']:.2f} days")
    print("─" * 50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RandomForest prediction on sensor data")
    parser.add_argument("--serial", type=str, help="Serial port (e.g., COM3 or /dev/ttyUSB0)")
    parser.add_argument("--json", type=str, help="JSON string with sensor data")
    
    args = parser.parse_args()
    
    if args.serial:
        read_from_serial(args.serial)
    elif args.json:
        predict_from_json(args.json)
    else:
        # Default: test with sample data
        print("\nNo input specified. Running test prediction...\n")
        test_data = {
            "temperature": 31.5,
            "humidity": 67.1,
            "pressure": 1012.4,
            "gas_resistance": 453.63,
            "co2": 1020
        }
        predict_from_json(json.dumps(test_data))
        print("\nUsage:")
        print("  python app_predict.py --serial COM3")
        print("  python app_predict.py --json '{\"temperature\":31.5,\"humidity\":67.1,\"pressure\":1012.4,\"gas_resistance\":453.63,\"co2\":1020}'")
