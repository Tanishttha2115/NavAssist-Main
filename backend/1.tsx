import React, { useState } from "react";
import { GoogleMap, MarkerF, Polyline, useJsApiLoader } from "@react-google-maps/api";
import { motion } from "framer-motion";
import { Maximize2, Minimize2 } from "lucide-react";
import { useLang } from "@/contexts/LangContext";

const MAPS_KEY = "AIzaSyCv6dwB1BL3uF2uliD-rp10-xSu8bhmesI";
const libraries: ("places")[] = ["places"];

interface Props {
  userLocation: { lat: number; lng: number } | null;
  destination: { lat: number; lng: number } | null;
  steps?: any[];
}

const darkMapStyles = [
  { elementType: "geometry", stylers: [{ color: "#1d2c4d" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#8ec3b9" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#1a3646" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#304a7d" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0e1626" }] },
];

const MapSection: React.FC<Props> = ({ userLocation, destination, steps }) => {
  const { t } = useLang();
  const [expanded, setExpanded] = useState(false);
  const [path, setPath] = useState<{ lat: number; lng: number }[]>([]);
  const { isLoaded } = useJsApiLoader({ googleMapsApiKey: MAPS_KEY, libraries });

  React.useEffect(() => {
    if (!steps || steps.length === 0) {
      setPath([]);
      return;
    }

    const newPath: { lat: number; lng: number }[] = [];

    steps.forEach((step: any) => {
      if (step?.start_location?.lat && step?.start_location?.lng) {
        newPath.push({
          lat: step.start_location.lat,
          lng: step.start_location.lng,
        });
      }
      if (step?.end_location?.lat && step?.end_location?.lng) {
        newPath.push({
          lat: step.end_location.lat,
          lng: step.end_location.lng,
        });
      }
    });

    // 🔥 fallback if backend steps missing coords
    if (newPath.length === 0 && userLocation && destination) {
      setPath([
        { lat: userLocation.lat, lng: userLocation.lng },
        { lat: destination.lat, lng: destination.lng },
      ]);
    } else {
      setPath(newPath);
    }
  }, [steps, userLocation, destination]);

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
          disableDefaultUI: false,
          zoomControl: true,
          streetViewControl: false,
          mapTypeControl: false,
          fullscreenControl: false,
          styles: darkMapStyles,
        }}
      >
        {path.length > 0 && (
          <Polyline
            path={path}
            options={{ strokeColor: "#3b82f6", strokeWeight: 5 }}
          />
        )}
        {userLocation && <MarkerF position={userLocation} label={t.you} />}
        {destination && <MarkerF position={destination} label={t.dest} />}
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