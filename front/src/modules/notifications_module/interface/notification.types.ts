// front/src/modules/notifications_module/interface/notification.types.ts

export type NotificationType =
  | "system"
  | "promotion"
  | "gift"
  | "project"
  | "factor"
  | "support"
  | "account"
  | "review"
  | "visit"
  | "other";

export type NotificationPriority = "low" | "normal" | "high";

export interface NotificationItemData {
  id: number;
  title: string;
  body: string;
  image: string | null;
  image_size: number;
  image_type: string;
  type: NotificationType;
  type_display: string;
  priority: NotificationPriority;
  priority_display: string;
  action_type: string;
  action_url: string;
  action_data: Record<string, unknown>;
  is_read: boolean;
  sent_at: string | null;
  created_at: string | null;
  expires_at: string | null;
}

export interface NotificationGroupData {
  id: string;
  group: string;
  items: NotificationItemData[];
}

export interface NotificationListResult {
  items: NotificationItemData[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface NotificationItemProps {
  item: NotificationItemData;
  onOpen: (item: NotificationItemData) => void;
}