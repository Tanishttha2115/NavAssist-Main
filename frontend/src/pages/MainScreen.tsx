import React, { useState, useEffect, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { MapPin, Volume2 } from "lucide-react";
import { useLocation } from "@/hooks/useLocation";
import { useSpeechRecognition, useTextToSpeech } from "@/hooks/useSpeech";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { useVibration } from "@/hooks/useVibration";
import { useCamera } from "@/hooks/useCamera";
import { useLang } from "@/contexts/LangContext";
import { api, type NavStep, type DetectedObject } from "@/lib/api";
import { toast } from "sonner";
import MapSection from "@/components/MapSection";
import LocationSearch, { type LocationSearchHandle } from "@/components/LocationSearch";
import NavigationSteps from "@/components/NavigationSteps";
import DetectionAlerts from "@/components/DetectionAlerts";
import CameraOverlay from "@/components/CameraOverlay";
import MicButton from "@/components/MicButton";
import EmergencyButton from "@/components/EmergencyButton";
import BluetoothConnect from "@/components/BluetoothConnect";
import OfflineBanner from "@/components/OfflineBanner";
import ThemeToggle from "@/components/ThemeToggle";
import LangToggle from "@/components/LangToggle";

const MainScreen: React.FC = () => {
  const { t, speechLang } = useLang();
  const { location, error: locError } = useLocation();
  const { transcript, listening, start, stop } = useSpeechRecognition();
  const { speak, clearQueue } = useTextToSpeech();
  const online = useOnlineStatus();
  const { left, right, danger } = useVibration();
  const camera = useCamera();

  const searchRef = useRef<LocationSearchHandle>(null);
  const [destination, setDestination] = useState<{ name: string; lat: number; lng: number } | null>(null);
  const [navSteps, setNavSteps] = useState<NavStep[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [detectedObjects, setDetectedObjects] = useState<DetectedObject[]>([]);
  const [navigating, setNavigating] = useState(false);

  const detectionRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastSpokenRef = useRef("");

  // Welcome message
  useEffect(() => {
    const id = setTimeout(() => speak(t.welcome, speechLang), 1000);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Announce location errors
  useEffect(() => {
    if (locError) speak(t.locationFail, speechLang);
  }, [locError, t, speechLang]);

  // Voice transcript -> mirror into search input AND auto-submit
  useEffect(() => {
    if (!transcript) return;
    searchRef.current?.setQuery(transcript);
    stop();
    handleTextSubmit(transcript);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transcript]);

  const handleSOS = async () => {
    danger();
    speak(t.emergencyCall, speechLang);
    if (location) {
      try {
        await api.sendSOS({ latitude: location.lat, longitude: location.lng });
      } catch {
        toast.error("SOS failed");
      }
    }
  };

  // Receive simplified real Google steps from MapSection
  const handleStepsReady = useCallback((simple: string[]) => {
    setNavSteps(simple.map((s) => ({ instruction: s, distance: "" } as NavStep)));
    setCurrentStep(0);
    setNavigating(true);
    camera.start();
  }, [camera]);

  const handleStepChange = useCallback(
    (idx: number) => {
      setCurrentStep(idx);
      const instr = (navSteps[idx]?.instruction ?? "").toLowerCase();
      if (instr.includes("left")) left();
      else if (instr.includes("right")) right();
    },
    [navSteps, left, right]
  );

  // Camera control
  useEffect(() => {
    if (navigating) {
      camera.start();
    } else {
      camera.stop();
    }
  }, [navigating]);

  // ─── Live Detection ───────────────────────────────────────────────────────
  useEffect(() => {
    if (!navigating) {
      if (detectionRef.current) clearInterval(detectionRef.current);
      setDetectedObjects([]);
      lastSpokenRef.current = "";
      return;
    }

    const speakOnce = (text: string) => {
      try {
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
      } catch {}
    };

    const phraseFor = (label: string, position: "left" | "center" | "right") => {
      const Label = label.charAt(0).toUpperCase() + label.slice(1);
      if (position === "center") return `${Label} ahead, stop`;
      if (position === "left") return `${Label} on left, move right`;
      return `${Label} on right, move left`;
    };

    const tick = async () => {
      try {
        console.log("DETECTION RUNNING");

        const video = camera.videoRef.current;
        if (!video || video.readyState < 2 || video.videoWidth === 0) return;

        // captureFrame returns base64 data URL string
        const image = camera.captureFrame();
        if (!image) return;

        // ✅ Use api.detectLive — handles base64→Blob + FormData correctly
        const res = await api.detectLive(image);
        if (!res) return;

        console.log("DETECTION RESPONSE:", res);

        const objects: string[] = res.objects ?? [];
        if (objects.length === 0) return;

        // Map each object to a DetectedObject (all "center" since backend
        // doesn't return position — position logic can be added later)
        const alerts = objects.map((obj) => `${obj} ahead`);

        const parsed = alerts.map((a) => {
          const tokens = a.toLowerCase().trim().split(/\s+/);
          let position: "left" | "center" | "right" = "center";
          if (tokens.includes("left")) position = "left";
          else if (tokens.includes("right")) position = "right";
          const label =
            tokens.find((tk) => !["left", "right", "center", "ahead"].includes(tk)) ||
            "object";
          return { label, position };
        });

        // Priority: center > left/right
        const chosen =
          parsed.find((p) => p.position === "center") || parsed[0];

        const key = `${chosen.label}-${chosen.position}`;
        lastSpokenRef.current = key;

        const obj: DetectedObject = {
          label: chosen.label,
          position: chosen.position,
          severity: chosen.position === "center" ? "danger" : "warning",
        };

        setDetectedObjects([obj]);
        speakOnce(phraseFor(chosen.label, chosen.position));

        if (chosen.position === "center") danger();
        else if (chosen.position === "left") left();
        else right();
      } catch (err) {
        console.error("Detection error:", err);
      }
    };

    tick();
    detectionRef.current = setInterval(tick, 1500);
    return () => {
      if (detectionRef.current) clearInterval(detectionRef.current);
    };
  }, [navigating, danger, left, right]);

  // Push live location to backend periodically while navigating
  useEffect(() => {
    if (!navigating || !location) return;
    api.sendLocation({ latitude: location.lat, longitude: location.lng }).catch(() => {});
  }, [location, navigating]);

  const handleMicPress = () => {
    if (listening) stop();
    else {
      speak(t.listening, speechLang);
      start(speechLang);
    }
  };

  const handlePlaceSelect = useCallback(
    (place: { name: string; lat: number; lng: number }) => {
      setDestination(place);
      speak(`${t.destinationSet} ${place.name}`, speechLang);
    },
    [t, speechLang, speak]
  );

  const handleTextSubmit = useCallback(
    (text: string) => {
      if (!(window as any).google?.maps) {
        toast.error("Map not ready");
        return;
      }
      const geocoder = new window.google.maps.Geocoder();
      geocoder.geocode({ address: text }, (results, status) => {
        if (status === "OK" && results && results[0]) {
          const loc = results[0].geometry.location;
          const place = {
            name: results[0].formatted_address,
            lat: loc.lat(),
            lng: loc.lng(),
          };
          setDestination(place);
          speak(`${t.destinationSet} ${place.name}`, speechLang);
        } else {
          toast.error("Place not found");
        }
      });
    },
    [t, speechLang, speak]
  );

  const handleUseCurrentLocation = () => {
    if (location) speak(t.usingCurrentLoc, speechLang);
    else speak(t.locNotAvailable, speechLang);
  };

  const stopNavigation = () => {
    setNavigating(false);
    setNavSteps([]);
    setCurrentStep(0);
    setDetectedObjects([]);
    setDestination(null);
    camera.stop();
    clearQueue();
    speak(t.navStopped, speechLang);
  };

  return (
    <div className="min-h-screen bg-background safe-area-bottom">
      <OfflineBanner online={online} />

      <div className="sticky top-0 z-30 bg-background/80 backdrop-blur-xl border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">{t.appName}</h1>
            <p className="text-xs text-muted-foreground">{t.subtitle}</p>
          </div>
          <div className="flex items-center gap-2">
            <LangToggle />
            <BluetoothConnect />
            <ThemeToggle />
          </div>
        </div>
      </div>

      <div className="px-4 py-4 space-y-4 pb-36">
        <MapSection
          userLocation={location}
          destination={destination ? { lat: destination.lat, lng: destination.lng } : null}
          onStepsReady={handleStepsReady}
          onStepChange={handleStepChange}
        />

        <LocationSearch
          ref={searchRef}
          onSelect={handlePlaceSelect}
          onTextSubmit={handleTextSubmit}
        />

        <div className="flex gap-3">
          <button
            onClick={handleUseCurrentLocation}
            className="flex-1 py-4 rounded-2xl bg-secondary text-foreground border border-border text-base font-semibold flex items-center justify-center gap-2 min-h-[56px] active:scale-95 transition-transform"
            aria-label={t.myLocation}
          >
            <MapPin className="w-5 h-5 text-primary" />
            {t.myLocation}
          </button>
          {navigating && (
            <button
              onClick={stopNavigation}
              className="px-8 py-4 rounded-2xl bg-destructive text-destructive-foreground text-base font-bold min-h-[56px] active:scale-95 transition-transform"
              aria-label={t.stop}
            >
              {t.stop}
            </button>
          )}
        </div>

        <MicButton listening={listening} onPress={handleMicPress} />

        {transcript && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center gap-2 p-3 rounded-xl bg-secondary border border-border"
          >
            <Volume2 className="w-4 h-4 text-primary" />
            <p className="text-base font-medium text-foreground">"{transcript}"</p>
          </motion.div>
        )}

        <NavigationSteps steps={navSteps} currentStep={currentStep} distanceToNext={null} />
        <DetectionAlerts objects={detectedObjects} />
        <EmergencyButton location={location} />
      </div>

      <CameraOverlay
        videoRef={camera.videoRef}
        active={camera.active}
        start={camera.start}
        stop={camera.stop}
      />
    </div>
  );
};

export default MainScreen;
