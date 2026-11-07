// src/modules/gift_module/repository/order.repository.ts

import { orderApi } from "../api/order.api";
import type { GiftOrder } from "../interface/gift.types";

export const orderRepository = {
  async list(status?: string): Promise<GiftOrder[]> {
    const res = await orderApi.list(status);
    return Array.isArray(res.data) ? res.data : [];
  },

  async detail(id: number): Promise<GiftOrder | null> {
    const res = await orderApi.detail(id);
    return res.data ?? null;
  },

  async cancel(id: number, note?: string): Promise<GiftOrder | null> {
    const res = await orderApi.cancel(id, note);
    return res.data ?? null;
  },
};