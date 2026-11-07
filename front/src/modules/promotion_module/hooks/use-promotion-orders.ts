// src/modules/promotion_module/hooks/use-promotion-orders.ts

import { useCallback, useEffect, useState } from "react";
import { promotionRepository } from "../repository/promotion.repository";
import type { PromotionOrder } from "../interface/promotion.types";

export const usePromotionOrders = () => {
  const [orders, setOrders] = useState<PromotionOrder[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setOrders(await promotionRepository.getOrders());
    } catch (err) {
      console.error("[promotion orders] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { orders, loading, refresh };
};