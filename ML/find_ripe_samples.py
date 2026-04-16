"""
Find sensor values that will predict as "near ripe" and "ripe"
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

def predict(cls_model, gas, co2, temp, humid, press):
    sample = pd.DataFrame([{
        "gas_resistance": gas,
        "co2": co2,
        "temperature": temp,
        "humidity": humid,
        "pressure": press
    }])
    return int(cls_model.predict(sample)[0])

def main():
    print("Loading model...")
    artifact = joblib.load("shelf_life_regressor.joblib")
    cls_model = artifact["cls_model"]
    reg_model = artifact["reg_model"]
    
    print("Loading dataset...")
    df = pd.read_csv("merged_avocado_dataset.csv")
    
    print("\n" + "=" * 80)
    print("SENSOR VALUES THAT PREDICT AS 'NEAR RIPE' AND 'RIPE'")
    print("=" * 80)
    
    # Find samples that actually predict as near ripe (class 1)
    print("\n--- NEAR RIPE (Class 1) Predictions ---\n")
    near_ripe_found = 0
    for idx, row in df.iterrows():
        pred = predict(cls_model, row['gas_resistance'], row['co2'], 
                      row['temperature'], row['humidity'], row['pressure'])
        if pred == 1 and near_ripe_found < 3:
            near_ripe_found += 1
            sample = pd.DataFrame([{
                "gas_resistance": row['gas_resistance'],
                "co2": row['co2'],
                "temperature": row['temperature'],
                "humidity": row['humidity'],
                "pressure": row['pressure']
            }])
            hours = float(reg_model.predict(sample)[0])
            days = hours / 24
            
            print(f"Sample {near_ripe_found}:")
            print(f"  Temperature: {row['temperature']}")
            print(f"  Humidity: {row['humidity']}")
            print(f"  Pressure: {row['pressure']}")
            print(f"  Gas Resistance: {row['gas_resistance']}")
            print(f"  CO2: {row['co2']}")
            print(f"  → Predicts: NEAR RIPE ({days:.2f} days shelf life)")
            print()
    
    if near_ripe_found == 0:
        print("  No samples found that predict as 'near ripe'")
        print("  The model may have difficulty distinguishing this class.")
    
    # Find samples that actually predict as ripe (class 2)
    print("\n--- RIPE (Class 2) Predictions ---\n")
    ripe_found = 0
    for idx, row in df.iterrows():
        pred = predict(cls_model, row['gas_resistance'], row['co2'], 
                      row['temperature'], row['humidity'], row['pressure'])
        if pred == 2 and ripe_found < 3:
            ripe_found += 1
            sample = pd.DataFrame([{
                "gas_resistance": row['gas_resistance'],
                "co2": row['co2'],
                "temperature": row['temperature'],
                "humidity": row['humidity'],
                "pressure": row['pressure']
            }])
            hours = float(reg_model.predict(sample)[0])
            days = hours / 24
            
            print(f"Sample {ripe_found}:")
            print(f"  Temperature: {row['temperature']}")
            print(f"  Humidity: {row['humidity']}")
            print(f"  Pressure: {row['pressure']}")
            print(f"  Gas Resistance: {row['gas_resistance']}")
            print(f"  CO2: {row['co2']}")
            print(f"  → Predicts: RIPE ({days:.2f} days shelf life)")
            print()
    
    if ripe_found == 0:
        print("  No samples found that predict as 'ripe'")
    
    print("=" * 80)
    print("\nYou can use these sensor values in your app to see 'near ripe'")
    print("and 'ripe' predictions!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
