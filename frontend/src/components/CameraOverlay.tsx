import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, X } from "lucide-react";

interface CameraOverlayProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  active: boolean;
  start: () => void;
  stop: () => void;
}

const CameraOverlay: React.FC<CameraOverlayProps> = ({ videoRef, active, start, stop }) => {
  React.useEffect(() => {
    if (active && videoRef.current) {
      videoRef.current.onloadedmetadata = () => {
        videoRef.current?.play().catch(() => {});
      };
    }
  }, [active, videoRef]);
  return (
    <>
      {!active && (
        <button
          onClick={start}
          className="fixed bottom-24 left-4 z-40 p-3 rounded-xl bg-card border border-border shadow-lg text-foreground"
          aria-label="Open camera"
        >
          <Camera className="w-5 h-5" />
        </button>
      )}

      <AnimatePresence>
        {active && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed bottom-24 left-4 z-40 w-[140px] h-[100px] sm:w-[180px] sm:h-[130px] rounded-2xl overflow-hidden border-2 border-primary shadow-2xl bg-black"
          >
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{ background: "black" }}
              className="w-full h-full object-cover"
            />
            <button
              onClick={stop}
              className="absolute top-2 right-2 p-2 rounded-full bg-card/90 text-foreground shadow-md"
              aria-label="Close camera"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="absolute bottom-2 left-2 px-2 py-1 rounded-md bg-card/80 text-foreground text-xs font-medium">
              Live
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default CameraOverlay;
