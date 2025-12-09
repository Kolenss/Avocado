import { ScrollView, View, Text } from "react-native";
import Statschart from "./Graph";

export default function CustomText({ label, className}: any){    
      return(
      <>
          <View className={`px-[5px]`}>
            <Text className={`text-darkgreentext text-xl`}>{ label }</Text>
          </View>
      </>
      );
}