const API_BASE = "https://navassist-main.onrender.com";
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...options,
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}

export interface LatLng {
  lat: number;
  lng: number;
}

export interface NavStep {
  instruction: string;
  distance: string;
  end_location?: LatLng;
  start_location?: LatLng;
  distance_meters?: number;
  maneuver?: string; // turn-left, turn-right, straight, etc.
}

export interface NavigateRequest {
  destination: string;
  origin?: LatLng;
  destinationCoords?: LatLng;
}

export interface DetectedObject {
  label: string;
  position: "left" | "center" | "right";
  severity: "safe" | "warning" | "danger";
}

export interface NavigateResponse {
  message?: string;
  steps: NavStep[];
}

export interface CommandResult {
  intent: string; // NAVIGATE | SOS | DETECTION | UNKNOWN
  destination?: string;
}

export const api = {
  navigate: (payload: NavigateRequest | string) => {
    const body = typeof payload === "string" ? { destination: payload } : payload;
    return request<NavigateResponse>("/navigate", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  detectLive: async (image?: string) => {
    if (!image) {
      return request<{ alerts?: string[]; objects?: DetectedObject[]; error?: string }>("/detect-live", {
        method: "GET",
      }); 
    }

    const base64 = image.includes(",") ? image.split(",")[1] : image;

    const byteString = atob(base64);
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uint8Array = new Uint8Array(arrayBuffer);

    for (let i = 0; i < byteString.length; i++) {
      uint8Array[i] = byteString.charCodeAt(i);
    }

    const blob = new Blob([uint8Array], { type: "image/jpeg" });
    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");

    const res = await fetch(`${API_BASE}/detect-image`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },

  sendSOS: (location: { latitude: number; longitude: number }) =>
    request<{ status: string }>("/send-sos", {
      method: "POST",
      body: JSON.stringify({ location }),
    }),

  sendLocation: (location: { latitude: number; longitude: number }) =>
    request<{ status: string }>("/location", {
      method: "POST",
      body: JSON.stringify(location),
    }),

  processCommand: (text: string) =>
    request<CommandResult>("/process-command", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
};
