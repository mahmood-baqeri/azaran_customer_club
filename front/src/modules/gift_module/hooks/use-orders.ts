// src/modules/gift_module/hooks/use-orders.ts

import { useCallback, useEffect, useState } from "react";
import { orderRepository } from "../repository/order.repository";
import type { GiftOrder } from "../interface/gift.types";

export const useOrders = (statusFilter?: string) => {
  const [orders, setOrders] = useState<GiftOrder[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await orderRepository.list(statusFilter);
      setOrders(data);
    } catch (err) {
      console.error("[orders] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { orders, loading, refresh };
};