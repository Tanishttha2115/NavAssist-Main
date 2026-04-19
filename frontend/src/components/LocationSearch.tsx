import React, { useRef, useState, useImperativeHandle, forwardRef } from "react";
import { Search, MapPin } from "lucide-react";
import { useLang } from "@/contexts/LangContext";
import { Autocomplete, useJsApiLoader } from "@react-google-maps/api";
import { MAPS_KEY, libraries } from "@/components/MapSection";

interface Props {
  onSelect: (place: { name: string; lat: number; lng: number }) => void;
  onTextSubmit?: (text: string) => void;
}

export interface LocationSearchHandle {
  setQuery: (text: string) => void;
}

const LocationSearch = forwardRef<LocationSearchHandle, Props>(({ onTextSubmit }, ref) => {
  const { t } = useLang();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [autocomplete, setAutocomplete] = useState<any>(null);
  const { isLoaded } = useJsApiLoader({ id: "google-map-script", googleMapsApiKey: MAPS_KEY, libraries });

  useImperativeHandle(ref, () => ({
    setQuery: (text: string) => setQuery(text),
  }));

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && query.trim() && onTextSubmit) {
      onTextSubmit(query.trim());
    }
  };

  const submit = () => {
    if (query.trim() && onTextSubmit) onTextSubmit(query.trim());
  };

  return (
    <div className="flex gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        {isLoaded ? (
          <Autocomplete
            onLoad={(auto) => setAutocomplete(auto)}
            onPlaceChanged={() => {
              if (autocomplete) {
                const place = autocomplete.getPlace();
                if (!place.geometry) return;

                const selected = {
                  name: place.formatted_address || place.name,
                  lat: place.geometry.location.lat(),
                  lng: place.geometry.location.lng(),
                };

                setQuery(selected.name);
                if (onTextSubmit) onTextSubmit(selected.name);
              }
            }}
          >
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t.searchPlaceholder}
              className="w-full pl-11 pr-10 py-4 rounded-2xl bg-secondary text-foreground border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none text-base min-h-[56px]"
              aria-label={t.searchPlaceholder}
            />
          </Autocomplete>
        ) : (
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t.searchPlaceholder}
            className="w-full pl-11 pr-10 py-4 rounded-2xl bg-secondary text-foreground border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none text-base min-h-[56px]"
            aria-label={t.searchPlaceholder}
          />
        )}
        <MapPin className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
      </div>
      <button
        onClick={submit}
        disabled={!query.trim()}
        className="px-5 rounded-2xl bg-primary text-primary-foreground font-bold min-h-[56px] disabled:opacity-50 active:scale-95 transition-transform"
        aria-label="Search"
      >
        <Search className="w-5 h-5" />
      </button>
    </div>
  );
});

LocationSearch.displayName = "LocationSearch";

export default LocationSearch;
