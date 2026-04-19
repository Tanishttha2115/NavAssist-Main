import { useState, useCallback, useRef } from "react";

// TTS Queue - speaks one after another, never overlapping
export const useTextToSpeech = () => {
  const queueRef = useRef<Array<{ text: string; lang: string }>>([]);
  const speakingRef = useRef(false);
  const lastSpoken = useRef("");
  const lastTime = useRef(0);

  const processQueue = useCallback(() => {
    if (speakingRef.current || queueRef.current.length === 0) return;

    const item = queueRef.current.shift()!;
    speakingRef.current = true;

    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(item.text);
    utter.lang = item.lang;
    utter.rate = 0.85;
    utter.pitch = 1.0;
    utter.volume = 1.0;

    utter.onend = () => {
      speakingRef.current = false;
      processQueue();
    };
    utter.onerror = () => {
      speakingRef.current = false;
      processQueue();
    };

    window.speechSynthesis.speak(utter);
  }, []);

  const speak = useCallback((text: string, lang: string = "en-US") => {
    const now = Date.now();
    if (text === lastSpoken.current && now - lastTime.current < 4000) return;
    lastSpoken.current = text;
    lastTime.current = now;

    queueRef.current.push({ text, lang });
    processQueue();
  }, [processQueue]);

  const clearQueue = useCallback(() => {
    queueRef.current = [];
    window.speechSynthesis.cancel();
    speakingRef.current = false;
  }, []);

  return { speak, clearQueue };
};

export const useSpeechRecognition = () => {
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const recRef = useRef<any>(null);

  const start = useCallback((lang: string = "en-US") => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) return;
    const rec = new SR();
    rec.lang = lang;
    rec.interimResults = false;
    rec.onresult = (e: any) => {
      const text = e.results[0][0].transcript;
      setTranscript(text);
    };
    rec.onstart = () => setListening(true);
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recRef.current = rec;
    rec.start();
  }, []);

  const stop = useCallback(() => {
    recRef.current?.stop();
  }, []);

  return { transcript, listening, start, stop };
};
