// front/src/modules/notifications_module/api/notifications.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type {
  NotificationItemData,
  NotificationListResult,
} from "../interface/notification.types";

const base = `${BASE_URL}notifications`;

// ─── envelope پاسخ بک‌اند ───
export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export interface NotificationListParams {
  unread_only?: boolean;
  type?: string;
  page?: number;
  page_size?: number;
}

// ─── data payloads ───
export interface UnreadCountData {
  count: number;
}

export interface ChangedData {
  changed: boolean;
}

export const notificationsApi = {
  list: (
    params: NotificationListParams = {}
  ): Promise<ApiResponse<NotificationListResult>> => {
    const qs = new URLSearchParams();
    if (params.unread_only) qs.set("unread_only", "true");
    if (params.type) qs.set("type", params.type);
    if (params.page) qs.set("page", String(params.page));
    if (params.page_size) qs.set("page_size", String(params.page_size));
    const q = qs.toString();
    return apiGET(`${base}/${q ? `?${q}` : ""}`, {}, true);
  },

  unreadCount: (): Promise<ApiResponse<UnreadCountData>> =>
    apiGET(`${base}/unread-count/`, {}, true),

  detail: (id: number): Promise<ApiResponse<NotificationItemData>> =>
    apiGET(`${base}/${id}/`, {}, true),

  markRead: (id: number): Promise<ApiResponse<ChangedData>> =>
    apiPOST(`${base}/${id}/read/`, {}, true),

  markAllRead: (): Promise<ApiResponse<UnreadCountData>> =>
    apiPOST(`${base}/read-all/`, {}, true),

  dismiss: (id: number): Promise<ApiResponse<ChangedData>> =>
    apiPOST(`${base}/${id}/dismiss/`, {}, true),
};