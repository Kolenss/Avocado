import React from "react";
import { View, Text, Pressable } from "react-native";
import ProgressBar from "./ProgressBar";



type CardProps = {
    logo: React.ReactNode;
    title: string;
    progressNum?: any;
    className?: string;
    setTab: any
};

export default function Card({ logo, title, progressNum, className, setTab }: CardProps){
    return(
        <>
        <Pressable onPress={ () => setTab(`${title}`)}>
            <View className=" flex flex-row w-[357px] rounded-[6px] bg-lightgreenbg border border-gray-400">
                <View className={` h-[48px] w-[160px] flex flex-row items-center rounded-[6px] p-[5px] gap-[5px] ${ className }`}>
                    { logo } 
                    <Text>{ title }</Text>
                </View>
                <View className="justify-center">
                    <ProgressBar progress={ progressNum } />
                    <View className="absolute justify-center items-center inset-0">
                        <Text className="text-darkgreentext">
                            { (progressNum * 100).toFixed(1) }
                        </Text>
                    </View>
                </View>
            </View>
        </Pressable>

        
        </>
    );
}