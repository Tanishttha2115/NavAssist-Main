import { useRef, useState, useCallback, useEffect } from "react";

export const useCamera = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [active, setActive] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);

  const start = useCallback(async () => {
    try {
      let stream: MediaStream;

      try {
        // try back camera (mobile)
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { exact: "environment" } },
        });
      } catch {
        // fallback for laptop / unsupported devices
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
      }
      streamRef.current = stream;
      const attachStream = () => {
        if (!videoRef.current) {
          console.log("Video ref not ready, retrying...");
          setTimeout(attachStream, 200);
          return;
        }

        const video = videoRef.current;

        // 🔥 reset stream
        video.srcObject = null;
        video.srcObject = stream;

        video.muted = true;
        video.playsInline = true;
        video.autoplay = true;

        video
          .play()
          .then(() => {
            console.log("Video playing ✅");
          })
          .catch(() => {
            video.onloadedmetadata = () => {
              video.play().catch(() => {});
            };
          });
      };

      attachStream();

      setActive(true);
    } catch {
      console.error("Camera access denied");
    }
  }, []);

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setActive(false);
  }, []);

  const captureFrame = useCallback((): string | null => {
    const video = videoRef.current;

    if (!video || video.readyState !== 4 || !video.videoWidth) {
      console.log("video not ready");
      return null;
    }

    if (!canvasRef.current) {
      canvasRef.current = document.createElement("canvas");
    }

    const canvas = canvasRef.current;
    canvas.width =320;
    canvas.height = Math.round((video.videoHeight / video.videoWidth) * 320);

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageSrc = canvas.toDataURL("image/jpeg", 0.7);

    console.log("IMAGE BAN GYI");
    console.log("LENGTH:", imageSrc?.length);

    return imageSrc;
  }, []);

  useEffect(() => () => stop(), [stop]);

  return { videoRef, active, start, stop, captureFrame };
};
