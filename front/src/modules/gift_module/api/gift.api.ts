// src/modules/gift_module/api/gift.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { Gift, GiftOrder } from "../interface/gift.types";

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

export const giftApi = {
  list: (): Promise<ApiListResponse<Gift>> =>
    apiGET(`${BASE_URL}gifts/`, {}, true),

  detail: (id: number): Promise<ApiItemResponse<Gift>> =>
    apiGET(`${BASE_URL}gifts/${id}/`, {}, true),

  buy: (payload: {
    gift_id: number;
    quantity: number;
    receiver_name: string;
    receiver_phone: string;
    address: string;
    postal_code: string;
    idempotency_key: string;
  }): Promise<ApiItemResponse<GiftOrder>> =>
    apiPOST(`${BASE_URL}gift-orders/`, payload, true),
};