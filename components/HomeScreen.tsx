import { View, Text, Pressable, Modal } from "react-native"
import ReadNow from "./ReadNow";
import TriviaBoard from "./TriviaBoard"
import ReadingCard from 'components/ReadingCard'
import MaterialCommunityIcons from '@expo/vector-icons/MaterialCommunityIcons';
import Entypo from '@expo/vector-icons/Entypo';
import FontAwesome6 from '@expo/vector-icons/FontAwesome6'; 
import CardModal from "./CardModal";
import { BlurView } from "expo-blur";
import { useBluetooth } from "routes/bluetoothScan";
import { useState } from "react";
import { BleManager } from "react-native-ble-plx";
import TempLogo from '../assets/Temp_Logo.png'
import CarbonLogo from '../assets/Carbon_Logo.png'
import HumidityLogo from '../assets/Humidity_Logo.png'
import GasLogo from '../assets/Gas_Logo.png'


const manager = new BleManager();

export default function Home(){

  const [modal, setModal] = useState(false);
  const [tab, setTab] = useState("Default");

  const { message, startScan, humidity, temperature, scanning, pressure, gasResistance } = useBluetooth();

    return(<>
        <View className='items-center justify-center h-[220px]'>
          <TriviaBoard/>
        </View>
          <View className='flex h-auto'>
            <View className=' h-auto p-[5px] bg-white rounded-[20px'>
              <Text className='text-newBackground text-[20px] justify-center p-[5px] px-[15px]'>Standard Readings</Text>
              <View className='flex items-center justify-between p-[]'>
                <ReadingCard title='Gas' logo={ GasLogo } progressNum={ gasResistance ? Number(gasResistance) / 100 : 0 } setTab={ setTab }/>
                <ReadingCard title='Humidity' logo={ HumidityLogo } progressNum={ humidity ? Number(humidity) / 100 : 0 } setTab={ setTab }/>
                <ReadingCard title='Temperature' logo={ TempLogo } progressNum={ temperature ? Number(temperature) / 100 : 0 } setTab={ setTab }/>
                <ReadingCard title='Carbon Dioxide' logo={ CarbonLogo } progressNum={ pressure ? Number(pressure) / 100 : 0 } setTab={ setTab }/>
              </View>
            </View>
            <View className=''>
              <Pressable onPress={() => setModal(true)} className=' p-[1px]'>
                <View className=' items-center justify-center gap-[5px] p-[10px]'>
                <Text className="text-white">Check full freshness report!</Text>
                <ReadNow/>
              </View>
              </Pressable>

              {/* Connect to Bluetooth button */}
              <Pressable className='' onPress={ startScan } >
                <View className=' items-center justify-center gap-[5px] h-[60px]'>
                <Text className='border px-[55px] p-[10px] rounded-[10px] bg-white text-newDarkText border-darkgreentext'>{ message }</Text>
              </View>
              </Pressable>
            </View>
          </View>
          
        {modal && 
          <Modal transparent={ true } className='items-center' animationType='fade'>
            <BlurView intensity={ 360 } tint='extraLight' className='flex-1'>
              <View className=' p-[5px] gap-[5px] flex-1 justify-center'>
                <View className='py-[20px] rounded-[15px] bg-lightgreenbg border border-darkgreentext'>
                  <View className=' p-[5px] items-center'>
                    <Text className='text-darkgreentext text-[20px]'>🥑 Final Prediction Result</Text>
                  </View>
                  <View>
                    <View className='p-[3px]'>
                      <View className='p-[2px]'>
                        <Text className='text-darkgreentext'>Content: </Text>
                      </View>
                      <View className=' p-[5px] gap-1'>
                        <Text className='text-avocadoText'>Freshness Status: Ripe</Text>
                        <Text className='text-avocadoText'>Confidence: 92%</Text>
                        <Text className='text-avocadoText'>CO2 Level: 450ppm</Text>
                        <Text className='text-avocadoText'>VOC Level: 320ppm</Text>
                      </View>
                    </View>
                    
                    <View className='p-[5px]'>
                      <Text className='text-darkgreentext'>Shelf Life Estimate: 2 days remaining</Text>
                    </View>
                    <View className='p-[5px]'>
                      <Text className='text-darkgreentext'>Note: This avocado is ready to eat within 1–2 days.</Text>
                    </View>
                  </View>
                  <Pressable onPress={() => setModal(false)}>
                    <View className='items-center mt-[5px]'>
                      <Text className='border px-[30px] py-[2px] text-darkgreentext bg-lightgreenbg rounded-[20px]'>Back</Text>
                    </View>
                  </Pressable>
                </View>
              </View>
            </BlurView>
          </Modal>
        }
        {tab == `Gas` && 
        <Modal transparent={true} animationType='fade'>
          <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
            <View className=' flex-1 justify-center items-center'>
              <CardModal logo={ <MaterialCommunityIcons name="fire" size={24} color="black"/> } Title={`Gas`} sensorModel={`BME680`} currentReading={`VOC Index: ${ gasResistance }`} setTab={ setTab }/>
            </View>
          </BlurView>
        </Modal>
        }
        {tab == `Humidity` && 
        <Modal transparent={true} animationType='fade'>
          <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
            <View className=' flex-1 justify-center items-center'>
              <CardModal Title={`Humidity`} sensorModel={`SHT31`} currentReading={`Humidity: ${ humidity }`} setTab={ setTab } logo={ <Entypo name="water" size={24} color="black"/> }/>
            </View>
          </BlurView>
        </Modal>
        }
        {tab == `Temperature` && 
        <Modal transparent={true} animationType='fade'>
          <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
            <View className=' flex-1 justify-center items-center'>
              <CardModal logo={ <FontAwesome6 name="temperature-half" size={24} color="black"/> } Title={`Temperature`} sensorModel={`SHT31`} currentReading={`Temperature: ${ temperature }`} setTab={ setTab } />
            </View>
          </BlurView>
        </Modal>
        }
        {tab == `Carbon Dioxide` && 
        <Modal transparent={true} animationType='fade'>
          <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
            <View className=' flex-1 justify-center items-center'>
              <CardModal logo={ <Entypo name="air" size={24} color="black" /> } Title={`Carbon Dioxide`} sensorModel={`NDIR CO₂`} currentReading={`Carbon Dioxide: ${ pressure }`} setTab={ setTab }/>
            </View>
          </BlurView>
        </Modal>
      }
    </>)
} 