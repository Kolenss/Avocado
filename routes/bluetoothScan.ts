import { create } from 'zustand';
import { BleManager } from "react-native-ble-plx";
import { Buffer } from "buffer";
import { PermissionsAndroid, Platform } from "react-native";
import { fetchPrediction, defaultPrediction, PredictionResult } from './prediction';

const ble = new BleManager();

const SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b";
const CHAR_UUID    = "beb5483e-36e1-4688-b7f5-ea07361b26a8";

type BluetoothStore = {
  message: string;
  scanning: boolean;
  connected: boolean;
  temperature: string | null;
  humidity: string | null;
  pressure: string | null;
  gasResistance: string | null;
  co2: string | null;
  prediction: PredictionResult;
  startScan: () => Promise<void>;
};

export const useBluetooth = create<BluetoothStore>((set, get) => ({
  message: "Press scan to start...",
  scanning: false,
  connected: false,
  temperature: null,
  humidity: null,
  pressure: null,
  gasResistance: null,
  co2: null,
  prediction: defaultPrediction,

  startScan: async () => {
    if (get().scanning) return;

    console.log("[BLE] startScan called");
    set({ scanning: true, message: "Scanning..." });

    if (Platform.OS === "android") {
      if (Platform.Version >= 31) {
        const results = await PermissionsAndroid.requestMultiple([
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        ]);
        console.log("[BLE] Permissions result:", JSON.stringify(results));
      } else {
        const result = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
        );
        console.log("[BLE] Location permission result:", result);
      }
    }

    let scanTimeout: ReturnType<typeof setTimeout> | null = null;

    console.log("[BLE] Starting device scan...");
    ble.startDeviceScan(null, null, async (error, device) => {
      if (error) {
        if (scanTimeout) clearTimeout(scanTimeout);
        console.error("[BLE] Scan error:", error.message, "| reason:", error.reason, "| code:", error.errorCode);
        set({ message: `Scan error: ${error.message}`, scanning: false });
        return;
      }

      if (device?.name) {
        console.log("[BLE] Device found:", device.name, "| id:", device.id);
      }

      if (device?.name === "ESP32_Sensor") {
        if (scanTimeout) clearTimeout(scanTimeout);
        ble.stopDeviceScan();
        console.log("[BLE] ESP32_Sensor found, connecting...");
        set({ message: "Connecting..." });

        try {
          const connected = await device.connect();
          console.log("[BLE] Connected to device:", connected.id);

          const mtu = await connected.requestMTU(128);
          console.log("[BLE] MTU negotiated:", mtu.mtu);

          await connected.discoverAllServicesAndCharacteristics();
          console.log("[BLE] Services and characteristics discovered");

          connected.monitorCharacteristicForService(SERVICE_UUID, CHAR_UUID, async (err, characteristic) => {
            if (err) {
              console.error("[BLE] Monitor error:", err.message, "| code:", err.errorCode);
              set({ message: `Error: ${err.message}`, connected: false });
              return;
            }

            if (characteristic?.value) {
              const decoded = Buffer.from(characteristic.value, "base64")
                .toString("utf8")
                .trim()
                .replace(/\0/g, "");

              console.log("[BLE] Raw base64:", characteristic.value);
              console.log("[BLE] Decoded:", decoded);

              const match = decoded.match(
                /TEMP:([\d.]+),HUM:([\d.]+),PRES:([\d.]+),GAS:([\d.]+),CO2:(\d+)/
              );

              if (match) {
                const [, temp, hum, pres, gas, co2] = match;
                console.log("[BLE] Parsed values — TEMP:", temp, "HUM:", hum, "PRES:", pres, "GAS:", gas, "CO2:", co2);

                set({ temperature: temp, humidity: hum, pressure: pres, gasResistance: gas, co2 });

                try {
                  const prediction = await fetchPrediction(temp, hum, pres, gas, co2);
                  console.log("[ML] Prediction result:", JSON.stringify(prediction));
                  set({ prediction });
                } catch (e: any) {
                  console.error("[ML] Prediction API error:", e?.message ?? e);
                }
              } else {
                console.warn("[BLE] Regex no match on decoded string:", decoded);
              }
            } else {
              console.warn("[BLE] Characteristic value is null/empty");
            }
          });

          set({ message: "Connected", scanning: false, connected: true });
          console.log("[BLE] Monitoring started successfully");

        } catch (e: any) {
          console.error("[BLE] Connection/setup error:", e?.message ?? e);
          set({ message: `Connection failed: ${e?.message ?? "unknown error"}`, scanning: false });
        }
      }
    });

    scanTimeout = setTimeout(() => {
      if (!get().connected) {
        console.warn("[BLE] Scan timeout — ESP32_Sensor not found");
        ble.stopDeviceScan();
        set({ scanning: false, message: "Device not found. Tap to retry." });
      }
    }, 10000);
  },
}));
