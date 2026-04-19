import React, { useState } from "react";
import { motion } from "framer-motion";
import { Bluetooth, BluetoothOff } from "lucide-react";
import { useLang } from "@/contexts/LangContext";

const BluetoothConnect: React.FC = () => {
  const { t } = useLang();
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");

  const handleConnect = async () => {
    if (!(navigator as any).bluetooth) {
      setError(t.btNotSupported);
      return;
    }
    try {
      const device = await (navigator as any).bluetooth.requestDevice({
        acceptAllDevices: true,
      });
      if (device) setConnected(true);
    } catch {
      setError(t.btCancelled);
    }
  };

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={handleConnect}
      className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium border transition-all ${
        connected
          ? "bg-safe/15 border-safe/30 text-safe"
          : "bg-secondary border-border text-muted-foreground"
      }`}
      aria-label={t.connectStick}
    >
      {connected ? <Bluetooth className="w-4 h-4" /> : <BluetoothOff className="w-4 h-4" />}
      {connected ? t.stickConnected : t.connectStick}
      {error && <span className="text-destructive text-[10px]">({error})</span>}
    </motion.button>
  );
};

export default BluetoothConnect;
