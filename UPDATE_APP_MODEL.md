# How to Update the App with New Model

## Problem
Your app is showing different predictions than `predict_cli.py` because it's using cached old model files.

## Solution: Clear Cache and Rebuild

### Option 1: Clear Metro Bundler Cache (Recommended)

```bash
# Stop the app if it's running (Ctrl+C)

# Clear cache and restart
npx expo start -c
```

The `-c` flag clears the cache. Then:
1. Press `a` for Android or `i` for iOS
2. Wait for the app to rebuild
3. Test again with the same sensor values

### Option 2: Full Clean (If Option 1 doesn't work)

```bash
# Stop the app

# Clear all caches
rm -rf node_modules/.cache
rm -rf .expo

# Restart
npx expo start -c
```

### Option 3: Android Specific (If using Android)

```bash
cd android
./gradlew clean
cd ..
npx expo start -c
```

## Verify It's Fixed

After rebuilding, test with these values in your app:

```
Gas Resistance: 187.0
CO2: 2847
Temperature: 31.2
Humidity: 75.8
Pressure: 1004.2
```

**Expected result:**
- Ripeness: **overripe** (class 4)
- Shelf Life: **0 hours (0 days)**

If you still see "unripe (2.4 days)", the cache wasn't cleared.

## Why This Happens

React Native/Expo bundles assets (like JSON files) at build time. When you update the JSON files, the app needs to:
1. Clear the old cached bundle
2. Rebuild with the new files

Simply copying files to `assets/` isn't enough - the app must be rebuilt.

## Alternative: Force Reload in App

If you're in development mode:
1. Shake your device (or press Cmd+D on iOS / Cmd+M on Android)
2. Select "Reload"
3. If that doesn't work, select "Debug" → "Clear Cache and Reload"

## Verification Script

After updating, run this to verify CLI and app match:

```bash
cd ML
python verify_match.py
```

Then test the same values in both CLI and app - they should match!
