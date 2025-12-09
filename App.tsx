  import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
  import { Text, View, Pressable, Modal, Alert, PermissionsAndroid, Platform } from 'react-native';
  import ReadingCard from 'components/ReadingCard'
  import MaterialCommunityIcons from '@expo/vector-icons/MaterialCommunityIcons';
  import Entypo from '@expo/vector-icons/Entypo';
  import FontAwesome6 from '@expo/vector-icons/FontAwesome6'; 
  import TriviaBoard from 'components/TriviaBoard';
  import Greeting from 'components/Greetings';
  import CustomTabs from 'components/Navigation';
  import ReadNow from 'components/ReadNow';
  import './global.css';
  import { useState, useEffect } from 'react';
  import SettingsScreen from 'components/Settings';
  import StatisticScreen from 'components/Statistics';
  import { CheckedProvider, useChecked } from 'components/CheckedContext';
  import { BlurView } from "expo-blur";
  import CardModal from 'components/CardModal';
  import Informational from 'components/Informational';
  import infoData from './assets/Informational.json';
  import InfoModal from 'components/InformationalModal';
  import { BleManager } from "react-native-ble-plx";
  import { Buffer } from "buffer";
  import { bluetoothManager } from 'routes/bluetoothScan';
  
  const manager = new BleManager();

  function HomeScreen(){

  const [modal, setModal] = useState(false);
  const [tab, setTab] = useState("Default");

  const { message, startScan, humidity, temperature, scanning } = bluetoothManager;

    return(
      <>
      <View className=' h-[280px]'>
        <TriviaBoard/>
      </View>
        <View className=' flex-1' >
          <View className=' h-[290px] p-[5px]'>
            <Text className='text-darkgreentext text-[20px] h-[50px] justify-center p-[5px]'>Standard Readings</Text>
            <View className='flex flex-1 items-center justify-between shadow-lg'>
              <ReadingCard title='Gas' logo={ <MaterialCommunityIcons name="fire" size={24} color="black"/> } progressNum={0.623} setTab={ setTab }/>
              <ReadingCard title='Humidity' logo={ <Entypo name="water" size={24} color="black"/> } progressNum={ humidity } setTab={ setTab }/>
              <ReadingCard title='Temperature' logo={ <FontAwesome6 name="temperature-half" size={24} color="black"/> } progressNum={ temperature } setTab={ setTab }/>
              <ReadingCard title='Carbon Dioxide' logo={ <Entypo name="air" size={24} color="black" /> } progressNum={0.241} setTab={ setTab }/>
            </View>
          </View>
          <View className=' flex-1 justify-center'>
            <Pressable onPress={() => setModal(true)} className=''>
              <View className=' items-center justify-center gap-[5px] h-[100px]'>
              <Text>Check full freshness report!</Text>
              <ReadNow/>
            </View>
            </Pressable>

            {/* Connect to Bluetooth button */}
            <Pressable className='' onPress={ startScan } disabled={scanning}>
              <View className=' items-center justify-center gap-[5px] h-[60px]'>
              <Text className='border px-[55px] p-[10px] rounded-[10px] bg-lightgreenbg text-darkgreentext border-darkgreentext'>{ message }</Text>
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
            <CardModal logo={ <MaterialCommunityIcons name="fire" size={24} color="black"/> } Title={`Gas`} sensorModel={`BME680`} currentReading={`VOC Index: 192`} setTab={ setTab }/>
          </View>
        </BlurView>
      </Modal>
      }
      {tab == `Humidity` && 
      <Modal transparent={true} animationType='fade'>
        <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
          <View className=' flex-1 justify-center items-center'>
            <CardModal Title={`Humidity`} sensorModel={`SHT31`} currentReading={`Humidity: 61.8`} setTab={ setTab } logo={ <Entypo name="water" size={24} color="black"/> }/>
          </View>
        </BlurView>
      </Modal>
      }
      {tab == `Temperature` && 
      <Modal transparent={true} animationType='fade'>
        <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
          <View className=' flex-1 justify-center items-center'>
            <CardModal logo={ <FontAwesome6 name="temperature-half" size={24} color="black"/> } Title={`Temperature`} sensorModel={`SHT31`} currentReading={`Temperature: 27.2`} setTab={ setTab } />
          </View>
        </BlurView>
      </Modal>
      }
      {tab == `Carbon Dioxide` && 
      <Modal transparent={true} animationType='fade'>
        <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
          <View className=' flex-1 justify-center items-center'>
            <CardModal logo={ <Entypo name="air" size={24} color="black" /> } Title={`Carbon Dioxide`} sensorModel={`NDIR CO₂`} currentReading={`Carbon Dioxide: 752`} setTab={ setTab }/>
          </View>
        </BlurView>
      </Modal>
      }
        
      </>
    );
  }

  function Statistics(){

    const data=[ {value:600}, {value:200}, {value:290}, {value:500}, {value: 500}, {value: 100}, {value: 400} , {value: 100} , {value: 400} , {value: 300}  ]

    return(
    <>
      <StatisticScreen />
    </>
    );
  }

  function Settings(){

    const [info, setInfo] = useState('Default');
    
    let content;

    if (info == 'terms') content = infoData[0].terms;
    else if (info == 'privacy') content = infoData[1].privacy;
    else if (info == 'about') content = infoData[2].about;

    return(
    <>
      <View className='items-center gap-[20px]'>
        <View>
          <Text className='text-[15px] p-[5px]'>Statistics</Text>
          <SettingsScreen/>
        </View>
        <View>
          <Text className='text-[15px] p-[5px]'>Privacy</Text>
          <Informational setInfo={ setInfo }/>
        </View>
      </View>

      {info == 'terms' && 
      <Modal transparent={ true } animationType='fade'>
        <BlurView className='flex-1 ' intensity={ 360 } tint='extraLight'>
          <View className=' flex-1 justify-center items-center'>
            <View>  
              <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
          </View>
        </BlurView>
      </Modal>}

      {info == 'privacy' &&
      <Modal transparent={ true } animationType='fade'>
        <BlurView className='flex-1 ' intensity={ 360 } tint='extraLight'>
          <View className=' flex-1 justify-center items-center'>
            <View>  
              <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
          </View>
        </BlurView>
      </Modal>}

      {info == 'about' && 
      <Modal transparent={ true } animationType='fade'>
        <BlurView className='flex-1 ' intensity={ 360 } tint='extraLight'>
          <View className=' flex-1 justify-center items-center'>
            <View>  
              <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
          </View>
        </BlurView>
      </Modal>}
      
    </>
    );
  }

  function Screen(){
   
    const [activeTab, setActiveTab] = useState('Home');
    const insets = useSafeAreaInsets();
    const { message, scanning, temperature, humidity, startScan } = bluetoothManager;

    return (
      <View
        style={{
          flex: 1,
          paddingTop: insets.top,
          paddingBottom: insets.bottom,
          paddingLeft: insets.left,
          paddingRight: insets.right,
          }}  
        className="bg-white"
        >
          <View className=' gap-[5px]'>
            <View className=''>
              <Greeting/>
            </View>
            <View className=' items-center p-[5px]'>
              <CustomTabs activeTab={ activeTab } setActiveTab={ setActiveTab }/>
            </View>
          </View>
          <View className=' flex-1'>
            { activeTab == "Statistics" && <Statistics/>}
            { activeTab == "Home" && <HomeScreen/>}
            { activeTab == "Settings" && <Settings />}
          </View>

      </View>
    );
  }

  export default function App() {
    return (
      <>
      <SafeAreaProvider>
        <CheckedProvider>
          <Screen/>
        </CheckedProvider>
      </SafeAreaProvider>
      </>
    );
  }
