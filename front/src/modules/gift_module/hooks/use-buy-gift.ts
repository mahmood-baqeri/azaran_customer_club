// src/modules/gift_module/hooks/use-buy-gift.ts

import { useCallback, useRef, useState } from "react";
import { giftRepository } from "../repository/gift.repository";
import type { GiftOrder } from "../interface/gift.types";
import { MyNotification } from "../../../shared/utils/notification";
import { useUser } from "../../user_module/hooks/use-user";
import { getErrorMessage } from "../../../shared/api/errors";

export const useBuyGift = () => {
  const { refreshUser } = useUser();
  const [submitting, setSubmitting] = useState(false);
  const submittingRef = useRef(false);

  const buy = useCallback(async (payload: {
    gift_id: number;
    quantity: number;
    receiver_name: string;
    receiver_phone: string;
    address: string;
    postal_code: string;
  }): Promise<GiftOrder | null> => {
    if (submittingRef.current) return null;
    submittingRef.current = true;
    setSubmitting(true);

    try {
      const idempotency_key = crypto.randomUUID();
      const order = await giftRepository.buyGift({ ...payload, idempotency_key });
      
      // ✅ آپدیت موجودی کیف پول در کل اپلیکیشن
      await refreshUser();
      
      MyNotification("", "سفارش با موفقیت ثبت شد.", "success");
      return order;
    } catch (err: unknown) {
      console.error("[buy] failed:", err);
      const errorMessage = "خطا در ثبت سفارش. دوباره تلاش کنید.";
      MyNotification("اخطار ! ", getErrorMessage(err, errorMessage), "error");
      return null;
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  }, [refreshUser]);

  return { buy, submitting };
};