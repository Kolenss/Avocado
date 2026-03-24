import React, { createContext, useContext, useState, useEffect } from "react";
import { useBluetooth } from "routes/bluetoothScan";

interface DataPoint {
  value: number;
  timestamp: Date;
}

interface StatisticsContextType {
  tempData: DataPoint[];
  humData: DataPoint[];
  gasData: DataPoint[];
  pressureData: DataPoint[];
}

const StatisticsContext = createContext<StatisticsContextType | null>(null);

export const StatisticsProvider = ({ children }: { children: React.ReactNode }) => {
  const { temperature, humidity, pressure, gasResistance } = useBluetooth();
  
  const [tempData, setTempData] = useState<DataPoint[]>([]);
  const [humData, setHumData] = useState<DataPoint[]>([]);
  const [gasData, setGasData] = useState<DataPoint[]>([]);
  const [pressureData, setPressureData] = useState<DataPoint[]>([]);

  useEffect(() => {
    if (temperature) {
      setTempData(prev => {
        if (prev.length >= 20) {
          return [{ value: parseFloat(temperature), timestamp: new Date() }];
        }
        return [...prev, { value: parseFloat(temperature), timestamp: new Date() }];
      });
    }
  }, [temperature]);

  useEffect(() => {
    if (humidity) {
      setHumData(prev => {
        if (prev.length >= 20) {
          return [{ value: parseFloat(humidity), timestamp: new Date() }];
        }
        return [...prev, { value: parseFloat(humidity), timestamp: new Date() }];
      });
    }
  }, [humidity]);

  useEffect(() => {
    if (pressure) {
      setPressureData(prev => {
        if (prev.length >= 20) {
          return [{ value: parseFloat(pressure), timestamp: new Date() }];
        }
        return [...prev, { value: parseFloat(pressure), timestamp: new Date() }];
      });
    }
  }, [pressure]);

  useEffect(() => {
    if (gasResistance) {
      setGasData(prev => {
        if (prev.length >= 20) {
          return [{ value: parseFloat(gasResistance), timestamp: new Date() }];
        }
        return [...prev, { value: parseFloat(gasResistance), timestamp: new Date() }];
      });
    }
  }, [gasResistance]);

  return (
    <StatisticsContext.Provider value={{ tempData, humData, gasData, pressureData }}>
      {children}
    </StatisticsContext.Provider>
  );
};

export const useStatistics = () => {
  const context = useContext(StatisticsContext);
  if (!context) throw new Error("useStatistics must be used inside StatisticsProvider");
  return context;
};
