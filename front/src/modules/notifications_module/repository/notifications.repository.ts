// front/src/modules/notifications_module/repository/notifications.repository.ts

import {
  notificationsApi,
  type NotificationListParams,
} from "../api/notifications.api";
import type {
  NotificationItemData,
  NotificationListResult,
} from "../interface/notification.types";

export const notificationsRepository = {
  async list(params: NotificationListParams = {}): Promise<NotificationListResult> {
    const res = await notificationsApi.list(params);
    return res.data;
  },

  async unreadCount(): Promise<number> {
    const res = await notificationsApi.unreadCount();
    return res.data.count;
  },

  async detail(id: number): Promise<NotificationItemData> {
    const res = await notificationsApi.detail(id);
    return res.data;
  },

  async markRead(id: number): Promise<boolean> {
    const res = await notificationsApi.markRead(id);
    return res.data.changed;
  },

  async markAllRead(): Promise<number> {
    const res = await notificationsApi.markAllRead();
    return res.data.count;
  },

  async dismiss(id: number): Promise<boolean> {
    const res = await notificationsApi.dismiss(id);
    return res.data.changed;
  },
};