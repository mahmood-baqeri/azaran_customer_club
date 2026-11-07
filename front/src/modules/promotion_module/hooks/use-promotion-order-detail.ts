// src/modules/promotion_module/hooks/use-promotion-order-detail.ts

import { useCallback, useEffect, useState } from "react";
import { promotionRepository } from "../repository/promotion.repository";
import type { PromotionOrder } from "../interface/promotion.types";
import { MyNotification } from "../../../shared/utils/notification";
import { getErrorMessage } from "../../../shared/api/errors";

export const usePromotionOrderDetail = (id: number | null) => {
  const [order, setOrder] = useState<PromotionOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setOrder(await promotionRepository.getOrderDetail(id));
    } catch (err) {
      console.error("[promotion order] load failed:", err);
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
      const updated = await promotionRepository.cancelOrder(id, note);
      if (updated) {
        setOrder(updated);
        MyNotification("", "سفارش با موفقیت لغو شد.", "success");
        return true;
      }
      return false;
    } catch (err: unknown) {
      console.error("[promotion cancel] failed:", err);
      const msg = "خطا در لغو سفارش.";
      MyNotification("اخطار ! ", getErrorMessage(err, msg), "error");
      return false;
    } finally {
      setCancelling(false);
    }
  };

  return { order, loading, cancelling, cancelOrder, refresh };
};