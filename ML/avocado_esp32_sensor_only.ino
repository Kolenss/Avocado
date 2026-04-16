/*
 * Avocado Sensor Reader - ESP32 WROOM
 * Reads BME680, SHT31, MH-Z14A sensors and sends data via Serial/WiFi
 * 
 * No ML inference on ESP32 - just raw sensor data
 * App/Server will run RandomForest prediction
 *
 * Libraries (Arduino Library Manager):
 *   - Adafruit BME680         by Adafruit
 *   - Adafruit SHT31          by Adafruit
 *   - Adafruit Unified Sensor by Adafruit
 *
 * Wiring:
 *   BME680 / SHT31 -> I2C  SDA=21, SCL=22
 *   MH-Z14A        -> UART RX=16,  TX=17
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_SHT31.h>
#include <HardwareSerial.h>

// ── Pin config ────────────────────────────────────────────────────────────────
#define SDA_PIN 21
#define SCL_PIN 22
#define RX_PIN  16
#define TX_PIN  17

// ── Sensors ───────────────────────────────────────────────────────────────────
Adafruit_BME680 bme;
Adafruit_SHT31  sht31;
HardwareSerial  MHZSerial(2);

static const byte CMD_READ_CO2[9] = {0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0x79};

// ── Helpers ───────────────────────────────────────────────────────────────────
static int readCO2() {
  while (MHZSerial.available()) MHZSerial.read();
  MHZSerial.write(CMD_READ_CO2, 9);
  delay(100);
  if (MHZSerial.available() < 9) return 0;
  byte buf[9];
  for (int i = 0; i < 9; i++) buf[i] = MHZSerial.read();
  if (buf[0] == 0xFF && buf[1] == 0x86)
    return (buf[2] << 8) | buf[3];
  return 0;
}

// ── Setup ─────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println("\n=== Avocado Sensor Reader ===");
  Wire.begin(SDA_PIN, SCL_PIN);

  if (!bme.begin(0x76)) { 
    Serial.println("[ERROR] BME680 not found"); 
    while (1); 
  }
  bme.setTemperatureOversampling(BME680_OS_NONE);
  bme.setHumidityOversampling(BME680_OS_NONE);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setGasHeater(320, 150);

  if (!sht31.begin(0x44)) { 
    Serial.println("[ERROR] SHT31 not found"); 
    while (1); 
  }

  MHZSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);

  Serial.println("Ready. Reading every 1 second...\n");
}

// ── Loop ──────────────────────────────────────────────────────────────────────
void loop() {
  float temp     = sht31.readTemperature();
  float humidity = sht31.readHumidity();
  float pressure = 0, gasKOhm = 0;
  int   co2      = readCO2();

  if (bme.performReading()) {
    pressure = bme.pressure / 100.0f;
    gasKOhm  = bme.gas_resistance / 1000.0f;
  }

  // Human-readable output
  Serial.println("──────────────────────────────");
  Serial.printf("Temp       : %.1f C\n",    temp);
  Serial.printf("Humidity   : %.1f %%\n",   humidity);
  Serial.printf("Pressure   : %.1f hPa\n",  pressure);
  Serial.printf("Gas        : %.2f kOhm\n", gasKOhm);
  Serial.printf("CO2        : %d ppm\n",    co2);

  // JSON output for app/server (easy to parse)
  Serial.print("JSON: {");
  Serial.printf("\"temperature\":%.2f,", temp);
  Serial.printf("\"humidity\":%.2f,", humidity);
  Serial.printf("\"pressure\":%.2f,", pressure);
  Serial.printf("\"gas_resistance\":%.2f,", gasKOhm);
  Serial.printf("\"co2\":%d", co2);
  Serial.println("}");

  delay(1000);
}
