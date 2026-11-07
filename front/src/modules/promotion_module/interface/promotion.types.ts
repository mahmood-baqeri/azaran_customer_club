// src/modules/promotion_module/interface/promotion.types.ts

export interface PromotionItem {
  id: number;
  title: string;
  badge: string | null;
  photo: string | null;
}

export interface Promotion {
  id: number;
  title: string;
  is_active: boolean;
  items: PromotionItem[];
}

export type PromotionOrderStatus =
  | "pending"
  | "approved"
  | "shipped"
  | "delivered"
  | "rejected"
  | "cancelled"
  | "returned";

export interface PromotionOrderLog {
  id: number;
  action: string;
  from_status: PromotionOrderStatus | null;
  to_status: PromotionOrderStatus | null;
  note: string | null;
  created_at: string | null;
}

export interface PromotionOrder {
  id: number;
  status: PromotionOrderStatus;
  status_display: string;
  tracking_code: string | null;
  created_at: string | null;
  receiver_name: string;
  receiver_phone: string;
  address: string;
  postal_code: string;
  promotion: {
    id: number;
    title: string;
    items: {
      id: number;
      title: string;
      photo: string | null;
    }[];
  };
  logs?: PromotionOrderLog[];
}