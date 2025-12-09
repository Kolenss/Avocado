import { View, Text } from "react-native";
import { LineChart } from "react-native-gifted-charts";

export default function Statschart({ className, data, data2 }: any) {
  

  return (
    <View className={`${className}`} style={{ backgroundColor: "white", paddingVertical: 20 }}>
      <LineChart
        thickness={4}
        color="#D1CF69"
        maxValue={600}
        noOfSections={4}
        areaChart
        yAxisTextStyle={{ color: "black" }}
        data={data}
        curved
        startFillColor={"#64a12d"}
        endFillColor={"#64a12d"}
        startOpacity={0.4}
        endOpacity={0.4}
        spacing={38}
        backgroundColor="white"
        rulesColor="gray"
        rulesType="solid"
        initialSpacing={10}
        yAxisColor="black"
        xAxisColor="black"
        dataPointsHeight={20}
        dataPointsWidth={20}
        dataPointsColor="green"
        
        data2={data2}
        dataPointsColor2="green"
        isAnimated
        animationDuration={750}
        focusEnabled
        showValuesAsDataPointsText
        showTextOnFocus
        showStripOnFocus  
        
      />
    </View>
  );
}
