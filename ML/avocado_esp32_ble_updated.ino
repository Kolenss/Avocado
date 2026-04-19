#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_SHT31.h>
#include <HardwareSerial.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define SDA_PIN 21
#define SCL_PIN 22
#define RX_PIN 16
#define TX_PIN 17

// BLE UUIDs
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHAR_READ_UUID      "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CHAR_COMMAND_UUID   "beb5483e-36e1-4688-b7f5-ea07361b26a9"

Adafruit_BME680 bme;
Adafruit_SHT31 sht31 = Adafruit_SHT31();
HardwareSerial MHZSerial(2);

// MH-Z14A commands
byte cmd_getData[9] = {0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0x79};
byte cmd_calibrateZero[9] = {0xFF, 0x01, 0x87, 0, 0, 0, 0, 0, 0x78};
byte cmd_setRange5000[9] = {0xFF, 0x01, 0x99, 0x00, 0x00, 0x00, 0x13, 0x88, 0xCB};
byte response[9];

// BLE
BLEServer* pServer = NULL;
BLECharacteristic* pCharRead = NULL;
BLECharacteristic* pCharCommand = NULL;
bool deviceConnected = false;
bool readRequested = false;
unsigned long sensorStartTime = 0;
bool sensorWarmedUp = false;

class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    Serial.println("BLE Client Connected");
  }

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("BLE Client Disconnected");
    BLEDevice::startAdvertising();
  }
};

class CommandCallbacks: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    std::string value = pCharacteristic->getValue();
    if (value.length() > 0) {
      Serial.print("Command received: ");
      Serial.println(value.c_str());
      
      if (value == "READ") {
        readRequested = true;
        Serial.println(">>> Fresh read requested <<<");
      }
    }
  }
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Wire.begin(SDA_PIN, SCL_PIN);

  // Initialize BLE
  BLEDevice::init("ESP32_Sensor");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Read characteristic (notify sensor data)
  pCharRead = pService->createCharacteristic(
    CHAR_READ_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharRead->addDescriptor(new BLE2902());

  // Command characteristic (receive commands from app)
  pCharCommand = pService->createCharacteristic(
    CHAR_COMMAND_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );
  pCharCommand->setCallbacks(new CommandCallbacks());

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("BLE Advertising started");

  // Initialize BME680
  if (!bme.begin(0x76)) {
    Serial.println("BME680 not found!");
    while (1);
  }
  bme.setTemperatureOversampling(BME680_OS_NONE);
  bme.setHumidityOversampling(BME680_OS_NONE);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setGasHeater(320, 150);

  // Initialize SHT35
  if (!sht31.begin(0x44)) {
    Serial.println("SHT35 not found!");
    while (1);
  }

  // Initialize MH-Z14A
  MHZSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(100);

  // Set sensor range to 5000 ppm
  Serial.println("Setting MH-Z14A range to 5000 ppm...");
  MHZSerial.write(cmd_setRange5000, 9);
  delay(500);

  // Clear any response
  while (MHZSerial.available()) {
    MHZSerial.read();
  }

  sensorStartTime = millis();
  Serial.println("All Sensors Initialized!");
  Serial.println("MH-Z14A warming up... (wait 3 minutes for accurate readings)");
}

int readCO2() {
  // Clear buffer
  while (MHZSerial.available()) {
    MHZSerial.read();
  }

  // Send read command
  MHZSerial.write(cmd_getData, 9);
  delay(100);

  // Read response
  if (MHZSerial.available() >= 9) {
    for (int i = 0; i < 9; i++) {
      response[i] = MHZSerial.read();
    }

    // Debug: print raw bytes
    Serial.print("Raw response: ");
    for (int i = 0; i < 9; i++) {
      Serial.print(response[i], HEX);
      Serial.print(" ");
    }
    Serial.println();

    // Verify checksum
    byte checksum = 0;
    for (int i = 1; i < 8; i++) {
      checksum += response[i];
    }
    checksum = 0xFF - checksum;
    checksum += 1;

    if (response[0] == 0xFF && response[1] == 0x86) {
      int co2 = (response[2] << 8) + response[3];
      Serial.print("Checksum calc: ");
      Serial.print(checksum, HEX);
      Serial.print(" | received: ");
      Serial.println(response[8], HEX);

      if (checksum == response[8]) {
        Serial.println("✓ Checksum valid");
      } else {
        Serial.println("✗ Checksum mismatch!");
      }
      return co2;
    } else {
      Serial.println("Invalid response header");
      return -1;
    }
  } else {
    Serial.print("Insufficient data. Available bytes: ");
    Serial.println(MHZSerial.available());
    return -1;
  }
}

void readAndSendSensors() {
  // Check warm-up status
  if (!sensorWarmedUp && (millis() - sensorStartTime > 180000)) {
    sensorWarmedUp = true;
    Serial.println("✓ MH-Z14A warm-up complete!");
  }

  Serial.println("========== SENSOR DATA ==========");
  float temperature = 0;
  float humidity = 0;
  float pressure = 0;
  float gasResistance = 0;
  int co2 = 0;

  // ===== SHT35 =====
  temperature = sht31.readTemperature();
  humidity = sht31.readHumidity();

  if (!isnan(temperature) && !isnan(humidity)) {
    Serial.println("----- SHT35 -----");
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");
  } else {
    Serial.println("SHT35 read failed");
  }

  // ===== BME680 =====
  if (bme.performReading()) {
    pressure = bme.pressure / 100.0;
    gasResistance = bme.gas_resistance / 1000.0;
    Serial.println("----- BME680 -----");
    Serial.print("Pressure: ");
    Serial.print(pressure);
    Serial.println(" hPa");
    Serial.print("Gas Resistance: ");
    Serial.print(gasResistance);
    Serial.println(" KOhms");
  } else {
    Serial.println("BME680 reading failed");
  }

  // ===== MH-Z14A =====
  Serial.println("----- MH-Z14A -----");
  if (!sensorWarmedUp) {
    unsigned long elapsed = (millis() - sensorStartTime) / 1000;
    Serial.print("Warming up... ");
    Serial.print(elapsed);
    Serial.print("/180 seconds (");
    Serial.print((elapsed * 100) / 180);
    Serial.println("%)");
  }

  co2 = readCO2();
  if (co2 >= 0) {
    Serial.print("CO2: ");
    Serial.print(co2);
    Serial.print(" ppm");
    if (!sensorWarmedUp) {
      Serial.print(" (warming up - not accurate yet)");
    }
    Serial.println();
  } else {
    Serial.println("CO2 read failed");
  }

  Serial.println("=================================");

  // Send data via BLE
  if (deviceConnected) {
    char bleData[128];
    snprintf(bleData, sizeof(bleData), 
      "TEMP:%.2f,HUM:%.2f,PRES:%.2f,GAS:%.2f,CO2:%d",
      temperature, humidity, pressure, gasResistance, co2);
    
    pCharRead->setValue(bleData);
    pCharRead->notify();
    
    Serial.print("BLE Sent: ");
    Serial.println(bleData);
  }

  Serial.println();
}

void loop() {
  // Auto-read every 5 seconds
  static unsigned long lastAutoRead = 0;
  if (millis() - lastAutoRead > 5000) {
    readAndSendSensors();
    lastAutoRead = millis();
  }

  // Manual read on command from app
  if (readRequested) {
    Serial.println(">>> MANUAL READ TRIGGERED <<<");
    readAndSendSensors();
    readRequested = false;
  }

  delay(100);
}
