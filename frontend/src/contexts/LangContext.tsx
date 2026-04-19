import React, { createContext, useContext, useState, useCallback } from "react";

type Lang = "en" | "hi";

const translations = {
  en: {
    appName: "NavAssist AI",
    subtitle: "Your AI Navigation Assistant",
    welcome: "Hello. NavAssist AI is ready. Press the mic button and say where you want to go.",
    listening: "Listening, please speak",
    listeningLabel: "Listening...",
    pressToSpeak: "Press to speak",
    navigatingTo: "Navigating to",
    setDestination: "Please set a destination",
    arrived: "You have arrived at your destination",
    navStopped: "Navigation stopped",
    destinationSet: "Destination set to",
    usingCurrentLoc: "Using current location",
    locNotAvailable: "Location not available",
    searchPlaceholder: "Search destination...",
    myLocation: "My Location",
    go: "Go",
    stop: "Stop",
    emergency: "Emergency SOS",
    emergencyCall: "Emergency call being initiated",
    navigation: "Navigation",
    detection: "Detection",
    mapLoading: "Loading map...",
    expandMap: "Expand map",
    shrinkMap: "Shrink map",
    you: "You",
    dest: "Dest",
    stopListening: "Stop listening",
    startVoice: "Press to say where you want to go",
    connectStick: "Connect Smart Stick",
    stickConnected: "Stick Connected",
    btNotSupported: "Bluetooth not supported on this device",
    btCancelled: "Connection cancelled",
    offline: "You are offline",
    safe: "Safe",
    warning: "Warning",
    danger: "Danger",
    dirStop: "Stop",
    dirMoveRight: "Move right",
    dirMoveLeft: "Move left",
    recalculating: "Recalculating route",
    offRoute: "You are off route",
    inMeters: "in",
    meters: "meters",
    locationFail: "Unable to fetch location",
    currentStep: "Current step",
    // Mock steps
    step1: "Walk straight",
    step1d: "20m",
    step2: "Turn left at the crossing",
    step2d: "5m",
    step3: "Turn right after the building",
    step3d: "10m",
    step4: "Continue straight",
    step4d: "15m",
    step5: "You have arrived",
    step5d: "0m",
    // Mock detections
    det1: "Person ahead",
    det2: "Obstacle on left",
    det3: "Stairs ahead",
    det4: "Clear path",
    det5: "Vehicle approaching",
    langToggle: "हिंदी",
  },
  hi: {
    appName: "NavAssist AI",
    subtitle: "आपका AI नेविगेशन सहायक",
    welcome: "नमस्ते। NavAssist AI तैयार है। माइक बटन दबाकर बोलें कहाँ जाना है।",
    listening: "सुन रहा हूँ, बोलिए",
    listeningLabel: "सुन रहा हूँ...",
    pressToSpeak: "बोलने के लिए दबाएं",
    navigatingTo: "की ओर नेविगेट कर रहे हैं",
    setDestination: "कृपया मंज़िल बताएं",
    arrived: "आप अपनी मंज़िल पर पहुँच गए हैं",
    navStopped: "नेविगेशन बंद किया गया",
    destinationSet: "मंज़िल",
    usingCurrentLoc: "आपकी वर्तमान लोकेशन का उपयोग हो रहा है",
    locNotAvailable: "लोकेशन उपलब्ध नहीं है",
    searchPlaceholder: "मंज़िल खोजें...",
    myLocation: "मेरी लोकेशन",
    go: "चलें",
    stop: "रुकें",
    emergency: "आपातकालीन SOS",
    emergencyCall: "आपातकालीन कॉल शुरू हो रही है",
    navigation: "नेविगेशन",
    detection: "पहचान",
    mapLoading: "मैप लोड हो रहा है...",
    expandMap: "मैप बड़ा करें",
    shrinkMap: "मैप छोटा करें",
    you: "आप",
    dest: "मंज़िल",
    stopListening: "सुनना बंद करें",
    startVoice: "बोलकर बताएं कहाँ जाना है",
    connectStick: "स्मार्ट स्टिक जोड़ें",
    stickConnected: "स्टिक जुड़ी हुई",
    btNotSupported: "ब्लूटूथ इस डिवाइस पर उपलब्ध नहीं",
    btCancelled: "कनेक्शन रद्द",
    offline: "आप ऑफ़लाइन हैं",
    safe: "सुरक्षित",
    warning: "सावधान",
    danger: "ख़तरा",
    dirStop: "रुकें",
    dirMoveRight: "दाएं चलें",
    dirMoveLeft: "बाएं चलें",
    recalculating: "रास्ता दोबारा निकाला जा रहा है",
    offRoute: "आप रास्ते से भटक गए हैं",
    inMeters: "में",
    meters: "मीटर",
    locationFail: "लोकेशन नहीं मिल पा रही",
    currentStep: "वर्तमान चरण",
    step1: "सीधे चलें",
    step1d: "20 मीटर",
    step2: "बाएं मुड़ें",
    step2d: "5 मीटर",
    step3: "दाएं मुड़ें",
    step3d: "10 मीटर",
    step4: "सीधे चलते रहें",
    step4d: "15 मीटर",
    step5: "आप पहुँच गए हैं",
    step5d: "0 मीटर",
    det1: "सामने व्यक्ति है",
    det2: "बाईं ओर रुकावट",
    det3: "सीढ़ियाँ आ रही हैं",
    det4: "रास्ता साफ़ है",
    det5: "गाड़ी आ रही है",
    langToggle: "English",
  },
} as const;

type Translations = typeof translations["en"];

interface LangContextType {
  lang: Lang;
  t: Translations;
  toggleLang: () => void;
  speechLang: string;
}

const LangContext = createContext<LangContextType | null>(null);

export const useLang = () => {
  const ctx = useContext(LangContext);
  if (!ctx) throw new Error("useLang must be inside LangProvider");
  return ctx;
};

export const LangProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLang] = useState<Lang>("en");

  const toggleLang = useCallback(() => {
    setLang((prev) => (prev === "en" ? "hi" : "en"));
  }, []);

  const t: Translations = translations[lang] as Translations;
  const speechLang = lang === "hi" ? "hi-IN" : "en-US";

  return (
    <LangContext.Provider value={{ lang, t, toggleLang, speechLang }}>
      {children}
    </LangContext.Provider>
  );
};
