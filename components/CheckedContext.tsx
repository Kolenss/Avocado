import React, { createContext, useContext, useState } from "react";

type SensorType = "Gas" | "Humidity" | "Temperature" | "CarbonDioxide";

type CheckedContextType = {
  checked: Record<SensorType, boolean>;
  setChecked: React.Dispatch<
    React.SetStateAction<Record<SensorType, boolean>>
  >;
};
const CheckedContext = createContext<CheckedContextType | null>(null);

export const CheckedProvider = ({ children }: { children: React.ReactNode }) => {
  const [checked, setChecked] = useState<Record<SensorType, boolean>>({
    Gas: true,
    Humidity: true,
    Temperature: true,
    CarbonDioxide: true,
  });

  return (
    <CheckedContext.Provider value={{ checked, setChecked }}>
      {children}
    </CheckedContext.Provider>
  );
};

export const useChecked = () => {
  const context = useContext(CheckedContext);
  if (!context) throw new Error("useChecked must be used inside CheckedProvider");
  return context;
};
