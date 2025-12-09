import { View, Text } from "react-native";
import SettingsCard from "../components/SettingsCard";


export default function SettingsScreen(){
    return(
        <>
            <View>
                <SettingsCard sensorType="Gas"/>
                <SettingsCard sensorType="Humidity"/>
                <SettingsCard sensorType="Temperature"/>
                <SettingsCard sensorType="CarbonDioxide"/>
                <Text></Text>
            </View>
            
        </>
    );
}