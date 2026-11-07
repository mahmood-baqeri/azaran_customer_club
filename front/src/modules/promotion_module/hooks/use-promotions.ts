// src/modules/promotion_module/hooks/use-promotions.ts

import { useCallback, useEffect, useState } from "react";
import { promotionRepository } from "../repository/promotion.repository";
import type { Promotion } from "../interface/promotion.types";

export const usePromotions = () => {
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setPromotions(await promotionRepository.list());
    } catch (err) {
      console.error("[promotions] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { promotions, loading, refresh };
};