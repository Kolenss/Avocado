import { ScrollView, View, Text } from "react-native";
import Statschart from "./Graph";
import CustomText from "./CustomLabel";
import { useChecked } from "./CheckedContext";
import useBluetoothScan from "routes/bluetoothScan";



export default function StatisticScreen(){

  const {
    message,
    scanning,
    temperature,
    humidity,
    startScan
  } = useBluetoothScan();

  const { checked } = useChecked();
    
    const data=[ {value: { temperature } }, {value: { temperature }}, {value: { temperature }}, {value: { temperature }}, {value:  { temperature }}, {value:  { temperature }}, {value:  { temperature }} , {value:  { temperature }} , {value:  { temperature }} , {value:  { temperature }}  ]
    const data2=[ {value:400}, {value:250}, {value:350}, {value:320}, {value: 280}, {value: 190}, {value: 480} , {value: 40} , {value: 555} , {value: 300}  ]
    
      return(
      <>
        <ScrollView>
          {Object.entries(checked).map(([sensor, value]) => (
            value && <View key={ sensor }>
              <CustomText label={`${ sensor }`}></CustomText>
              <Statschart data={data} className="" data2={ data2 }/>
            </View>
          ))}
        </ScrollView>
      </>
      );
}
