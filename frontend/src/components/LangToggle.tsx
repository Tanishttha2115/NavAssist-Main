import React from "react";
import { motion } from "framer-motion";
import { Languages } from "lucide-react";
import { useLang } from "@/contexts/LangContext";

const LangToggle: React.FC = () => {
  const { t, toggleLang } = useLang();

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={toggleLang}
      className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-secondary border border-border text-xs font-semibold text-foreground"
      aria-label="Switch language"
    >
      <Languages className="w-4 h-4" />
      {t.langToggle}
    </motion.button>
  );
};

export default LangToggle;
