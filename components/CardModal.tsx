import { Pressable, Text, View, Image, ImageSourcePropType } from "react-native";

export default function CardModal({ setTab, Title, sensorModel, currentReading, logo }: { setTab: any, Title: string, sensorModel: string, currentReading: string, logo: ImageSourcePropType }) {
  return (
    <View className="w-[300px] rounded-[20px] bg-lightgreenbg overflow-hidden" style={{ shadowColor: '#384728', shadowOpacity: 0.15, shadowRadius: 12, elevation: 8 }}>
      
      {/* Header */}
      <View className="bg-newBackground px-[20px] py-[18px] items-center gap-[6px]">
        <View className="bg-white/20 rounded-full p-[12px]">
          <Image source={logo} style={{ width: 36, height: 36 }} resizeMode="contain" />
        </View>
        <Text className="text-white text-[20px] font-bold mt-[4px]">{Title}</Text>
        <Text className="text-white/80 text-[12px]">Sensor: {sensorModel}</Text>
      </View>

      {/* Reading */}
      <View className="px-[20px] py-[18px] gap-[12px]">
        <View className="bg-white rounded-[12px] px-[16px] py-[14px]">
          <Text className="text-darkgreentext text-[12px] font-semibold mb-[2px]">CURRENT READING</Text>
          <Text className="text-newDarkText text-[22px] font-bold">{currentReading}</Text>
        </View>

        <Pressable onPress={() => setTab('Default')}>
          <View className="bg-darkgreentext py-[12px] rounded-[12px] items-center">
            <Text className="text-white font-semibold text-[15px]">Close</Text>
          </View>
        </Pressable>
      </View>

    </View>
  );
}
