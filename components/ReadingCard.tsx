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
            <View className="flex flex-row w-[340px] rounded-[6px] border-black-400 items-center justify-center gap-[4px] p-[3px]">
                <View className={` h-[48px] w-[48px] flex flex-row items-center rounded-[6px] p-[4px] gap-[4px] ${ className }`}>
                    <Image source={ logo } resizeMode='contain' style={{ width: 36, height: 36 }}></Image>
                </View>
                <View className="justify-center ">
                    <ProgressBar progress={ progressNum } />
                    <View className="absolute justify-between items-center inset-0 flex flex-row px-[10px]">
                        <Text className="text-[11px] text-black">{ title }</Text>
                        <Text className="text-[14px] text-black">{ (progressNum * 100).toFixed(1) }</Text>
                    </View>
                </View>
            </View>
        </Pressable>
        </>
    );
}
