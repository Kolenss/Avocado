import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
import { View, ImageBackground, Dimensions } from 'react-native';
import Greeting from 'components/Greetings';
import CustomTabs from 'components/Navigation';
import './global.css';
import { useState } from 'react';
import StatisticScreen from 'components/Statistics';
import { CheckedProvider } from 'components/CheckedContext';
import { StatisticsProvider } from 'components/StatisticsContext';
import Home from 'components/HomeScreen';
import Privacy from 'components/SettingsScreen';

function Screen() {
  const [activeTab, setActiveTab] = useState('Home');
  const insets = useSafeAreaInsets();
  const { height, width } = Dimensions.get('window');

  return (
    <View
      style={{
        flex: 1,
        paddingTop: insets.top,
        paddingBottom: insets.bottom,
        paddingLeft: insets.left,
        paddingRight: insets.right,
      }}
    >
      <ImageBackground source={require("./assets/Home_Screen.png")} resizeMode='cover' style={{ width, height }}>
        <View className='gap-[5px]'>
          <Greeting />
          <View className='items-center p-[5px]'>
            <CustomTabs activeTab={activeTab} setActiveTab={setActiveTab} />
          </View>
        </View>
        <View className='flex-1 items-center'>
          {activeTab === "Statistics" && <StatisticScreen />}
          {activeTab === "Home" && <Home />}
          {activeTab === "Settings" && <Privacy />}
        </View>
      </ImageBackground>
    </View>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <CheckedProvider>
        <StatisticsProvider>
          <Screen />
        </StatisticsProvider>
      </CheckedProvider>
    </SafeAreaProvider>
  );
}
