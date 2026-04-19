import React from "react";
import { motion } from "framer-motion";
import { Mic, MicOff } from "lucide-react";
import { useLang } from "@/contexts/LangContext";

interface Props {
  listening: boolean;
  onPress: () => void;
}

const MicButton: React.FC<Props> = ({ listening, onPress }) => {
  const { t } = useLang();

  return (
    <div className="flex flex-col items-center gap-2">
      <motion.button
        whileTap={{ scale: 0.88 }}
        onClick={onPress}
        className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all ${
          listening ? "bg-primary mic-glow-active" : "bg-primary mic-glow"
        }`}
        aria-label={listening ? t.stopListening : t.startVoice}
        role="button"
      >
        {listening && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-primary"
            animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
            transition={{ duration: 1.2, repeat: Infinity }}
          />
        )}
        {listening ? (
          <MicOff className="w-10 h-10 text-primary-foreground" />
        ) : (
          <Mic className="w-10 h-10 text-primary-foreground" />
        )}
      </motion.button>
      <p className="text-sm font-medium text-muted-foreground">
        {listening ? t.listeningLabel : t.pressToSpeak}
      </p>
    </div>
  );
};

export default MicButton;
