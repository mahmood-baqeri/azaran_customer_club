// src/modules/gift_module/interface/gift.types.ts

export interface Gift {
  id: number;
  title: string;
  description: string | null;
  photo: string | null;
  gallery: string[];
  azar_value: number;
  stock: number;
  is_active: boolean;
  created_at: string | null;
}

export type OrderStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "returned";

export interface GiftOrder {
  id: number;
  status: OrderStatus;
  status_display: string;
  quantity: number;
  total_azar_value: number;
  tracking_code: string | null;
  internal_note: string | null;
  created_at: string | null;
  updated_at: string | null;
  receiver_name: string;
  receiver_phone: string;
  address: string;
  postal_code: string;
  gift: {
    id: number;
    title: string;
    photo: string | null;
    azar_value: number;
  };
  user: {
    id: number;
    name: string;
    mobile: string;
  };
  assigned_to: {
    id: number;
    name: string;
  } | null;
  logs?: OrderLog[];
}

export interface OrderLog {
  id: number;
  action: string;
  from_status: OrderStatus | null;
  to_status: OrderStatus | null;
  note: string | null;
  created_at: string | null;
  changed_by: { id: number; name: string } | null;
}