import { View, Text } from "react-native";
import greeting from 'assets/Greetings.json'

export default function Greeting(){
    const randomNum = Math.floor(Math.random() * 10 )
    return(
        <>
            <View className="px-[15px] p-[5px] gap-[5px] ">
                <Text className="text-white text-[36px]">Hello</Text>
                <Text className="text-white text-[14px]"> { greeting[randomNum].greeting } </Text>
            </View>
        </>
    );
}