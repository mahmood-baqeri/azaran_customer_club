// src/modules/gift_module/hooks/use-gift-detail.ts

import { useCallback, useEffect, useState } from "react";
import { giftRepository } from "../repository/gift.repository";
import type { Gift } from "../interface/gift.types";

export const useGiftDetail = (id: number | null) => {
  const [gift, setGift] = useState<Gift | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await giftRepository.getGiftDetail(id);
      setGift(data);
    } catch (err) {
      console.error("[gift detail] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { gift, loading };
};