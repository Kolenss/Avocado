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

export default function TestCard({ logo, title, progressNum, className, setTab }: CardProps){
    return(
        <>
        <Pressable onPress={ () => setTab(`${title}`)}>
            <View className=" flex flex-row w-[357px] rounded-[6px] bg-lightgreenbg border border-gray-400">
                <View className={`border h-[62px] w-[63px] items-center rounded-full p-[5px] gap-[5px] justify-center ${ className }`}>
                    { logo } 
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