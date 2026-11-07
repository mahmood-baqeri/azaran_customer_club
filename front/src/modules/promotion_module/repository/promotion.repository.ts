// src/modules/promotion_module/repository/promotion.repository.ts

import { promotionApi } from "../api/promotion.api";
import type { Promotion, PromotionOrder } from "../interface/promotion.types";

export const promotionRepository = {
  async list(): Promise<Promotion[]> {
    const res = await promotionApi.list();
    return Array.isArray(res.data) ? res.data : [];
  },

  async buy(payload: Parameters<typeof promotionApi.buy>[0]): Promise<PromotionOrder | null> {
    const res = await promotionApi.buy(payload);
    return res.data ?? null;
  },

  async getOrders(): Promise<PromotionOrder[]> {
    const res = await promotionApi.orders();
    return Array.isArray(res.data) ? res.data : [];
  },

  async getOrderDetail(id: number): Promise<PromotionOrder | null> {
    const res = await promotionApi.orderDetail(id);
    return res.data ?? null;
  },

  async cancelOrder(id: number, note?: string): Promise<PromotionOrder | null> {
    const res = await promotionApi.cancelOrder(id, note);
    return res.data ?? null;
  },
};