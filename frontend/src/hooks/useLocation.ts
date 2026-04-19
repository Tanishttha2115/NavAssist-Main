import { useState, useEffect, useCallback } from "react";

interface LocationState {
  lat: number;
  lng: number;
}

export const useLocation = () => {
  const [location, setLocation] = useState<LocationState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const update = useCallback(() => {
    if (!navigator.geolocation) {
      setError("Geolocation not supported");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      (err) => setError(err.message)
    );
  }, []);

  useEffect(() => {
    update();
    const id = navigator.geolocation?.watchPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      (err) => setError(err.message),
      { enableHighAccuracy: true }
    );
    return () => {
      if (id !== undefined) navigator.geolocation.clearWatch(id);
    };
  }, []);

  return { location, error, refresh: update };
};
