# Avocado Ripeness System - Architecture

## Option 1: ESP32 with On-Device ML (Current - RAM Limited)

```
┌─────────────────────────────────────────┐
│           ESP32 WROOM                   │
│  ┌──────────────────────────────────┐   │
│  │  Sensors                         │   │
│  │  - BME680 (temp, humidity, gas)  │   │
│  │  - SHT31 (temp, humidity)        │   │
│  │  - MH-Z14A (CO2)                 │   │
│  └──────────────────────────────────┘   │
│              ↓                          │
│  ┌──────────────────────────────────┐   │
│  │  TFLite Micro Models             │   │
│  │  - Classifier (13 KB)            │   │
│  │  - Regressor (5 KB, simplified)  │   │
│  │  Arena: 56 KB total              │   │
│  └──────────────────────────────────┘   │
│              ↓                          │
│  ┌──────────────────────────────────┐   │
│  │  Predictions                     │   │
│  │  - Ripeness class                │   │
│  │  - Shelf life (±36h error)       │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Pros:**
- Standalone operation
- No internet required
- Instant predictions

**Cons:**
- Limited RAM (520 KB)
- Simplified model (lower accuracy)
- ~36 hour prediction error vs full RF

---

## Option 2: ESP32 as Sensor Node + App ML (RECOMMENDED)

```
┌─────────────────────────────┐
│       ESP32 WROOM           │
│  ┌──────────────────────┐   │
│  │  Sensors             │   │
│  │  - BME680            │   │
│  │  - SHT31             │   │
│  │  - MH-Z14A           │   │
│  └──────────────────────┘   │
│           ↓                 │
│  ┌──────────────────────┐   │
│  │  JSON Output         │   │
│  │  {                   │   │
│  │   "temperature": 31.5│   │
│  │   "humidity": 67.1   │   │
│  │   "pressure": 1012.4 │   │
│  │   "gas_resistance":  │   │
│  │      453.63          │   │
│  │   "co2": 1020        │   │
│  │  }                   │   │
│  └──────────────────────┘   │
└─────────────────────────────┘
           ↓
    Serial / WiFi / BLE
           ↓
┌─────────────────────────────┐
│    App / Server             │
│  ┌──────────────────────┐   │
│  │  Full RandomForest   │   │
│  │  - 300 trees         │   │
│  │  - ~1-2 MB model     │   │
│  │  - High accuracy     │   │
│  └──────────────────────┘   │
│           ↓                 │
│  ┌──────────────────────┐   │
│  │  Predictions         │   │
│  │  - Ripeness class    │   │
│  │  - Shelf life        │   │
│  │    (accurate)        │   │
│  └──────────────────────┘   │
└─────────────────────────────┘
```

**Pros:**
- Full RandomForest accuracy
- No RAM constraints
- Easy to update model
- Can add more features
- Better logging/analytics

**Cons:**
- Requires connectivity
- Slightly higher latency
- App/server dependency

---

## Implementation Files

### Option 2 Files (Sensor Node + App ML)

**ESP32 Code:**
- `avocado_esp32_sensor_only.ino` - Reads sensors, outputs JSON

**App/Server Code:**
- `app_predict.py` - Receives data, runs RandomForest
- `shelf_life_regressor.joblib` - Full RF model

### Usage

**1. Upload ESP32 sketch:**
```bash
# Open avocado_esp32_sensor_only.ino in Arduino IDE
# Select board: ESP32 Dev Module
# Upload
```

**2. Run app prediction:**
```bash
# From serial port (real-time)
python app_predict.py --serial COM3

# From JSON (single prediction)
python app_predict.py --json '{"temperature":31.5,"humidity":67.1,"pressure":1012.4,"gas_resistance":453.63,"co2":1020}'

# Test mode (no args)
python app_predict.py
```

---

## Communication Options

### 1. Serial (USB Cable)
- **Use:** Development, testing
- **Code:** `app_predict.py --serial COM3`
- **Pros:** Simple, reliable
- **Cons:** Wired connection

### 2. WiFi (HTTP/MQTT)
- **Use:** Production, remote monitoring
- **ESP32:** Add WiFi client code
- **Server:** REST API or MQTT broker
- **Pros:** Wireless, scalable
- **Cons:** Requires network setup

### 3. Bluetooth Low Energy (BLE)
- **Use:** Mobile app
- **ESP32:** BLE server
- **App:** BLE client (iOS/Android)
- **Pros:** Low power, direct to phone
- **Cons:** Limited range

---

## Recommendation

**Use Option 2 (Sensor Node + App ML)** because:

1. **Full accuracy** - No compromise on predictions
2. **Simpler ESP32 code** - Just sensor reading
3. **Flexible** - Easy to update model without reflashing ESP32
4. **Scalable** - Can add more sensors/features
5. **Better UX** - App can show history, trends, notifications

The ESP32 becomes a simple, reliable sensor node, and all the intelligence lives in your app where you have unlimited resources.
