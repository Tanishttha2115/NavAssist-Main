import React, { useEffect, useRef, useState } from "react";
import { GoogleMap, MarkerF, DirectionsRenderer, useJsApiLoader } from "@react-google-maps/api";
import { motion } from "framer-motion";
import { Maximize2, Minimize2 } from "lucide-react";
import { useLang } from "@/contexts/LangContext";

const MAPS_KEY = "AIzaSyCv6dwB1BL3uF2uliD-rp10-xSu8bhmesI";
const libraries: ("places")[] = ["places"];

interface Props {
  userLocation: { lat: number; lng: number } | null;
  destination: { lat: number; lng: number } | null;
  onStepsReady?: (simpleSteps: string[]) => void;
  onStepChange?: (index: number) => void;
}

const darkMapStyles = [
  { elementType: "geometry", stylers: [{ color: "#1d2c4d" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#8ec3b9" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#1a3646" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#304a7d" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0e1626" }] },
];

const simplify = (step: any): string => {
  const m = (step?.maneuver || "").toString().toLowerCase();
  const txt = (step?.instructions || "").toString().toLowerCase();
  const hay = m + " " + txt;
  if (hay.includes("left")) return "Turn left";
  if (hay.includes("right")) return "Turn right";
  return "Go straight";
};

const speak = (text: string) => {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-US";
  u.rate = 0.95;
  window.speechSynthesis.speak(u);
};

// Haversine distance in meters
const distMeters = (a: { lat: number; lng: number }, b: { lat: number; lng: number }) => {
  const R = 6371000;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const x =
    Math.sin(dLat / 2) ** 2 +
    Math.sin(dLng / 2) ** 2 * Math.cos(lat1) * Math.cos(lat2);
  return 2 * R * Math.asin(Math.sqrt(x));
};

const MapSection: React.FC<Props> = ({ userLocation, destination, onStepsReady, onStepChange }) => {
  const { t } = useLang();
  const [expanded, setExpanded] = useState(false);
  const [directions, setDirections] = useState<google.maps.DirectionsResult | null>(null);
  const { isLoaded } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey: MAPS_KEY,
    libraries,
  });

  const requestedKeyRef = useRef<string>("");
  const stepsRef = useRef<google.maps.DirectionsStep[]>([]);
  const currentStepRef = useRef(0);

  // Request directions once per origin->destination pair
  useEffect(() => {
    if (!isLoaded || !userLocation || !destination) return;
    const key = `${userLocation.lat.toFixed(4)},${userLocation.lng.toFixed(4)}->${destination.lat},${destination.lng}`;
    if (requestedKeyRef.current === key) return;
    requestedKeyRef.current = key;

    const service = new window.google.maps.DirectionsService();
    service.route(
      {
        origin: userLocation,
        destination,
        travelMode: window.google.maps.TravelMode.WALKING,
      },
      (result, status) => {
        if (status === "OK" && result) {
          setDirections(result);
          const steps = result.routes[0]?.legs[0]?.steps ?? [];
          stepsRef.current = steps;
          currentStepRef.current = 0;
          onStepsReady?.(steps.map(simplify));
          if (steps.length) {
            onStepChange?.(0);
            speak(simplify(steps[0]));
          }
        } else {
          console.error("Directions failed:", status);
        }
      }
    );
  }, [isLoaded, userLocation, destination, onStepsReady, onStepChange]);

  // Reset when destination cleared
  useEffect(() => {
    if (!destination) {
      requestedKeyRef.current = "";
      stepsRef.current = [];
      currentStepRef.current = 0;
      setDirections(null);
    }
  }, [destination]);

  // Watch user location vs current step end_location
  useEffect(() => {
    if (!userLocation || stepsRef.current.length === 0) return;
    const idx = currentStepRef.current;
    const step = stepsRef.current[idx];
    const end = step?.end_location;
    if (!end) return;

    const endLatLng = { lat: end.lat(), lng: end.lng() };
    const d = distMeters(userLocation, endLatLng);

    if (d < 20) {
      const next = idx + 1;
      if (next < stepsRef.current.length) {
        currentStepRef.current = next;
        onStepChange?.(next);
        speak(simplify(stepsRef.current[next]));
      } else {
        speak("You have arrived");
        stepsRef.current = [];
        onStepChange?.(idx);
      }
    }
  }, [userLocation, onStepChange]);

  if (!isLoaded) {
    return (
      <div className="h-[220px] rounded-2xl bg-secondary animate-pulse flex items-center justify-center">
        <span className="text-muted-foreground text-sm">{t.mapLoading}</span>
      </div>
    );
  }

  const center = userLocation || destination || { lat: 28.6139, lng: 77.209 };

  return (
    <motion.div
      layout
      className={`relative rounded-2xl overflow-hidden border border-border ${
        expanded ? "fixed inset-0 z-50" : "h-[220px]"
      }`}
    >
      <GoogleMap
        mapContainerStyle={{ width: "100%", height: "100%" }}
        center={center}
        zoom={16}
        options={{
          zoomControl: true,
          streetViewControl: false,
          mapTypeControl: false,
          fullscreenControl: false,
          styles: darkMapStyles,
        }}
      >
        {userLocation && <MarkerF position={userLocation} label={t.you} />}
        {destination && <MarkerF position={destination} label={t.dest} />}
        {directions && (
          <DirectionsRenderer
            directions={directions}
            options={{
              suppressMarkers: true,
              polylineOptions: { strokeColor: "#3b82f6", strokeWeight: 6 },
            }}
          />
        )}
      </GoogleMap>

      <button
        onClick={() => setExpanded(!expanded)}
        className="absolute top-3 right-3 p-3 rounded-xl bg-card/80 backdrop-blur-sm border border-border text-foreground min-w-[48px] min-h-[48px] flex items-center justify-center"
        aria-label={expanded ? t.shrinkMap : t.expandMap}
      >
        {expanded ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
      </button>
    </motion.div>
  );
};

export default MapSection;
export { MAPS_KEY, libraries };
