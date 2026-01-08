  import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
  import { Text, View, Pressable, Modal, Alert, PermissionsAndroid, Platform, ImageBackground, Dimensions } from 'react-native';
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
  import Home from 'components/HomeScreen';
  import { Buffer } from "buffer";
  import { useBluetooth } from 'routes/bluetoothScan';
  import Privacy from 'components/SettingsScreen';
  
  const manager = new BleManager();

  function HomeScreen(){
    return(
      <>
      <Home/>
      </>
    );
  }

  function Statistics(){

    return(
    <>
      <StatisticScreen />
    </>
    );
  }

  function Settings(){
    return(
    <>
      <Privacy/>
    </>
    );
  }

  function Screen(){
   
    const [activeTab, setActiveTab] = useState('Home');
    const insets = useSafeAreaInsets();
    const { height, width } = Dimensions.get('window')

    return (
      <View
        style={{
          flex: 1,
          paddingTop: insets.top,
          paddingBottom: insets.bottom,
          paddingLeft: insets.left,
          paddingRight: insets.right,
          }}  
        className=""
        >
          <ImageBackground source={require("./assets/Home_Screen.png")} resizeMode='cover' style={{ width: width, height: height}}>
            <View className=' gap-[5px]'>
              <View className=''>
                <Greeting/>
              </View>
              <View className=' items-center p-[5px]'>
                <CustomTabs activeTab={ activeTab } setActiveTab={ setActiveTab }/>
              </View>
          </View>
          <View className=' flex-1 items-center'>
            { activeTab == "Statistics" && <Statistics/>}
            { activeTab == "Home" && <HomeScreen/>}
            { activeTab == "Settings" && <Settings />}
          </View>
          </ImageBackground>
      
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
