# Complete clean and rebuild script for React Native app
# This ensures the app uses the latest model files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMPLETE CLEAN AND REBUILD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Delete caches
Write-Host "Step 1: Deleting all caches..." -ForegroundColor Yellow
Remove-Item -Recurse -Force node_modules\.cache -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .expo -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
Write-Host "✓ Caches deleted" -ForegroundColor Green
Write-Host ""

# Step 2: Clean Gradle
Write-Host "Step 2: Cleaning Gradle build..." -ForegroundColor Yellow
Set-Location android
& .\gradlew clean
Set-Location ..
Write-Host "✓ Gradle cleaned" -ForegroundColor Green
Write-Host ""

# Step 3: Prebuild
Write-Host "Step 3: Regenerating native projects..." -ForegroundColor Yellow
npx expo prebuild --clean
Write-Host "✓ Native projects regenerated" -ForegroundColor Green
Write-Host ""

# Step 4: Build and run
Write-Host "Step 4: Building and installing app..." -ForegroundColor Yellow
Write-Host "This will take a few minutes..." -ForegroundColor Gray
Write-Host ""
npx expo run:android

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BUILD COMPLETE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test with these values:" -ForegroundColor Yellow
Write-Host "  Gas Resistance: 239.4" -ForegroundColor White
Write-Host "  CO2: 1158" -ForegroundColor White
Write-Host "  Temperature: 31.3" -ForegroundColor White
Write-Host "  Humidity: 74.6" -ForegroundColor White
Write-Host "  Pressure: 1004.0" -ForegroundColor White
Write-Host ""
Write-Host "Expected: overripe (0 days)" -ForegroundColor Green
