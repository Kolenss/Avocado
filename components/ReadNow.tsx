import { Text, View } from "react-native";

export default function ReadNow(){
    return(
        <>
            <View className=" w-[285px] h-[32px] justify-center items-center bg-white rounded-[10px]">
                <Text className="text-newDarkText text-[22px]">
                    Read Now
                </Text>
            </View>
        </>
    );
}