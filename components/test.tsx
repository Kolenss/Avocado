import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView } from "react-native";
import { fetchPrediction, PredictionResult, defaultPrediction } from "routes/prediction";

export default function TestPrediction() {
  const [temperature, setTemperature] = useState("");
  const [humidity, setHumidity] = useState("");
  const [pressure, setPressure] = useState("");
  const [gasResistance, setGasResistance] = useState("");
  const [co2, setCo2] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function runTest() {
    if (!temperature || !humidity || !pressure || !gasResistance || !co2) {
      console.warn("[TEST] Fill in all fields first");
      return;
    }
    setLoading(true);
    try {
      console.log("[TEST] Inputs:", { temperature, humidity, pressure, gasResistance, co2 });
      const prediction = await fetchPrediction(temperature, humidity, pressure, gasResistance, co2);
      console.log("[TEST] Result:", JSON.stringify(prediction, null, 2));
      setResult(prediction);
    } catch (e) {
      console.error("[TEST] Error:", e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={{ padding: 20, gap: 10 }}>
      <Text style={{ fontSize: 18, fontWeight: "bold", marginBottom: 10 }}>ML Prediction Tester</Text>

      {[
        { label: "Temperature (°C)", value: temperature, set: setTemperature },
        { label: "Humidity (%)", value: humidity, set: setHumidity },
        { label: "Pressure (hPa)", value: pressure, set: setPressure },
        { label: "Gas Resistance (kΩ)", value: gasResistance, set: setGasResistance },
        { label: "CO2 (ppm)", value: co2, set: setCo2 },
      ].map(({ label, value, set }) => (
        <View key={label} style={{ marginBottom: 8 }}>
          <Text style={{ marginBottom: 4 }}>{label}</Text>
          <TextInput
            value={value}
            onChangeText={set}
            keyboardType="numeric"
            placeholder={`Enter ${label}`}
            style={{ borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 8 }}
          />
        </View>
      ))}

      <Pressable onPress={runTest} style={{ backgroundColor: "#2d6a4f", padding: 12, borderRadius: 8, alignItems: "center" }}>
        <Text style={{ color: "white", fontWeight: "bold" }}>{loading ? "Running..." : "Run Prediction"}</Text>
      </Pressable>

      {result && (
        <View style={{ marginTop: 16, padding: 12, backgroundColor: "#f0fdf4", borderRadius: 8, gap: 6 }}>
          <Text style={{ fontWeight: "bold", fontSize: 16 }}>Result:</Text>
          <Text>Ripeness: <Text style={{ fontWeight: "bold" }}>{result.ripeness_label} (class {result.ripeness_class})</Text></Text>
          <Text>Shelf Life: <Text style={{ fontWeight: "bold" }}>{result.shelf_life_hours} hrs / {result.shelf_life_days} days</Text></Text>
          <Text>Note: {result.note}</Text>
        </View>
      )}
    </ScrollView>
  );
}
