# FORCE UPDATE: App Still Using Old Model

## Confirmed Issue
The JSON files in `assets/` ARE the new model ✓  
But your app is loading OLD cached files ✗

## Nuclear Option: Complete Clean Build

Do ALL of these steps in order:

### Step 1: Stop Everything
```bash
# Stop any running Metro bundler or app (Ctrl+C)
```

### Step 2: Delete ALL Cache
```bash
# Delete Metro bundler cache
Remove-Item -Recurse -Force node_modules\.cache -ErrorAction SilentlyContinue

# Delete Expo cache
Remove-Item -Recurse -Force .expo -ErrorAction SilentlyContinue

# Delete Android build cache
Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\build -ErrorAction SilentlyContinue

# Delete Gradle cache (optional but recommended)
Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
```

### Step 3: Clean Android Build
```bash
cd android
./gradlew clean
cd ..
```

### Step 4: Regenerate Native Projects
```bash
npx expo prebuild --clean
```

### Step 5: Build and Install Fresh
```bash
npx expo run:android
```

Wait for the complete build and installation.

### Step 6: Test
Enter these values in your app:
```
Gas Resistance: 239.4
CO2: 1158
Temperature: 31.3
Humidity: 74.6
Pressure: 1004.0
```

**Should show:** overripe (0 days) ✓

## Alternative: Manual Asset Copy

If the above doesn't work, the assets might not be bundling correctly. Try this:

### Check where assets are bundled:
```bash
# After building, check:
dir android\app\build\generated\assets\
```

The JSON files should be there. If not, there's a bundling issue.

## Last Resort: Hardcode Asset Path

If nothing works, we can modify the app to load from a different location or embed the model differently. But try the nuclear option first!

## Verification

After rebuilding, the app console should show:
```
[ML] Loaded regression trees: 300 trees
[ML] Loaded classification trees: 300 trees
```

And predictions should match `predict_cli.py` exactly.
