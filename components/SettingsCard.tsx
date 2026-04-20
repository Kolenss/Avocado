import { View, Text } from "react-native";
import { RadioButton } from "react-native-paper";
import { useChecked } from "./CheckedContext";


type SensorType = 'Gas' | 'Humidity' | 'Temperature' | 'CarbonDioxide'
  

export default function SettingsCard( {sensorType, className} : { sensorType: SensorType; className?: string; } ){
    
    const { checked, setChecked } = useChecked();
    
    const toggle = () => {
        setChecked((prev) => ({
            ...prev, [sensorType] : !prev[sensorType]
        }))
    }

    return(
        <>
            <View className={` h-[48px] w-[300px] flex flex-row items-center rounded-[10px] p-[5px] g-[5px] bg-lightgreenbg m-[5px] ${ className }`}>
                <RadioButton value={ sensorType } onPress={ toggle } status={ checked[sensorType] ? "checked" : "unchecked"}/>
                <Text>{ sensorType }</Text>
            </View>
        </>
    );
}