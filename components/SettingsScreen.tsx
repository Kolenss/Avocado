import { View, Modal, Text } from "react-native";
import Informational from "./Informational";
import { useState } from "react";
import infoData from '../assets/Informational.json';
import InfoModal from "./InformationalModal";
import SettingsScreen from "./Settings";


export default function Privacy(){

    const [info, setInfo] = useState('Default');
    
    let content;

    if (info == 'terms') content = infoData.find(item => item.terms)?.terms;
    else if (info == 'privacy') content = infoData.find(item => item.privacy)?.privacy;
    else if (info == 'about') content = infoData.find(item => item.about)?.about;


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
        <View style={{ flex: 1, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
            <View className=' flex-1 justify-center items-center'>
            <View>  
                <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
            </View>
        </View>
        </Modal>}

        {info == 'privacy' &&
        <Modal transparent={ true } animationType='fade'>
        <View style={{ flex: 1, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
            <View className=' flex-1 justify-center items-center'>
            <View>  
                <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
            </View>
        </View>
        </Modal>}

        {info == 'about' && 
        <Modal transparent={ true } animationType='fade'>
        <View style={{ flex: 1, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
            <View className=' flex-1 justify-center items-center'>
            <View>  
                <InfoModal content={ content } setInfo={ setInfo } info={ info } ></InfoModal>
            </View>
            </View>
        </View>
        </Modal>}
              
    </>)
}