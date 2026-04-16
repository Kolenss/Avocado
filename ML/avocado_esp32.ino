/*
 * Avocado Ripeness + Shelf Life Detector
 * ESP32 WROOM + BME680 + SHT31 + MH-Z14A + TFLite Micro
 *
 * Libraries (Arduino Library Manager):
 *   - Chirale_TensorFlowLite  by spaziochirale
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

#include <Chirale_TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include "avocado_ripeness_model_data.h"

// ── Pin config ────────────────────────────────────────────────────────────────
#define SDA_PIN 21
#define SCL_PIN 22
#define RX_PIN  16
#define TX_PIN  17

// ── Model config ──────────────────────────────────────────────────────────────
#define N_INPUTS           5
#define N_CLS_OUTPUTS      7
#define ARENA_CLS_SIZE     (32 * 1024)    // 32 KB for classifier
#define ARENA_REG_SIZE     (24 * 1024)    // 24 KB for regressor (minimal to fit RAM)

// ── Labels ────────────────────────────────────────────────────────────────────
static const char* LABELS[N_CLS_OUTPUTS] = {
  "Unripe", "Near Ripe", "Ripe", "Very Ripe", "Overripe", "Molds", "Rotten"
};

// ── Sensors ───────────────────────────────────────────────────────────────────
Adafruit_BME680 bme;
Adafruit_SHT31  sht31;
HardwareSerial  MHZSerial(2);

static const byte CMD_READ_CO2[9] = {0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0x79};

// ── TFLite — Classifier ───────────────────────────────────────────────────────
static uint8_t arenaClassifier[ARENA_CLS_SIZE];
static const tflite::Model*       clsModel       = nullptr;
static tflite::MicroInterpreter*  clsInterpreter = nullptr;
static TfLiteTensor*              clsInput       = nullptr;

// ── TFLite — Regressor ────────────────────────────────────────────────────────
static uint8_t arenaRegressor[ARENA_REG_SIZE];
static const tflite::Model*       regModel       = nullptr;
static tflite::MicroInterpreter*  regInterpreter = nullptr;
static TfLiteTensor*              regInput       = nullptr;

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

// Apply StandardScaler and fill a tensor's input buffer
static void fillScaledInput(TfLiteTensor* tensor,
                             const float* mean, const float* std,
                             float temp, float humidity,
                             float pressure, float gas, float co2) {
  float raw[N_INPUTS] = { temp, humidity, pressure, gas, co2 };
  for (int i = 0; i < N_INPUTS; i++)
    tensor->data.f[i] = (raw[i] - mean[i]) / std[i];
}

static void runInference(float temp, float humidity,
                         float pressure, float gasKOhm, int co2) {
  // gas stays in kOhm — matches CSV training data scale
  fillScaledInput(clsInput, SCALER_MEAN, SCALER_STD,
                  temp, humidity, pressure, gasKOhm, (float)co2);
  if (clsInterpreter->Invoke() != kTfLiteOk) {
    Serial.println("[ERROR] Classifier inference failed");
    return;
  }
  TfLiteTensor* clsOut = clsInterpreter->output(0);
  int   bestClass = 0;
  float bestScore = clsOut->data.f[0];
  for (int i = 1; i < N_CLS_OUTPUTS; i++) {
    if (clsOut->data.f[i] > bestScore) {
      bestScore = clsOut->data.f[i];
      bestClass = i;
    }
  }

  fillScaledInput(regInput, SCALER_MEAN, SCALER_STD,
                  temp, humidity, pressure, gasKOhm, (float)co2);
  if (regInterpreter->Invoke() != kTfLiteOk) {
    Serial.println("[ERROR] Regressor inference failed");
    return;
  }
  
  TfLiteTensor* regOut = regInterpreter->output(0);
  // denormalize: model outputs [0,1], convert back to hours
  float hours = regOut->data.f[0] * (REG_Y_MAX - REG_Y_MIN) + REG_Y_MIN;
  hours = max(0.0f, hours);
  float days  = hours / 24.0f;

  Serial.printf("Ripeness   : %s (%.1f%%)\n", LABELS[bestClass], bestScore * 100.0f);
  Serial.printf("Shelf Life : %.1f hrs  (%.2f days)\n", hours, days);
}

// ── Setup ─────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println("\n=== Avocado Ripeness + Shelf Life Detector ===");
  Wire.begin(SDA_PIN, SCL_PIN);

  if (!bme.begin(0x76)) { Serial.println("[ERROR] BME680 not found"); while (1); }
  bme.setTemperatureOversampling(BME680_OS_NONE);
  bme.setHumidityOversampling(BME680_OS_NONE);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setGasHeater(320, 150);

  if (!sht31.begin(0x44)) { Serial.println("[ERROR] SHT31 not found"); while (1); }

  MHZSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);

  // Init classifier
  static tflite::AllOpsResolver resolverCls;
  clsModel = tflite::GetModel(avocado_ripeness_model_data);
  if (clsModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("[ERROR] Classifier schema mismatch"); while (1);
  }
  static tflite::MicroInterpreter clsInterp(
    clsModel, resolverCls, arenaClassifier, ARENA_CLS_SIZE);
  clsInterpreter = &clsInterp;
  if (clsInterpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("[ERROR] Classifier AllocateTensors failed"); while (1);
  }
  clsInput = clsInterpreter->input(0);

  // Init regressor
  static tflite::AllOpsResolver resolverReg;
  regModel = tflite::GetModel(avocado_shelf_life_model_data);
  if (regModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("[ERROR] Regressor schema mismatch"); while (1);
  }
  static tflite::MicroInterpreter regInterp(
    regModel, resolverReg, arenaRegressor, ARENA_REG_SIZE);
  regInterpreter = &regInterp;
  if (regInterpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("[ERROR] Regressor AllocateTensors failed"); while (1);
  }
  regInput = regInterpreter->input(0);

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

  Serial.println("──────────────────────────────");
  Serial.printf("Temp       : %.1f C\n",    temp);
  Serial.printf("Humidity   : %.1f %%\n",   humidity);
  Serial.printf("Pressure   : %.1f hPa\n",  pressure);
  Serial.printf("Gas        : %.2f kOhm\n", gasKOhm);
  Serial.printf("CO2        : %d ppm\n",    co2);

  runInference(temp, humidity, pressure, gasKOhm, co2);

  delay(1000);
}
