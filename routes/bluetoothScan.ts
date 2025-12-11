// bluetoothManager.ts
import { create } from 'zustand';
import { BleManager } from "react-native-ble-plx";
import { Buffer } from "buffer";
import { PermissionsAndroid, Platform } from "react-native";
import { template } from '@babel/core';

const ble = new BleManager();

type BluetoothStore = {
  message: string;
  scanning: boolean;
  temperature: string | null;
  humidity: string | null;
  pressure: string | null;
  gasResistance: string | null;

  startScan: () => Promise<void>;
};

export const useBluetooth = create<BluetoothStore>((set, get) => ({
  message: "Press scan to start...",
  scanning: false,
  temperature: null,
  humidity: null,
  pressure: null,
  gasResistance: null,

  startScan: async () => {
    const scanning = get().scanning;
    if (scanning) return;

    set({ scanning: true, message: "Scanning..." });

    // Android permissions
    if (Platform.OS === "android") {
      if (Platform.Version >= 31) {
        await PermissionsAndroid.requestMultiple([
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        ]);
      } else {
        await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
        );
      }
    }

    // Start scanning
    ble.startDeviceScan(null, null, async (error, device) => {
      if (error) {
        set({ message: error.message, scanning: false });
        return;
      }

      if (device?.name === "ESP32_Sensor") {
        ble.stopDeviceScan();
        set({ message: "Connecting..." });

        const connected = await device.connect();

        // Request bigger MTU so full message can fit
        await connected.requestMTU(128);

        await connected.discoverAllServicesAndCharacteristics();

        const services = await connected.services();

        for (const service of services) {
          const chars = await service.characteristics();

          for (const c of chars) {
            if (c.isNotifiable) {
              // Start monitoring notifications
              c.monitor((err, characteristic) => {
                if (err) {
                  set({ message: `Error: ${err.message}` });
                  return;
                }

                if (characteristic?.value) {
                  const decoded = Buffer.from(characteristic.value, "base64")
                    .toString("utf8")
                    .trim()
                    .replace(/\0/g, "");

                  console.log("RAW BASE64:", characteristic.value);
                  console.log("DECODED:", decoded);

                  // Match TEMP, HUM, PRES, GAS
                  const match = decoded.match(
                    /TEMP:([\d.]+),HUM:([\d.]+),PRES:([\d.]+),GAS:([\d.]+)/
                  );

                  if (match) {
                    set({
                      temperature: match[1],
                      humidity: match[2],
                      pressure: match[3],
                      gasResistance: match[4],
                    });
                  }
                }
              });
            }
          }
        }

        // Mark connected after starting monitor
        set({ message: "Connected!", scanning: false });
      }
    });

    // Stop scanning after 10 seconds (safety)
    setTimeout(() => {
      ble.stopDeviceScan();
      set({ scanning: false, message: "Scan stopped." });
    }, 10000);
  },
}));
