import { View, Text } from "react-native";
import greeting from 'assets/Greetings.json'

export default function Greeting(){
    const randomNum = Math.floor(Math.random() * 10 )
    return(
        <>
            <View className="  px-[10px] h-[60px] p-[5px] gap-[5px]">
                <Text className="text-darkgreentext text-[20px]">How are you Kolens!</Text>
                <Text className="text-avocadoText text-[14px]"> { greeting[randomNum].greeting } </Text>
            </View>
        </>
    );
}