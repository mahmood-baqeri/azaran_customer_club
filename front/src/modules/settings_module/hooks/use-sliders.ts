// src/modules/settings_module/hooks/use-sliders.ts

import { useCallback, useEffect, useRef, useState } from "react";
import { sliderRepository } from "../repository/settings.repository";
import type { SliderItem } from "../interface/settings.types";

export const useSliders = () => {
  const [sliders, setSliders] = useState<SliderItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inFlight = useRef(false);

  const refresh = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setLoading(true);
    setError(null);
    try {
      const items = await sliderRepository.list();
      setSliders(items);
    } catch (err) {
      console.warn("[sliders] load failed:", err);
      setError("خطا در دریافت اسلایدر");
    } finally {
      inFlight.current = false;
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { sliders, loading, error, refresh };
};