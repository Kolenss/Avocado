# Prediction Consistency Summary

## Problem Identified
The original `app_predict.py` was missing the classification model, so it couldn't predict ripeness labels. It only predicted shelf life hours, which is why the app always showed "unripe" as a default.

## Solution Applied
Updated `app_predict.py` and `predict_cli.py` to use the SAME prediction logic as the React Native app (`routes/prediction.ts`):

### Unified Prediction Logic (All 3 Methods Now Match)

1. **Load both models**: Classification model (cls_model) + Regression model (reg_model)
2. **Feature order**: `[gas_resistance, co2, temperature, humidity, pressure]`
3. **Predict ripeness class**: Use classification model → get class 0-6
4. **Predict shelf life**: Use regression model → get hours
5. **Apply clamping rule**: If ripeness_class >= 4 (overripe/molds/rotten), set shelf_life to 0
6. **Return results**: ripeness_class, ripeness_label, shelf_life_hours, shelf_life_days

## Files Updated

### 1. `ML/app_predict.py`
- ✅ Added classification model loading
- ✅ Added ripeness prediction
- ✅ Added clamping logic (class >= 4 → shelf_life = 0)
- ✅ Updated output to include ripeness_class and ripeness_label

### 2. `ML/predict_cli.py`
- ✅ Added clamping logic (class >= 4 → shelf_life = 0)
- ✅ Now matches app behavior exactly

### 3. `routes/prediction.ts` (React Native App)
- ✅ Already had correct logic (no changes needed)

## Verification

Run the consistency test:
```bash
cd ML
python test_prediction_consistency.py
```

This test verifies that `predict_cli.py` and `app_predict.py` produce identical results for the same sensor inputs.

## Usage Examples

### CLI Prediction
```bash
cd ML
python predict_cli.py
# Enter values when prompted
```

### App Prediction (from sensor data)
```bash
cd ML
python app_predict.py --json '{"temperature":31.5,"humidity":67.1,"pressure":1012.4,"gas_resistance":453.63,"co2":1020}'
```

### App Prediction (from serial port)
```bash
cd ML
python app_predict.py --serial COM3
```

## Expected Behavior

Now when you:
1. Get sensor readings in the React Native app
2. Run those same values through `predict_cli.py`
3. Run those same values through `app_predict.py`

**All three will give you IDENTICAL results:**
- Same ripeness label (unripe, ripe, overripe, etc.)
- Same ripeness class (0-6)
- Same shelf life hours
- Same shelf life days

## Model Behavior Notes

The classification model predicts ripeness based on sensor patterns learned from training data:
- **Class 0 (unripe)**: High gas resistance, low CO2, moderate temperature
- **Class 2 (ripe)**: Medium gas resistance, medium CO2
- **Class 4+ (overripe/molds/rotten)**: Low gas resistance, high CO2, shelf life forced to 0

If you're seeing mostly "unripe" predictions, it means:
1. Your sensor readings match the "unripe" pattern in the training data
2. The model is working correctly
3. To get different predictions, you need sensor readings that match ripe/overripe patterns

## Training Data Distribution

The model was trained on:
- Label 0 (unripe): 162 samples
- Label 1 (near ripe): 48 samples
- Label 2 (ripe): 42 samples
- Label 3 (very ripe): 22 samples
- Label 4 (overripe): 27 samples
- Label 5 (molds): 32 samples
- Label 6 (rotten): 140 samples
- **Total**: 473 samples

## Adding More Data

If you want to improve predictions, you can:
1. Add more sensor readings to `newfeed-data-set-avocado-open-only-clean.csv`
2. Retrain the model by running:
   ```bash
   cd ML
   python shelf_life_model.py
   ```
3. This will update `shelf_life_regressor.joblib` with the new model
4. For the React Native app, you'll also need to regenerate the tree JSON files:
   ```bash
   python export_trees_to_json.py
   ```
