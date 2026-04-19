import pandas as pd

print("\n=== COMPARING DATASETS ===\n")

# Load both datasets
df1 = pd.read_csv("merged_avocado_dataset.csv")
df2 = pd.read_csv("merged_avocado_dataset1.csv")

print("--- merged_avocado_dataset.csv ---")
print(f"Rows: {len(df1)}")
print(f"Columns: {list(df1.columns)}")
print(f"\nLabel distribution:")
print(df1["ripeness_label"].value_counts().sort_index())
print(f"\nMissing values:")
print(df1.isnull().sum())
print(f"\nData ranges:")
print(df1.describe())

print("\n\n--- merged_avocado_dataset1.csv ---")
print(f"Rows: {len(df2)}")
print(f"Columns: {list(df2.columns)}")
print(f"\nLabel distribution:")
print(df2["Label"].value_counts().sort_index())
print(f"\nMissing values:")
print(df2.isnull().sum())
print(f"\nData ranges:")
print(df2.describe())

print("\n\n=== COMPARISON SUMMARY ===")
print(f"Dataset 1 has {len(df1)} rows")
print(f"Dataset 2 has {len(df2)} rows")
print(f"Difference: {abs(len(df2) - len(df1))} rows ({((len(df2) - len(df1)) / len(df1) * 100):.1f}% more in dataset 2)")
