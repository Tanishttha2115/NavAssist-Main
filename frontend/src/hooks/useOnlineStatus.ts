import { useState, useEffect } from "react";
import { useTextToSpeech } from "./useSpeech";

export const useOnlineStatus = () => {
  const [online, setOnline] = useState(navigator.onLine);
  const { speak } = useTextToSpeech();

  useEffect(() => {
    const onOnline = () => setOnline(true);
    const onOffline = () => {
      setOnline(false);
      speak("You are offline");
    };
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, [speak]);

  return online;
};
