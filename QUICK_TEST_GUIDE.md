# Quick Test Guide - Verify App Predictions

## ✅ What Was Done

1. ✅ Retrained model with `merged_avocado_dataset1.csv` (1,293 rows vs 946 rows)
2. ✅ Exported new JSON trees to `assets/` directory
3. ✅ Verified CLI and App predictions match

## 🚀 Next Step: Rebuild Your App

```bash
npx expo run:android --variant release
```

## 🧪 Test These Values

After rebuilding, test with these sensor values:

### Test 1: Unripe Avocado
```
Gas: 314.6
CO2: 5000
Temp: 28.6
Humidity: 75.3
Pressure: 1008.5

Expected:
- Ripeness: Unripe
- Shelf Life: ~7.7 days
```

### Test 2: Near Ripe Avocado
```
Gas: 205.9
CO2: 4377
Temp: 29.8
Humidity: 88.3
Pressure: 1006.2

Expected:
- Ripeness: Near Ripe
- Shelf Life: ~3.8 days
```

## ✓ Verification

1. **Test CLI first:**
   ```bash
   cd ML
   python predict_cli.py
   ```
   Enter the values from Test 1

2. **Test in your app:**
   - Use same values
   - Compare results
   - Should match CLI predictions

## 📊 What Changed

- **More training data**: 36.7% increase (946 → 1,293 rows)
- **Better balance**: Label 1 (Near Ripe) increased from 96 to 285 samples
- **Same accuracy**: Model maintains similar performance with more data

## 🔧 If Predictions Don't Match

1. Check JSON files exist in `assets/`:
   - `reg_trees_compact.json` (~4.8 MB)
   - `cls_trees_compact.json` (~3.2 MB)

2. Clear cache and rebuild:
   ```bash
   npx expo start --clear
   npx expo run:android --variant release
   ```

3. Run verification script:
   ```bash
   cd ML
   python verify_app_cli_match.py
   ```

## 📝 Important Notes

- Feature order: `[gas, co2, temp, humidity, pressure]` - DO NOT CHANGE
- Predictions may differ by ±0.1 hours (floating point precision) - this is OK
- Overripe/molds/rotten always show 0 shelf life remaining

## 📚 Detailed Documentation

See `ML/TESTING_GUIDE.md` for complete testing instructions and more test samples.
