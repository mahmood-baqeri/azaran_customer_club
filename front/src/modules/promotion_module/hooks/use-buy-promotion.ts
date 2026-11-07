// src/modules/promotion_module/hooks/use-buy-promotion.ts

import { useCallback, useRef, useState } from "react";
import { promotionRepository } from "../repository/promotion.repository";
import type { PromotionOrder } from "../interface/promotion.types";
import { MyNotification } from "../../../shared/utils/notification";
import { getErrorMessage } from "../../../shared/api/errors";

export const useBuyPromotion = () => {
  const [submitting, setSubmitting] = useState(false);
  const submittingRef = useRef(false);

  const buy = useCallback(async (payload: {
    promotion_id: number;
    receiver_name: string;
    receiver_phone: string;
    address: string;
    postal_code: string;
  }): Promise<PromotionOrder | null> => {
    if (submittingRef.current) return null;
    submittingRef.current = true;
    setSubmitting(true);

    try {
      const idempotency_key = crypto.randomUUID();
      const order = await promotionRepository.buy({ ...payload, idempotency_key });
      MyNotification("", "سفارش شما با موفقیت ثبت شد.", "success");
      return order;
    } catch (err: unknown) {
      const msg = "خطا در ثبت سفارش.";
      MyNotification("اخطار ! ", getErrorMessage(err, msg), "error");
      return null;
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  }, []);

  return { buy, submitting };
};