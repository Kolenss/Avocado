

// bluetoothScan.ts
import { useState, useEffect } from 'react';
import { Platform, PermissionsAndroid, Alert } from 'react-native';
import { Buffer } from 'buffer'; // For decoding base64 data
import { BleManager } from "react-native-ble-plx";


// Replace with your actual manager import
const manager = new BleManager();

const useBluetoothScan = () => {
  const [modal, setModal] = useState(false);
  const [tab, setTab] = useState("Default");
  const [message, setMessage] = useState("Press scan to start...");
  const [scanning, setScanning] = useState(false);
  const [temperature, setTemperature] = useState<string | null>(null);
  const [humidity, setHumidity] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      manager.destroy();
    };
  }, []);

  const requestPermissions = async () => {
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
  };

  const startScan = async () => {
    await requestPermissions();
    setScanning(true);
    setMessage("Scanning for ESP32_Sensor...");

    manager.startDeviceScan(null, null, async (error, device) => {
      if (error) {
        Alert.alert("Scan Error", error.message);
        setScanning(false);
        return;
      }

      if (device?.name) console.log("Found:", device.name);

      if (device?.name === "ESP32_Sensor") {
        setMessage(`Found device: ${device.name}`);
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
                    setMessage(`Error: ${err.message}`);
                    return;
                  }
                  if (characteristic?.value) {
                    const decoded = Buffer.from(characteristic.value, "base64").toString("utf8");
                    setMessage(decoded);

                    const match = decoded.match(/TEMP:(\d+\.\d+),HUM:(\d+\.\d+)/);
                    if (match) {
                      setTemperature(match[1]);
                      setHumidity(match[2]);
                    }
                  }
                });
                return;
              }
            }
          }
        } catch (err: any) {
          setMessage(`Connection error: ${err.message}`);
        } finally {
          setScanning(false);
        }
      }
    });

    setTimeout(() => {
      manager.stopDeviceScan();
      setScanning(false);
      setMessage("Scan stopped.");
    }, 10000);
  };

  return {
    modal,
    setModal,
    tab,
    setTab,
    message,
    temperature,
    humidity,
    scanning,
    startScan,
  };
};

export default useBluetoothScan;
