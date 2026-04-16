import { ScrollView, View, Text } from "react-native";
import CustomText from "./CustomLabel";
import { useChecked } from "./CheckedContext";
import { useBluetooth } from "routes/bluetoothScan";
import { useStatistics } from "./StatisticsContext";

interface DataPoint {
  value: number;
  timestamp: Date;
}

export default function StatisticScreen(){

  const {
    temperature,
    humidity,
    pressure,
    gasResistance,
  } = useBluetooth();

  const { checked } = useChecked();
  const { tempData, humData, gasData, pressureData, co2Data } = useStatistics();

  const getDataForSensor = (sensor: string) => {
    switch(sensor) {
      case "Temperature": return tempData;
      case "Humidity": return humData;
      case "Gas": return gasData;
      case "Pressure": return pressureData;
      case "CarbonDioxide": return co2Data;
      default: return [];
    }
  }

  const calculateChange = (data: DataPoint[], index: number) => {
    if (index === 0) return null;
    const current = data[index].value;
    const previous = data[index - 1].value;
    const change = current - previous;
    const percentChange = previous !== 0 ? (change / previous) * 100 : 0;
    return { change, percentChange };
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: false 
    });
  }
  
      return(
      <>
        <ScrollView>
          {!temperature && !humidity && !pressure && !gasResistance ? (
            <View className="flex-1 items-center justify-center p-[40px]">
              <Text className="text-[18px] text-center text-gray-600 mb-[10px]">
                📡 No Device Connected
              </Text>
              <Text className="text-[14px] text-center text-gray-500">
                Please connect to ESP32 first to view sensor statistics
              </Text>
            </View>
          ) : (
            Object.entries(checked).map(([sensor, value]) => {
              const data = getDataForSensor(sensor);
              return value && <View key={ sensor } className="mb-[20px]">
                <CustomText label={`${ sensor }`}></CustomText>
                
                {/* Time-series data table */}
                <View className="bg-white mx-[10px] rounded-[10px] p-[10px] mt-[10px]">
                  <Text className="text-[14px] font-bold text-darkgreentext mb-[8px]">Reading History</Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={true}>
                    <View>
                      {/* Table Header */}
                      <View className="flex-row border-b border-gray-300 pb-[5px] mb-[5px]">
                        <Text className="w-[60px] text-[11px] font-semibold text-gray-700">#</Text>
                        <Text className="w-[90px] text-[11px] font-semibold text-gray-700">Time</Text>
                        <Text className="w-[80px] text-[11px] font-semibold text-gray-700">Value</Text>
                        <Text className="w-[80px] text-[11px] font-semibold text-gray-700">Change</Text>
                        <Text className="w-[70px] text-[11px] font-semibold text-gray-700">%</Text>
                      </View>
                      
                      {/* Table Rows */}
                      {data.map((point, index) => {
                        const changeData = calculateChange(data, index);
                        const isIncrease = changeData && changeData.change > 0;
                        const isDecrease = changeData && changeData.change < 0;
                        
                        return (
                          <View key={index} className="flex-row py-[6px] border-b border-gray-100">
                            <Text className="w-[60px] text-[11px] text-gray-600">{index + 1}</Text>
                            <Text className="w-[90px] text-[11px] text-gray-800">{formatTime(point.timestamp)}</Text>
                            <Text className="w-[80px] text-[12px] font-semibold text-darkgreentext">{point.value.toFixed(2)}</Text>
                            <Text className={`w-[80px] text-[11px] font-semibold ${isIncrease ? 'text-green-600' : isDecrease ? 'text-red-600' : 'text-gray-500'}`}>
                              {changeData ? `${isIncrease ? '▲' : isDecrease ? '▼' : '—'} ${Math.abs(changeData.change).toFixed(2)}` : '—'}
                            </Text>
                            <Text className={`w-[70px] text-[11px] font-semibold ${isIncrease ? 'text-green-600' : isDecrease ? 'text-red-600' : 'text-gray-500'}`}>
                              {changeData ? `${changeData.percentChange > 0 ? '+' : ''}${changeData.percentChange.toFixed(1)}%` : '—'}
                            </Text>
                          </View>
                        );
                      })}
                    </View>
                  </ScrollView>
                  
                  {data.length === 0 && (
                    <Text className="text-[12px] text-gray-500 text-center py-[10px]">No data available yet</Text>
                  )}
                </View>
              </View>
            })
          )}
        </ScrollView>
      </>
      );
}
