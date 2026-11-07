// src/modules/promotion_module/api/promotion.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { Promotion, PromotionOrder } from "../interface/promotion.types";

export interface ApiListResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T[];
}

export interface ApiItemResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export const promotionApi = {
  // لیست پک‌ها
  list: (): Promise<ApiListResponse<Promotion>> =>
    apiGET(`${BASE_URL}promotions/`, {}, true),

  // ثبت سفارش جدید
  buy: (payload: {
    promotion_id: number;
    receiver_name: string;
    receiver_phone: string;
    address: string;
    postal_code: string;
    idempotency_key: string;
  }): Promise<ApiItemResponse<PromotionOrder>> =>
    apiPOST(`${BASE_URL}promotions/orders/`, payload, true),

  // لیست سفارشات من
  orders: (): Promise<ApiListResponse<PromotionOrder>> =>
    apiGET(`${BASE_URL}promotions/orders/`, {}, true),

  // جزئیات یک سفارش
  orderDetail: (id: number): Promise<ApiItemResponse<PromotionOrder>> =>
    apiGET(`${BASE_URL}promotions/orders/${id}/`, {}, true),

  // لغو سفارش
  cancelOrder: (id: number, note?: string): Promise<ApiItemResponse<PromotionOrder>> =>
    apiPOST(`${BASE_URL}promotions/orders/${id}/cancel/`, { note }, true),
};