import { View, Pressable } from 'react-native'
import InformationalCard from './InformationalCard';
import EvilIcons from '@expo/vector-icons/EvilIcons';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import Ionicons from '@expo/vector-icons/Ionicons';
import React, { useState } from 'react';

export default function Informational({setInfo} : {setInfo: React.Dispatch<React.SetStateAction<string>>}){
    
    return(
        <>
            <View>
                <Pressable onPress={() => setInfo('terms')}>
                    <InformationalCard information={ `Terms and Conditions` } logo={ <EvilIcons name="lock" size={24} color="black" /> }/>
                </Pressable>
                <Pressable onPress={() => setInfo('privacy')}>
                    <InformationalCard information={ `Privacy and Policy` } logo={ <MaterialIcons name="privacy-tip" size={24} color="black" /> }/>
                </Pressable>
                <Pressable onPress={() => setInfo('about')}>
                    <InformationalCard information={ `About App` } logo={ <Ionicons name="information-circle-outline" size={24} color="black" /> }/>
                </Pressable>
            </View>
        </>
    );
}
