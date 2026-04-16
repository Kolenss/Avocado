# Testing Guide: Verify App and CLI Predictions Match

## Model Update Summary

✅ **Completed:**
1. Updated `shelf_life_model.py` to use `merged_avocado_dataset1.csv` (1,293 rows vs 946 rows)
2. Retrained RandomForest models (regression + classification)
3. Exported new tree structures to JSON
4. Copied JSON files to `assets/` directory:
   - `reg_trees_compact.json` (4.8 MB, 300 trees)
   - `cls_trees_compact.json` (3.2 MB, 300 trees)

## Model Performance

**Regression (Shelf Life Prediction):**
- MAE: 44.28 hours
- RMSE: 56.77 hours
- R²: 0.2233

**Classification (Ripeness Detection):**
- Accuracy: 44.40%

## Test Samples for Verification

Use these exact sensor values to test both CLI and App predictions:

### Sample 1 - Unripe Avocado
```
Gas Resistance: 314.6
CO2: 5000
Temperature: 28.6
Humidity: 75.3
Pressure: 1008.5

Expected Results:
- Ripeness: Unripe (class 0)
- Shelf Life: 185.64 hours (7.73 days)
```

### Sample 2 - Unripe Avocado
```
Gas Resistance: 408.5
CO2: 3215
Temperature: 28.5
Humidity: 76.4
Pressure: 1008.7

Expected Results:
- Ripeness: Unripe (class 0)
- Shelf Life: 195.36 hours (8.14 days)
```

### Sample 3 - Near Ripe Avocado
```
Gas Resistance: 205.9
CO2: 4377
Temperature: 29.8
Humidity: 88.3
Pressure: 1006.2

Expected Results:
- Ripeness: Near Ripe (class 1)
- Shelf Life: 92.12 hours (3.84 days)
```

### Sample 4 - Ripe Avocado
```
Gas Resistance: 300.0
CO2: 4000
Temperature: 29.5
Humidity: 80.0
Pressure: 1007.0

Expected Results:
- Ripeness: Near Ripe (class 1)
- Shelf Life: 63.98 hours (2.67 days)
```

## Testing Steps

### 1. Test CLI Predictions

```bash
cd ML
python predict_cli.py
```

Enter the values from Sample 1 when prompted:
- gas_resistance: 314.6
- co2: 5000
- temperature: 28.6
- humidity: 75.3
- pressure: 1008.5

Verify the output matches the expected results.

### 2. Test App Predictions

1. Rebuild your React Native app:
   ```bash
   npx expo run:android --variant release
   ```

2. Connect to your ESP32 sensor or manually input the test values

3. Compare the app's prediction with the CLI prediction

4. They should match exactly (within rounding differences)

## Verification Checklist

- [ ] CLI predictions match expected results for all 4 samples
- [ ] App predictions match CLI predictions for all 4 samples
- [ ] Ripeness labels are identical between CLI and App
- [ ] Shelf life values are within ±0.1 hours difference

## Feature Order (CRITICAL)

Both CLI and App use this exact feature order:
1. gas_resistance
2. co2
3. temperature
4. humidity
5. pressure

**Do not change this order!** The model was trained with this specific order.

## Troubleshooting

### If predictions don't match:

1. **Check JSON files in assets/**
   - Verify `reg_trees_compact.json` and `cls_trees_compact.json` exist
   - Check file sizes (should be ~4.8MB and ~3.2MB)
   - Verify LastWriteTime is recent

2. **Verify feature order**
   - Ensure app sends: [gas, co2, temp, hum, press]
   - Check `routes/prediction.ts` line where features array is created

3. **Check model version**
   - Ensure `shelf_life_regressor.joblib` was updated
   - Run `python test_cli_predictions.py` to verify CLI uses new model

4. **Rebuild app completely**
   ```bash
   npx expo start --clear
   npx expo run:android --variant release
   ```

## Files Modified

- `ML/shelf_life_model.py` - Updated CSV_PATH to use dataset1
- `ML/shelf_life_regressor.joblib` - Retrained model artifact
- `ML/reg_trees_compact.json` - New regression trees
- `ML/cls_trees_compact.json` - New classification trees
- `assets/reg_trees_compact.json` - Copied for app use
- `assets/cls_trees_compact.json` - Copied for app use

## Next Steps

After verifying predictions match:
1. Test with real ESP32 sensor data
2. Monitor prediction accuracy in production
3. Collect more data to improve model performance
4. Consider retraining if accuracy is insufficient
