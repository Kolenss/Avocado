import React from "react";
import { View } from "react-native";
import * as Progress from "react-native-progress";

type Progress = {
    progress?: number;
}

export default function ProgressBar({ progress }: Progress) {
  return (
    <View className="items-center">
      <Progress.Bar
        progress={ progress }
        width={240}
        height={27} 
        color="#64A12D"  
        unfilledColor="#E5E7EB" 
        borderWidth={0}
        borderRadius={999}
        useNativeDriver
      />
    </View>
  );
}
