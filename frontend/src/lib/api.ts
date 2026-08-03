const API_BASE = "http://localhost:8000";
function base64ToBlob(dataUrl: string): Blob {
  const [header, base64] = dataUrl.split(",");
  const mime = header.match(/:(.*?);/)?.[1] ?? "image/jpeg";
  const binary = atob(base64);
  const array = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    array[i] = binary.charCodeAt(i);
  }
  return new Blob([array], { type: mime });
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers:
        options?.body instanceof FormData
          ? {}
          : { "Content-Type": "application/json" },
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
  maneuver?: string; 
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
  intent: string;
  destination?: string;
}

export const api = {
  navigate: (payload: NavigateRequest | string) => {
    const body =
      typeof payload === "string" ? { destination: payload } : payload;
    return request<NavigateResponse>("/navigate", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  detectLive: async (image?: string) => {
    if (!image) return;

    if (!image.startsWith("data:image")) {
      console.error("Invalid image format");
      return;
    }

    const blob = base64ToBlob(image);

    const formData = new FormData();
    formData.append("file", blob, "frame.jpg"); 

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);

    try {
      const res = await fetch(`${API_BASE}/detect-image`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return res.json();
    } finally {
      clearTimeout(timeout);
    }
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