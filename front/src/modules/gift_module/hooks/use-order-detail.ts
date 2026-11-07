// src/modules/gift_module/hooks/use-order-detail.ts

import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { orderRepository } from "../repository/order.repository";
import type { GiftOrder } from "../interface/gift.types";
import { MyNotification } from "../../../shared/utils/notification";

export const useOrderDetail = (id: number | null) => {
  const [order, setOrder] = useState<GiftOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await orderRepository.detail(id);
      setOrder(data);
    } catch (err) {
      console.error("[order detail] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const cancelOrder = async (note?: string): Promise<boolean> => {
    if (!id || cancelling) return false;
    setCancelling(true);
    try {
      const updated = await orderRepository.cancel(id, note);
      if (updated) {
        setOrder(updated);
        MyNotification("", "سفارش با موفقیت لغو شد.", "success");
        return true;
      }
      return false;
    } catch (err: unknown) {
      console.error("[order cancel] failed:", err);
      let msg = "خطا در لغو سفارش.";
      if (axios.isAxiosError(err)) {
        const backendMsg = err.response?.data?.message;
        if (typeof backendMsg === "string" && backendMsg.trim()) {
          msg = backendMsg;
        }
      }
      MyNotification("خطا", msg, "error");
      return false;
    } finally {
      setCancelling(false);
    }
  };

  return { order, loading, cancelling, cancelOrder, refresh };
};