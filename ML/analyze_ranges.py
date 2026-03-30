"""
Analyze sensor value ranges for each ripeness stage.
"""

import pandas as pd
import numpy as np

CSV_PATH = "newfeed-data-set-avocado-open-only-clean.csv"

# Load and prepare data
df = pd.read_csv(CSV_PATH)
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Standardize column names
col_map = {}
for feat in ["gas_resistance", "co2", "temperature", "humidity", "pressure", "label"]:
    search_terms = {
        "gas_resistance": ["gas", "resistance"],
        "co2": ["co2", "co_2"],
        "temperature": ["temp"],
        "humidity": ["humid"],
        "pressure": ["press"],
        "label": ["label", "ripeness"]
    }
    terms = search_terms.get(feat, [feat])
    for c in df.columns:
        c_lower = c.lower()
        if any(term in c_lower for term in terms):
            col_map[feat] = c
            break

# Extract relevant columns
data = df[[col_map.get("gas_resistance", "Gas Resistance"), 
           col_map.get("co2", "CO2"),
           col_map.get("temperature", "Temperature"),
           col_map.get("humidity", "Humidity"),
           col_map.get("pressure", "Pressure"),
           col_map.get("label", "Label")]]
data.columns = ["gas_resistance", "co2", "temperature", "humidity", "pressure", "ripeness_label"]
data = data.apply(pd.to_numeric, errors="coerce").dropna()

RIPENESS_MAP = {
    0: "Unripe",
    1: "Near Ripe",
    2: "Ripe",
    3: "Very Ripe",
    4: "Overripe",
    5: "Molds",
    6: "Rotten"
}

print("=" * 80)
print("SENSOR VALUE RANGES BY RIPENESS STAGE")
print("=" * 80)
print(f"\nTotal samples: {len(data)}")
print(f"\nFeature order: gas_resistance, co2, temperature, humidity, pressure\n")

for label in sorted(data["ripeness_label"].unique()):
    subset = data[data["ripeness_label"] == label]
    count = len(subset)
    pct = (count / len(data)) * 100
    
    print(f"\n{'='*80}")
    print(f"{RIPENESS_MAP.get(label, 'Unknown')} (Class {int(label)}) - {count} samples ({pct:.1f}%)")
    print(f"{'='*80}")
    
    for col in ["gas_resistance", "co2", "temperature", "humidity", "pressure"]:
        vals = subset[col]
        print(f"\n{col.upper()}:")
        print(f"  Min:    {vals.min():.2f}")
        print(f"  Max:    {vals.max():.2f}")
        print(f"  Mean:   {vals.mean():.2f}")
        print(f"  Median: {vals.median():.2f}")
        print(f"  Std:    {vals.std():.2f}")

print("\n" + "=" * 80)
print("SUMMARY: Typical sensor patterns by ripeness stage")
print("=" * 80)

for label in sorted(data["ripeness_label"].unique()):
    subset = data[data["ripeness_label"] == label]
    print(f"\n{RIPENESS_MAP.get(label, 'Unknown')}:")
    print(f"  Gas: {subset['gas_resistance'].mean():.1f} kΩ")
    print(f"  CO2: {subset['co2'].mean():.0f} ppm")
    print(f"  Temp: {subset['temperature'].mean():.1f}°C")
    print(f"  Humidity: {subset['humidity'].mean():.1f}%")
    print(f"  Pressure: {subset['pressure'].mean():.1f} hPa")
