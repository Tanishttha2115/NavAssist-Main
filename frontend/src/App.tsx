import { useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { LangProvider } from "@/contexts/LangContext";
import Index from "./pages/Index.tsx";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

// ─── Permissions Hook ───────────────────────────────────────────────────────
const usePermissions = () => {
  useEffect(() => {
    // 📍 Location
    navigator.geolocation.getCurrentPosition(
      () => console.log("✅ Location granted"),
      (err) => console.warn("❌ Location denied:", err.message)
    );

    // 🎤 Microphone
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        console.log("✅ Mic granted");
        stream.getTracks().forEach((t) => t.stop()); // free karo stream
      })
      .catch((err) => console.warn("❌ Mic denied:", err.message));

    // 📷 Camera
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        console.log("✅ Camera granted");
        stream.getTracks().forEach((t) => t.stop()); // free karo stream
      })
      .catch((err) => console.warn("❌ Camera denied:", err.message));

    // 🔊 Speaker test (Web Speech API)
    if ("speechSynthesis" in window) {
      console.log("✅ Speaker ready");
    } else {
      console.warn("❌ Speaker not supported");
    }

    // 🚫 Pull-to-refresh band
    document.body.style.overscrollBehavior = "none";
  }, []); // sirf ek baar — app open hone pe
};

// ─── App ────────────────────────────────────────────────────────────────────
const App = () => {
  usePermissions();

  return (
    <ThemeProvider>
      <LangProvider>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </TooltipProvider>
        </QueryClientProvider>
      </LangProvider>
    </ThemeProvider>
  );
};

export default App;