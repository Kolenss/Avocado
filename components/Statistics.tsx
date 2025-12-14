import { ScrollView, View, Text } from "react-native";
import Statschart from "./Graph";
import CustomText from "./CustomLabel";
import { useChecked } from "./CheckedContext";
import { useBluetooth } from "routes/bluetoothScan";
import { useEffect, useState } from "react";



export default function StatisticScreen(){

  const {
    message,
    scanning,
    temperature,
    humidity,
    pressure,
    gasResistance,
    startScan
  } = useBluetooth();

  const { checked } = useChecked();
  const [ tempData, setTempData ] = useState<Array<{ value: number }>>([])
  const [ humData, setHumData] = useState<Array<{ value: number }>>([])
  const [ gasData, setGasData] = useState<Array<{ value: number }>>([])
  const [ pressureData, setPressureData] = useState<Array<{ value: number }>>([])

  useEffect(() => {
    if(temperature){
      setTempData(prev => {
        const updated = [...prev, {value: parseFloat(temperature)}]
      if(updated.length > 20) updated.shift()
      return updated
      })
    }
  }, [temperature]);

  useEffect(() => {
    if(humidity){
      setHumData(prev => {
        const updated = [...prev, {value: parseFloat(humidity)}]
      if(updated.length > 20) updated.shift()
      return updated
      })
    }
  }, [humidity]);
  
  useEffect(() => {
    if(pressure){
      setPressureData(prev => {
        const updated = [...prev, {value: parseFloat(pressure)}]
      if(updated.length > 20) updated.shift()
      return updated
      })
    }
  }, [pressure]);

  
  useEffect(() => {
    if(gasResistance){
      setGasData(prev => {
        const updated = [...prev, {value: parseFloat(gasResistance)}]
      if(updated.length > 20) updated.shift()
      return updated
      })
    }
  }, [gasResistance]);

  console.log(tempData)
  console.log(humData)
  console.log(gasData)
  console.log(pressureData)
  
    // const data=[ {value: 22 }, {value: 22 }, {value: 22 }, {value:  22 }, {value:  22 }, {value: 22 }, {value:   22 } , {value:  22 } , {value:  22 } , {value:   22 }  ]
    // const data2=[ {value:400}, {value:250}, {value:350}, {value:320}, {value: 280}, {value: 190}, {value: 480} , {value: 40} , {value: 555} , {value: 300}  ]
    
      return(
      <>
        <ScrollView>
          {Object.entries(checked).map(([sensor, value]) => (
            value && <View key={ sensor }>
              <CustomText label={`${ sensor }`}></CustomText>
              {/* <Statschart data={data2} ></Statschart> */}
              <Statschart data={sensor == "Temperature" ? tempData : sensor == "Humidity" ? humData : sensor == "Gas" ? gasData : sensor == "CarbonDioxide" ? pressureData : [] } className=""/>
            </View>
          ))}
        </ScrollView>
      </>
      );
}
