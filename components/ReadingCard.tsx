import React from "react";
import { View, Text, Pressable, ImageSourcePropType, Image } from "react-native";
import ProgressBar from "./ProgressBar";



type CardProps = {
    logo: ImageSourcePropType;
    title: string;
    progressNum?: any;
    className?: string;
    setTab: any
};

export default function Card({ logo, title, progressNum, className, setTab }: CardProps){
    return(
        <>
        <Pressable onPress={ () => setTab(`${title}`)}>
            <View className="flex flex-row w-[357px] rounded-[6px] border-black-400 items-center justify-center gap-[5px] p-[5px]">
                <View className={` h-[62px] w-1/5 flex flex-row items-center rounded-[6px] p-[5px] gap-[5px] ${ className }`}>
                    <Image source={ logo } resizeMode='contain'></Image>
                </View>
                <View className="justify-center ">
                    <ProgressBar progress={ progressNum } />
                    <View className="absolute justify-between items-center inset-0 flex flex-row px-[10px]">
                        <Text className="text-[12px] text-black">{ title }</Text>
                        <Text className="text-[17px] text-black">{ (progressNum * 100).toFixed(1) }</Text>
                    </View>
                </View>
            </View>
        </Pressable>

        
        </>
    );
}