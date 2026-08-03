import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { WifiOff } from "lucide-react";
import { useLang } from "@/contexts/LangContext";

interface Props {
  online: boolean;
}

const OfflineBanner: React.FC<Props> = ({ online }) => {
  const { t } = useLang();

  return (
    <AnimatePresence>
      {!online && (
        <motion.div
          initial={{ y: -40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -40, opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-50 bg-warning text-warning-foreground py-2 px-4 flex items-center justify-center gap-2 text-sm font-medium"
        >
          <WifiOff className="w-4 h-4" />
          {t.offline}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default OfflineBanner;
