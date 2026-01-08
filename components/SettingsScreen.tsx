import { View, Modal, Text } from "react-native";
import { BlurView } from "expo-blur";
import Informational from "./Informational";
import { useState } from "react";
import infoData from '../assets/Informational.json';
import InfoModal from "./InformationalModal";
import SettingsScreen from "./Settings";


export default function Privacy(){

    const [info, setInfo] = useState('Default');
    
    let content;

    if (info == 'terms') content = infoData[0].terms;
    else if (info == 'privacy') content = infoData[1].privacy;
    else if (info == 'about') content = infoData[2].about;


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
              
    </>)
}