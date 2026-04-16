import React, { useState } from "react";
import { View, Text, Pressable } from "react-native";


export default function CustomTabs({ activeTab, setActiveTab}: any) {  

  return (
    <View className="flex-row bg-white rounded-[50px] w-[340px] justify-between p-[5px]">
      <Pressable onPress={() => setActiveTab("Statistics")}   
      className={`${activeTab === "Statistics" ? `bg-newBackground rounded-[50px]` : `text-avocadoText bg-transparent`} p-[5px] w-[100px] justify-center items-center`}>
        <Text className={`${ activeTab === "Statistics" ? `text-white` : `text-avocadoText`} text-[12px]`}>Statistics</Text>
      </Pressable>
      <Pressable onPress={() => setActiveTab("Home")} className={`${activeTab === "Home" ? `bg-newBackground rounded-[50px]` : `text-avocadoText bg-transparent`} p-[5px] w-[100px] justify-center items-center`}>
        <Text className={`${ activeTab === "Home" ? `text-white` : `text-avocadoText`} text-[12px]`}>Home</Text>
      </Pressable>
      <Pressable onPress={() => setActiveTab("Settings")} className={`${activeTab === "Settings" ? `bg-newBackground rounded-[50px]` : `text-avocadoText bg-transparent`} p-[5px] w-[100px] justify-center items-center`}>
        <Text className={`${ activeTab === "Settings" ? `text-white` : `text-avocadoText`} text-[12px]`}>Settings</Text>
      </Pressable>
    </View>
  );
}
