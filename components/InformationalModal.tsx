import { Pressable, Text, View } from "react-native";


export default function InfoModal({content, setInfo, info}: any){
    return(
        <Pressable onPress={() => setInfo(`Default`)}>
            <View className="border border-darkgreentext w-[270px] bg-lightgreenbg px-[15px] p-[30px] rounded-[15px] gap-[20px]">
                {info == 'terms' &&
                    <Text className="text-[20px] text-darkgreentext">
                        Terms & Conditions
                    </Text>
                }
                {info == 'privacy' &&
                    <Text className="text-[20px] text-darkgreentext">
                        Privacy & Policy
                    </Text>
                }
                {info == 'about' &&
                    <Text className="text-[20px] text-darkgreentext">
                        About App
                    </Text>
                }
                <Text className="text-[17px] text-darkgreentext">
                    { content }
                </Text>
            </View>
        </Pressable>
    );
}