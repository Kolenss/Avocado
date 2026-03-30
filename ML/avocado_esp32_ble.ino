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
#define CHAR_READ_UUID      "beb5483e-36e1-4688-b7f5-ea07361b26a8"  // Read sensor data
#define CHAR_COMMAND_UUID   "beb5483e-36e1-4688-b7f5-ea07361b26a9"  // Write commands

Adafruit_BME680 bme;
Adafruit_SHT31 sht31 = Adafruit_SHT31();
HardwareSerial MHZSerial(2);

// MH-Z14A commands
byte cmd_getData[9] = {0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0x79};
byte response[9];

// BLE
BLEServer* pServer = NULL;
BLECharacteristic* pCharRead = NULL;
BLECharacteristic* pCharCommand = NULL;
bool deviceConnected = false;
bool readRequested = false;

// Sensor data
float temperature = 0;
float humidity = 0;
float pressure = 0;
float gasResistance = 0;
int co2 = 0;

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

class CommandCallbacks: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    std::string value = pCharacteristic->getValue();
    if (value.length() > 0) {
      Serial.print("Command received: ");
      Serial.println(value.c_str());
      
      if (value == "READ") {
        readRequested = true;
        Serial.println("Fresh read requested");
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

  // Read characteristic (notify)
  pCharRead = pService->createCharacteristic(
    CHAR_READ_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharRead->addDescriptor(new BLE2902());

  // Command characteristic (write)
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

  Serial.println("All Sensors Initialized!");
}

int readCO2() {
  while (MHZSerial.available()) {
    MHZSerial.read();
  }

  MHZSerial.write(cmd_getData, 9);
  delay(100);

  if (MHZSerial.available() >= 9) {
    for (int i = 0; i < 9; i++) {
      response[i] = MHZSerial.read();
    }

    if (response[0] == 0xFF && response[1] == 0x86) {
      int co2 = (response[2] << 8) + response[3];
      return co2;
    }
  }
  return -1;
}

void readSensors() {
  // Read SHT35
  temperature = sht31.readTemperature();
  humidity = sht31.readHumidity();

  // Read BME680
  if (bme.performReading()) {
    pressure = bme.pressure / 100.0;
    gasResistance = bme.gas_resistance / 1000.0;
  }

  // Read MH-Z14A
  co2 = readCO2();

  Serial.println("========== SENSOR DATA ==========");
  Serial.print("Temperature: "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
  Serial.print("Pressure: "); Serial.print(pressure); Serial.println(" hPa");
  Serial.print("Gas Resistance: "); Serial.print(gasResistance); Serial.println(" KOhms");
  Serial.print("CO2: "); Serial.print(co2); Serial.println(" ppm");
  Serial.println("=================================");
}

void sendBLEData() {
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
}

void loop() {
  // Auto-read every 5 seconds
  static unsigned long lastAutoRead = 0;
  if (millis() - lastAutoRead > 5000) {
    readSensors();
    sendBLEData();
    lastAutoRead = millis();
  }

  // Manual read on command
  if (readRequested) {
    Serial.println(">>> Manual read triggered <<<");
    readSensors();
    sendBLEData();
    readRequested = false;
  }

  delay(100);
}
