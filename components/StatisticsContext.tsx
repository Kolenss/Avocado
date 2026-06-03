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
  co2Data: DataPoint[];
}

const StatisticsContext = createContext<StatisticsContextType | null>(null);

export const StatisticsProvider = ({ children }: { children: React.ReactNode }) => {
  const { temperature, humidity, pressure, gasResistance, co2 } = useBluetooth();
  
  const [tempData, setTempData] = useState<DataPoint[]>([]);
  const [humData, setHumData] = useState<DataPoint[]>([]);
  const [gasData, setGasData] = useState<DataPoint[]>([]);
  const [pressureData, setPressureData] = useState<DataPoint[]>([]);
  const [co2Data, setCo2Data] = useState<DataPoint[]>([]);

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

  useEffect(() => {
    if (co2) {
      setCo2Data(prev => {
        if (prev.length >= 20) {
          return [{ value: parseFloat(co2), timestamp: new Date() }];
        }
        return [...prev, { value: parseFloat(co2), timestamp: new Date() }];
      });
    }
  }, [co2]);

  return (
    <StatisticsContext.Provider value={{ tempData, humData, gasData, pressureData, co2Data }}>
      {children}
    </StatisticsContext.Provider>
  );
};

export const useStatistics = () => {
  const context = useContext(StatisticsContext);
  if (!context) throw new Error("useStatistics must be used inside StatisticsProvider");
  return context;
};
