// src/modules/gift_module/repository/gift.repository.ts

import { giftApi } from "../api/gift.api";
import type { Gift, GiftOrder } from "../interface/gift.types";

export const giftRepository = {
  async getGifts(): Promise<Gift[]> {
    const res = await giftApi.list();
    return Array.isArray(res.data) ? res.data : [];
  },

  async getGiftDetail(id: number): Promise<Gift | null> {
    const res = await giftApi.detail(id);
    return res.data ?? null;
  },

  async buyGift(payload: Parameters<typeof giftApi.buy>[0]): Promise<GiftOrder | null> {
    const res = await giftApi.buy(payload);
    return res.data ?? null;
  },
};