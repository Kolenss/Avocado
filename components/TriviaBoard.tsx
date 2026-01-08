import { View, Text, ImageBackground, Dimensions } from "react-native";
import { Image } from "react-native";
import data from 'assets/AvocadoTrivias.json'

export default function TriviaBoard(){
    const randomNum = Math.floor(Math.random() * 10);
    const randomimage = Math.floor(Math.random() * 1);

    const { height, width } = Dimensions.get("window")

    const images = [
        require("../assets/high5.gif"),
    ];

    return(
        <>
            <View className="h-[191px] w-[332px] flex flex-row justify-center items-center rounded-[40px]">
                <ImageBackground source={require('../assets/Trivia_Background.png')} resizeMode="contain" className=" flex flex-row h-[191px] w-[332px] rounded-[50px]">
                    <View className=" w-1/2 h-full flex flex-col">
                        <View className="h-1/5 justify-center items-center">
                            <Text className="text-[17px] text-white">Trivia</Text>
                        </View>
                        <View className="h-3/5 justify-center items-center px-[10px]">
                            <Text className="text-[18px] text-white text-center">{ data[randomNum].trivia }</Text>
                        </View>
                        <View className="h-1/5 items-center">
                            <Text className="text-[12px] text-white">Did you know?</Text>
                        </View>
                    </View>
                    <View className="w-1/2 h-full justify-center items-center">
                        <Image source={require("../assets/high5.gif")} className="w-[140px] h-[120px] rounded-[40px]" resizeMode="contain"></Image>
                    </View>
                </ImageBackground>
                
                {/* <View className="flex flex-col gap-[5px]">
                    <View className="items-center">
                        <Text className="text-2xl text-darkgreentext">Trivia</Text>
                    </View>
                    <View className="flex flex-row border items-center">
                        <View className=" items-end justify-center">
                            <Image source={ images[randomimage] } className="w-[200px] h-[200px]"></Image>
                        </View>
                        <View className="border w-[185px] h-[155px] flex items-center justify-center bg-lightgreenbg rounded-[15px]">
                            <Text className="text-center">{ data[randomNum].trivia }</Text>
                        </View>
                    </View>
                    
                </View> */}
                
            </View>
        </>
    );
}