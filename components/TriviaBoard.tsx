import { View, Text } from "react-native";
import { Image } from "react-native";
import data from 'assets/AvocadoTrivias.json'

export default function TriviaBoard(){
    const randomNum = Math.floor(Math.random() * 10);
    const randomimage = Math.floor(Math.random() * 8);

    const images = [
        require("../assets/board.png"),
        require("../assets/happy.png"),
        require("../assets/hi.png"),
        require("../assets/idea.png"),
        require("../assets/meditate.png"),
        require("../assets/muscle.png"),
        require("../assets/strong.png"),
        require("../assets/think.png"),
    ];
    return(
        <>
            <View className="h-[240px] w-[365px] flex flex-row justify-center items-center">
                <View className="flex flex-col gap-[5px]">
                    <View className="items-center">
                        <Text className="text-2xl text-darkgreentext">Did you know?</Text>
                    </View>
                    <View className="flex flex-row">
                        <View className=" items-end justify-center">
                            <Image source={ images[randomimage] } className="scale-x-[-1]"></Image>
                        </View>
                        <View className="border w-[185px] h-[155px] flex items-center justify-center bg-lightgreenbg rounded-[15px]">
                            <Text className="text-center">{ data[randomNum].trivia }</Text>
                        </View>
                    </View>
                    
                </View>
                
            </View>
        </>
    );
}