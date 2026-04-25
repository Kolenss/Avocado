import { Pressable, Text, View } from "react-native";


export default function CardModal({setTab, Title, sensorModel, sensorModel2, currentReading, currentReading2, logo}: any){
    return(
        <Pressable onPress={() => setTab(`Default`)}>
            <View className="border border-darkgreentext w-[270px] bg-lightgreenbg px-[15px] p-[10px] rounded-[5px]">
                <View className="gap-[5px]">
                    <View className="items-center">
                        <Text className="text-[20px] text-darkgreentext">
                            { logo }{ Title } Sensor
                        </Text>
                    </View>
                    <View>
                        <Text className="text-[15px] font-bold text-darkgreentext">
                            Model: { sensorModel }
                        </Text>
                    </View>
                    <View>
                        <Text className="px-[10px]">
                            Current Reading: {`\n`}
                            { currentReading }
                        </Text>
                    </View>
                </View>
            </View>
        </Pressable>
    );
}