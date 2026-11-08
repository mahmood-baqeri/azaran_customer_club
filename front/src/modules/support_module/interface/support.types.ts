// src/modules/support_module/interface/support.types.ts

export type SupportCategory = 
  | "site_issue" 
  | "invoice" 
  | "gift_order" 
  | "complaint" 
  | "suggestion" 
  | "other";

export type SupportStatus = "open" | "in_progress" | "resolved" | "closed";

export interface SupportMessage {
  id: number;
  text: string;
  file: string | null;
  is_admin_reply: boolean;
  is_read: boolean;
  created_at: string | null;
  sender: {
    id: number;
    name: string;
    mobile: string;
  };
}

export interface SupportTicket {
  id: number;
  category: SupportCategory;
  category_display: string;
  status: SupportStatus;
  status_display: string;
  priority: "low" | "normal" | "high" | "urgent";
  subject: string;
  created_at: string | null;
  last_message_at: string | null;
  closed_at: string | null;
  close_reason: string | null;
  messages?: SupportMessage[];
}