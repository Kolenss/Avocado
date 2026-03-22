import { Pressable, Text, View, Image, ImageBackground } from "react-native";
import sensor from '../assets/Sensors.png'

export default function CardModal({setTab, Title, sensorModel, sensorModel2, currentReading, currentReading2, logo}: any){
    return(
        <Pressable onPress={() => setTab(``)}>
            <ImageBackground source={require('../assets/Trivia_Background.png')} resizeMode="contain" className=" flex flex-row h-[191px] w-[332px] rounded-[50px]">
                <View className={` text-white w-full px-[15px] p-[20px] rounded-[5px] justify-between`}>
                    <View className="items-center flex flex-row justify-center ">
                        <Image source={ logo } className=""/>
                        <Text className="text-[30px] flex flex-auto  text-white">
                            { Title } Sensor
                        </Text>
                    </View>
                    <View className=" flex flex-row items-center text-center gap-[15px]">
                        <Image source={ sensor } style={{height: 40, width: 40}}/>
                        <Text className="text-[20px] text-white">
                            Model: { sensorModel }
                        </Text>
                    </View>
                    <View className="px-[15px]">
                        <Text className="text-[15px] text-white gap-[5px]">
                            Current Reading: {`\n`}
                            { currentReading }
                        </Text>
                    </View>
                </View>
            </ImageBackground>
        </Pressable>
    );
}