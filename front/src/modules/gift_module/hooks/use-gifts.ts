// src/modules/gift_module/hooks/use-gifts.ts

import { useCallback, useEffect, useState } from "react";
import { giftRepository } from "../repository/gift.repository";
import type { Gift } from "../interface/gift.types";

export const useGifts = () => {
  const [gifts, setGifts] = useState<Gift[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await giftRepository.getGifts();
      setGifts(data);
    } catch (err) {
      console.error("[gifts] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { gifts, loading, refresh };
};