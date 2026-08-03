import { useCallback } from "react";

export const useVibration = () => {
  const vibrate = useCallback((pattern: number | number[]) => {
    if (navigator.vibrate) navigator.vibrate(pattern);
  }, []);

  const left = useCallback(() => vibrate(100), [vibrate]);
  const right = useCallback(() => vibrate(300), [vibrate]);
  const danger = useCallback(() => vibrate([200, 100, 200, 100, 400]), [vibrate]);

  return { vibrate, left, right, danger };
};
