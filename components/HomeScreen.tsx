import { View, Text, Pressable, Modal, ScrollView } from "react-native"
import ReadNow from "./ReadNow";
import TriviaBoard from "./TriviaBoard"
import ReadingCard from 'components/ReadingCard'

import CardModal from "./CardModal";
import { useBluetooth } from "routes/bluetoothScan";
import { useState } from "react";
import { fetchPrediction } from "routes/prediction";
import TempLogo from '../assets/Temp_Logo.png'
import CarbonLogo from '../assets/Carbon_Logo.png'
import HumidityLogo from '../assets/Humidity_Logo.png'
import GasLogo from '../assets/Gas_Logo.png'
import TestPrediction from "./test";

export default function Home(){

  const [modal, setModal] = useState(false);
  const [tab, setTab] = useState("Default");

  const { message, startScan, humidity, temperature, pressure, gasResistance, co2, prediction } = useBluetooth();
  const [localPrediction, setLocalPrediction] = useState(prediction);
  const [predicting, setPredicting] = useState(false);

  async function runPrediction() {
    if (!temperature || !humidity || !pressure || !gasResistance || !co2) return;
    setPredicting(true);
    
    try {
      // Run prediction on current sensor values
      const result = await fetchPrediction(temperature, humidity, pressure, gasResistance, co2);
      setLocalPrediction(result);
    } catch (e) {
      console.error("[ML] Manual prediction error:", e);
    } finally {
      setPredicting(false);
      setModal(true);
    }
  }

  return(<>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 10 }}>
      <View className='items-center justify-center h-[200px]'>
        <TriviaBoard/>
      </View>
        <View className='flex h-auto'>
          <View className=' h-auto p-[3px] bg-white rounded-[20px] border border-green rounded-[25px]'>
            <Text className='text-newBackground text-[16px] justify-center p-[3px] px-[12px]'>Standard Readings</Text>
            <View className='flex items-center justify-between'>
              <ReadingCard title='Temperature' logo={ TempLogo } progressNum={ temperature ? Number(temperature) / 100 : 0 } setTab={ setTab }/>
              <ReadingCard title='Humidity' logo={ HumidityLogo } progressNum={ humidity ? Number(humidity) / 100 : 0 } setTab={ setTab }/>
              <ReadingCard title='Pressure' logo={ GasLogo } progressNum={ pressure ? Number(pressure) / 100 : 0 } setTab={ setTab }/>
              <ReadingCard title='Gas' logo={ GasLogo } progressNum={ gasResistance ? Number(gasResistance) / 100 : 0 } setTab={ setTab }/>
              <ReadingCard title='Carbon Dioxide' logo={ CarbonLogo } progressNum={ co2 ? Number(co2) / 100 : 0 } setTab={ setTab }/>
            </View>
          </View>
          <View className=''>
            <Pressable onPress={runPrediction} className=' p-[1px]'>
              <View className=' items-center justify-center gap-[3px] p-[6px]'>
              <Text className="text-white text-[13px]">{predicting ? 'Analyzing...' : 'Check full freshness report!'}</Text>
              <ReadNow/>
            </View>
            </Pressable>

            {/* Connect to Bluetooth button */}
            <Pressable className='' onPress={ startScan } >
              <View className=' items-center justify-center gap-[3px] h-[48px]'>
              <Text className='border px-[40px] p-[8px] rounded-[10px] bg-white text-newDarkText border-darkgreentext text-[13px]'>{ message }</Text>
            </View>
            </Pressable>
          </View>
        </View>
      </ScrollView>
        
      {modal && 
        <Modal transparent={ true } className='items-center' animationType='fade'>
          <View style={{ flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.7)' }}>
            <View className=' p-[5px] gap-[5px] flex-1 justify-center'>
              <View className='py-[20px] px-[15px] rounded-[20px] bg-newBackground mx-[10px]'>
                <View className=' p-[5px] items-center mb-[10px]'>
                  <Text className='text-darkgreentext text-[22px] font-bold'>🥑 Freshness Report</Text>
                </View>
                <View className='bg-lightgreenbg rounded-[12px] p-[15px] mb-[10px]'>
                  <View className='mb-[15px]'>
                    <Text className='text-newDarkText font-semibold text-[16px] mb-[8px]'>Prediction Results</Text>
                    <View className='gap-[6px]'>
                      <Text className='text-darkgreentext text-[15px]'>
                        Freshness Status: <Text className='font-bold text-darkgreentext'>{localPrediction.ripeness_label}</Text>
                      </Text>
                      <Text className='text-darkgreentext text-[15px]'>
                        Shelf Life: <Text className='font-bold text-darkgreentext'>
                          {localPrediction.shelf_life_days > 0
                            ? `${localPrediction.shelf_life_days.toFixed(1)} days (${localPrediction.shelf_life_hours.toFixed(0)} hrs)`
                            : '0 days'}
                        </Text>
                      </Text>
                    </View>
                  </View>
                  
                  <View className='mb-[15px]'>
                    <Text className='text-newDarkText font-semibold text-[16px] mb-[8px]'>Sensor Readings</Text>
                    <View className='gap-[6px]'>
                      <Text className='text-darkgreentext text-[15px]'>
                        CO₂ Level: <Text className='font-bold text-darkgreentext'>{co2 || '0'} ppm</Text>
                      </Text>
                      <Text className='text-darkgreentext text-[15px]'>
                        VOC (Gas): <Text className='font-bold text-darkgreentext'>{gasResistance ? `${Number(gasResistance).toFixed(1)}` : '0.0'} KΩ</Text>
                      </Text>
                      <Text className='text-darkgreentext text-[15px]'>
                        Temperature: <Text className='font-bold text-darkgreentext'>{temperature ? `${Number(temperature).toFixed(1)}` : '0.0'}°C</Text>
                      </Text>
                      <Text className='text-darkgreentext text-[15px]'>
                        Humidity: <Text className='font-bold text-darkgreentext'>{humidity ? `${Number(humidity).toFixed(1)}` : '0.0'}%</Text>
                      </Text>
                      <Text className='text-darkgreentext text-[15px]'>
                        Pressure: <Text className='font-bold text-darkgreentext'>{pressure ? `${Number(pressure).toFixed(1)}` : '0.0'} hPa</Text>
                      </Text>
                    </View>
                  </View>
                  
                  <View className='bg-newBackground/30 p-[10px] rounded-[8px]'>
                    <Text className='text-darkgreentext text-[14px]'>
                      💡 <Text className='font-semibold'>Note:</Text> {localPrediction.note}
                    </Text>
                  </View>
                </View>
                
                <Pressable onPress={() => setModal(false)}>
                  <View className='items-center mt-[5px] bg-newDarkText py-[10px] rounded-[10px]'>
                    <Text className='text-white font-semibold text-[16px]'>Close</Text>
                  </View>
                </Pressable>
              </View>
            </View>
          </View>
        </Modal>
      }
      {tab == `Gas` && 
      <Modal transparent={true} animationType='fade'>
        <View style={{ flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.7)' }}>
          <View className='flex-1 justify-center items-center'>
            <CardModal logo={ GasLogo } Title={`Gas`} sensorModel={`BME680`} currentReading={`${gasResistance ? Number(gasResistance).toFixed(1) : '0.0'} KΩ`} setTab={ setTab }/>
          </View>
        </View>
      </Modal>
      }
      {tab == `Humidity` && 
      <Modal transparent={true} animationType='fade'>
        <View style={{ flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.7)' }}>
          <View className='flex-1 justify-center items-center'>
            <CardModal logo={ HumidityLogo } Title={`Humidity`} sensorModel={`SHT31`} currentReading={`${humidity ? Number(humidity).toFixed(1) : '0.0'} %`} setTab={ setTab }/>
          </View>
        </View>
      </Modal>
      }
      {tab == `Temperature` && 
      <Modal transparent={true} animationType='fade'>
        <View style={{ flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.7)' }}>
          <View className='flex-1 justify-center items-center'>
            <CardModal logo={ TempLogo } Title={`Temperature`} sensorModel={`SHT31`} currentReading={`${temperature ? Number(temperature).toFixed(1) : '0.0'} °C`} setTab={ setTab }/>
          </View>
        </View>
      </Modal>
      }
      {tab == `Pressure` && 
      <Modal transparent={true} animationType='fade'>
        <View style={{ flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.7)' }}>
          <View className='flex-1 justify-center items-center'>
            <CardModal logo={ GasLogo } Title={`Pressure`} sensorModel={`BME680`} currentReading={`${pressure ? Number(pressure).toFixed(1) : '0.0'} hPa`} setTab={ setTab }/>
          </View>
        </View>
      </Modal>
      }
      {tab == `Carbon Dioxide` && 
      <Modal transparent={true} animationType='fade'>
        <View style={{ flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.7)' }}>
          <View className='flex-1 justify-center items-center'>
            <CardModal logo={ CarbonLogo } Title={`Carbon Dioxide`} sensorModel={`MH-Z14A`} currentReading={`${co2 || '0'} ppm`} setTab={ setTab }/>
          </View>
        </View>
      </Modal>
    }
  </>)
}
