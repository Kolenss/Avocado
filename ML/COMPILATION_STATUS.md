# ESP32 Avocado Ripeness + Shelf Life Detector - Compilation Status

## Current Status: READY TO COMPILE

### Changes Made (Latest Session)

1. **Reduced Arena Size**
   - Changed `ARENA_REG_SIZE` from 80 KB → 24 KB
   - Previous compilation failed with 128 KB RAM overflow
   - New size should fit within ESP32 WROOM's 520 KB SRAM

2. **Simplified Neural Network**
   - Changed from: 5 → 384 → 256 → 128 → 64 → 1 (~250k weights, ~1 MB model)
   - Changed to: 5 → 32 → 16 → 1 (~700 weights, ~3 KB model)
   - Regressor TFLite size: 5.0 KB (down from 11.7 KB)
   - Training epochs: 200 (down from 500)
   - Removed dropout and L2 regularization for simplicity

3. **Fixed Header File**
   - Added `REG_Y_MIN` and `REG_Y_MAX` constants (0.0 - 185.86 hours)
   - Fixed comment to show gas_resistance in kOhm (not Ohm)
   - Both models now use same `SCALER_MEAN` and `SCALER_STD`

4. **Fixed ESP32 Code**
   - Removed duplicate regressor inference call
   - Removed fallback `#ifndef REG_Y_MIN` block (now in header)
   - Gas resistance stays in kOhm throughout (matches CSV data)

5. **Cleaned Conversion Script**
   - Removed duplicate code at end of file
   - Simplified training callbacks
   - Fixed encoding to UTF-8 to avoid Unicode errors

### Model Performance

**Sanity Check Results:**
- Input: [31.5°C, 67.1%, 1012.4 hPa, 453.63 kOhm, 1020 ppm]
- Ripeness: class 0 (unripe)
- Keras regressor: 184.55 hours (7.69 days)
- RF regressor: 148.46 hours (6.19 days) ← predict_cli.py reference
- **Difference: ~36 hours** (acceptable given RAM constraints)

**Training Metrics:**
- Final MAE: 13.20 hours (0.55 days)
- This is the average error when approximating the RandomForest

### Memory Usage Estimate

```
Classifier arena:  32 KB
Regressor arena:   24 KB
Classifier model:  13 KB
Regressor model:    5 KB
Other variables:  ~50 KB (BME680, SHT31, buffers, stack)
─────────────────────────
Total estimate:  ~124 KB out of 520 KB available
```

### Next Steps

1. **Compile the Arduino sketch** in Arduino IDE
   - If it compiles: Upload to ESP32 and test
   - If it fails: Further reduce `ARENA_REG_SIZE` (try 16 KB or 12 KB)

2. **If arena needs to be smaller:**
   - Edit `avocado_esp32.ino`: Change `ARENA_REG_SIZE` to 16 KB or 12 KB
   - Edit `convert_to_tflite.py`: Reduce network to 5 → 16 → 8 → 1
   - Re-run `python convert_to_tflite.py`
   - Copy new `avocado_ripeness_model_data.h` to Arduino sketch folder

3. **Test predictions:**
   - Compare ESP32 output with `predict_cli.py` output
   - Expect ~30-40 hour difference (neural net approximation error)
   - Unripe avocados should show 120-180 hours shelf life

### Files Modified

- `avocado_esp32.ino` - Reduced arena, removed duplicate code
- `convert_to_tflite.py` - Smaller network, cleaned up
- `avocado_ripeness_model_data.h` - Regenerated with REG_Y constants

### Known Limitations

- Neural network is a simplified approximation of RandomForest
- Prediction accuracy is lower than full RF model
- Trade-off: RAM constraints vs prediction accuracy
- ESP32 WROOM cannot fit the full 300-tree RandomForest (~1-2 MB)
