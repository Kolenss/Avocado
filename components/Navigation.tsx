import React, { useState } from "react";
import { View, Text, Pressable } from "react-native";


export default function CustomTabs({ activeTab, setActiveTab}: any) {  

  return (
    <View className="flex-row bg-lightgreenbg rounded-[50px] w-[340px] justify-between p-[5px]">
      <Pressable onPress={() => setActiveTab("Statistics")}   
      className={`${activeTab === "Statistics" ? `text-black bg-white rounded-[50px]` : `text-avocadoText bg-transparent`} p-[5px] w-[100px] justify-center items-center`}>
        <Text className={`${ activeTab === "Statistics" ? `text-black` : `text-avocadoText`} text-[11px]`}>Statistics</Text>
      </Pressable>
      <Pressable onPress={() => setActiveTab("Home")} className={`${activeTab === "Home" ? `text-black bg-white rounded-[50px]` : `text-avocadoText bg-transparent`} p-[5px] w-[100px] justify-center items-center`}>
        <Text className={`${ activeTab === "Home" ? `text-black` : `text-avocadoText`} text-[11px]`}>Home</Text>
      </Pressable>
      <Pressable onPress={() => setActiveTab("Settings")} className={`${activeTab === "Settings" ? `text-black bg-white rounded-[50px]` : `text-avocadoText bg-transparent`} p-[5px] w-[100px] justify-center items-center`}>
        <Text className={`${ activeTab === "Settings" ? `text-black` : `text-avocadoText`} text-[11px]`}>Settings</Text>
      </Pressable>
    </View>
  );
}
