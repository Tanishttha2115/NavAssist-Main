import React from "react";
import { motion } from "framer-motion";
import { Phone } from "lucide-react";
import { useTextToSpeech } from "@/hooks/useSpeech";
import { useVibration } from "@/hooks/useVibration";
import { useLang } from "@/contexts/LangContext";
import { api } from "@/lib/api";

interface Props {
  location: { lat: number; lng: number } | null;
}

const EmergencyButton: React.FC<Props> = ({ location }) => {
  const { t, speechLang } = useLang();
  const { speak } = useTextToSpeech();
  const { danger } = useVibration();

  const handleSOS = async () => {
    danger();
    speak(t.emergencyCall, speechLang);

    // Get fresh location and send to backend
    const sendWith = (lat: number, lng: number) =>
      api.sendSOS({ latitude: lat, longitude: lng }).catch(() => {});

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => sendWith(pos.coords.latitude, pos.coords.longitude),
        () => { if (location) sendWith(location.lat, location.lng); },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    } else if (location) {
      sendWith(location.lat, location.lng);
    }

    window.location.href = "tel:112";
  };

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={handleSOS}
      className="w-full py-5 rounded-2xl bg-destructive text-destructive-foreground font-bold text-lg flex items-center justify-center gap-3 shadow-lg min-h-[64px] active:scale-95 transition-transform"
      aria-label={t.emergency}
    >
      <Phone className="w-6 h-6" />
      {t.emergency}
    </motion.button>
  );
};

export default EmergencyButton;
