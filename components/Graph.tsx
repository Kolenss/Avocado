import { View, Dimensions } from "react-native";
import { LineChart } from "react-native-gifted-charts";

interface StatsChartProps {
  className?: string;
  data: Array<{ value: number }>;
  data2?: Array<{ value: number }>;
}

export default function Statschart({ className, data, data2 }: StatsChartProps) {
  const screenWidth = Dimensions.get("window").width;
  const chartPadding = 20; // padding inside the chart container

  const spacing =
    data && data.length > 1
      ? Math.max(8, (screenWidth - chartPadding * 2) / (data.length - 1))
      : 10;

  const maxVal =
    data && data.length > 0
      ? Math.max(...data.map(d => d.value)) * 1.05 // small headroom
      : 100;

  return (
    <View
      className=''
      style={{ backgroundColor: "white", paddingVertical: 20 }}
    >
      <LineChart
        thickness={2}
        color="#64a12d"
        maxValue={maxVal}
        noOfSections={5}
        areaChart
        yAxisTextStyle={{ color: "black" }}
        data={data}
        curved
        startFillColor="#64a12d"
        endFillColor="#64a12d"
        startOpacity={0.4}
        endOpacity={0.4}
        spacing={spacing}     
        initialSpacing={10}
        backgroundColor="white"
        rulesColor="gray"
        rulesType="solid"
        yAxisColor="black"
        xAxisColor="black"
        dataPointsHeight={6}   
        dataPointsWidth={6}
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
