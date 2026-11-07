// src/modules/settings_module/hooks/use-locations.ts

import { useCallback, useEffect, useState } from "react";
import { City, Province } from "../interface/settings.types";
import { locationApi } from "../api/settings.api";


export const useProvinces = () => {
  const [provinces, setProvinces] = useState<Province[]>([]);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await locationApi.getProvinces();
      setProvinces(res.data ?? []);
    } catch (err) {
      console.error("[locations] provinces load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { provinces, loading, refresh };
};

export const useCities = (provinceId: number | null) => {
  const [cities, setCities] = useState<City[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!provinceId) {
      setCities([]);
      return;
    }

    let cancelled = false;
    setLoading(true);

    locationApi
      .getCities(provinceId)
      .then((res) => {
        if (!cancelled) setCities(res.data ?? []);
      })
      .catch((err) => {
        if (!cancelled) {
          console.error("[locations] cities load failed:", err);
          setCities([]);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [provinceId]);

  return { cities, loading };
};