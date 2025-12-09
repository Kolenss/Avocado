// bluetoothManager.ts
import { BleManager } from 'react-native-ble-plx';
import { useState, useEffect } from 'react';
import { Buffer } from 'buffer';
import { Platform, PermissionsAndroid, Alert } from 'react-native';

const manager = new BleManager();

export const bluetoothManager = {
  message: "Press scan to start...",
  scanning: false,
  temperature: null as string | null,
  humidity: null as string | null,
  startScan: async function() {
    if (this.scanning) return;
    this.scanning = true;
    this.message = "Scanning for ESP32_Sensor...";

    if (Platform.OS === "android") {
      if (Platform.Version >= 31) {
        await PermissionsAndroid.requestMultiple([
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        ]);
      } else {
        await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION);
      }
    }

    manager.startDeviceScan(null, null, async (error, device) => {
      if (error) {
        Alert.alert("Scan Error", error.message);
        this.scanning = false;
        return;
      }

      if (device?.name === "ESP32_Sensor") {
        this.message = `Found device: ${device.name}`;
        manager.stopDeviceScan();

        try {
          const connectedDevice = await device.connect();
          await connectedDevice.discoverAllServicesAndCharacteristics();

          const services = await connectedDevice.services();
          for (const service of services) {
            const characteristics = await service.characteristics();
            for (const c of characteristics) {
              if (c.isNotifiable) {
                c.monitor((err, characteristic) => {
                  if (err) {
                    this.message = `Error: ${err.message}`;
                    return;
                  }
                  if (characteristic?.value) {
                    const decoded = Buffer.from(characteristic.value, "base64").toString("utf8");
                    const match = decoded.match(/TEMP:(\d+\.\d+),HUM:(\d+\.\d+)/);
                    if (match) {
                      this.temperature = match[1];
                      this.humidity = match[2];
                    }
                  }
                });
                return;
              }
            }
          }
        } catch (err: any) {
          this.message = `Connection error: ${err.message}`;
        } finally {
          this.scanning = false;
        }
      }
    });

    setTimeout(() => {
      manager.stopDeviceScan();
      this.scanning = false;
      this.message = "Scan stopped.";
    }, 10000);
  }
};
