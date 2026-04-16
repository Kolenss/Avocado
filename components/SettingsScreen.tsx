import { View, Modal, Text } from "react-native";
<<<<<<< HEAD
=======
import { BlurView } from "expo-blur";
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
import Informational from "./Informational";
import { useState } from "react";
import infoData from '../assets/Informational.json';
import InfoModal from "./InformationalModal";
import SettingsScreen from "./Settings";


export default function Privacy(){

    const [info, setInfo] = useState('Default');
    
    let content;

<<<<<<< HEAD
    if (info == 'terms') content = infoData.find(item => item.terms)?.terms;
    else if (info == 'privacy') content = infoData.find(item => item.privacy)?.privacy;
    else if (info == 'about') content = infoData.find(item => item.about)?.about;
=======
    if (info == 'terms') content = infoData[0].terms;
    else if (info == 'privacy') content = infoData[1].privacy;
    else if (info == 'about') content = infoData[2].about;
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3


    return(<>
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
<<<<<<< HEAD
        <View style={{ flex: 1, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
=======
        <BlurView className='flex-1 ' intensity={ 360 } tint='extraLight'>
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
            <View className=' flex-1 justify-center items-center'>
            <View>  
                <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
            </View>
<<<<<<< HEAD
        </View>
=======
        </BlurView>
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
        </Modal>}

        {info == 'privacy' &&
        <Modal transparent={ true } animationType='fade'>
<<<<<<< HEAD
        <View style={{ flex: 1, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
=======
        <BlurView className='flex-1 ' intensity={ 360 } tint='extraLight'>
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
            <View className=' flex-1 justify-center items-center'>
            <View>  
                <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
            </View>
<<<<<<< HEAD
        </View>
=======
        </BlurView>
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
        </Modal>}

        {info == 'about' && 
        <Modal transparent={ true } animationType='fade'>
<<<<<<< HEAD
        <View style={{ flex: 1, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
=======
        <BlurView className='flex-1 ' intensity={ 360 } tint='extraLight'>
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
            <View className=' flex-1 justify-center items-center'>
            <View>  
                <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
            </View>
<<<<<<< HEAD
        </View>
=======
        </BlurView>
>>>>>>> 288643606676c2e7143f21b9052331a9949e8ff3
        </Modal>}
              
    </>)
}