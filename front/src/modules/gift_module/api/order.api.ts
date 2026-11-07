// src/modules/gift_module/api/order.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { GiftOrder } from "../interface/gift.types";

export interface OrderListResponse {
  status: "Success" | "Error";
  message: string;
  data: GiftOrder[];
}

export interface OrderDetailResponse {
  status: "Success" | "Error";
  message: string;
  data: GiftOrder;
}

export const orderApi = {
  list: (status?: string): Promise<OrderListResponse> => {
    const q: Record<string, unknown> = {};
    if (status) q.status = status;
    return apiGET(`${BASE_URL}gift-orders/`, q, true);
  },

  detail: (id: number): Promise<OrderDetailResponse> =>
    apiGET(`${BASE_URL}gift-orders/${id}/`, {}, true),

  cancel: (id: number, note?: string): Promise<OrderDetailResponse> =>
    apiPOST(`${BASE_URL}gift-orders/${id}/cancel/`, { note }, true),
};