import { BleManager, Device } from 'react-native-ble-plx';
import { PermissionsAndroid, Platform } from 'react-native';

const manager = new BleManager();

export async function requestPermission(){
    if (Platform.OS == 'android' && Platform.Version >= 23) {
        await PermissionsAndroid.requestMultiple([
            PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
            PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
            PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
        ])
    }
}

export async function connectToESP32(targetName: string): Promise<Device | null> {
  return new Promise((resolve, reject) => {
    console.log('🔍 Scanning for BLE devices...');

    manager.startDeviceScan(null, null, async (error, device) => {
      if (error) {
        console.log('❌ Scan error:', error);
        reject(error);
        return;
      }

      if (device && device.name === targetName) {
        console.log(`✅ Found device: ${device.name}`);
        manager.stopDeviceScan();

        try {
          const connectedDevice = await device.connect();
          await connectedDevice.discoverAllServicesAndCharacteristics();
          console.log('📡 Connected to ESP32!');
          resolve(connectedDevice);
        } catch (err) {
          console.log('❌ Connection failed:', err);
          reject(err);
        }
      }
    });

    // Stop scanning after 10 seconds if nothing is found
    setTimeout(() => {
      manager.stopDeviceScan();
      reject(new Error('Timeout: No device found.'));
    }, 10000);
  });
}
