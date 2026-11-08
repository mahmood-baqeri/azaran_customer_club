// src/modules/factor_module/interface/factor.types.ts

export type FactorStatus = "pending" | "approved" | "rejected";

export interface Factor {
  id: number;
  invoice_number: string | null;
  status: FactorStatus;
  status_display: string;
  photo: string;
  amount: number | null;
  invoice_issue_at: string | null;
  shop_name: string | null;
  created_at: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
  
  seller?: {
    phone: string | null;
    address: string | null;
  };
  meterage?: {
    number_water_taps: number | null;
    number_connections: number | null;
    pipe_length: number | null;
  };
  owner?: {
    uuid: string;
    name: string;
    mobile: string;
  };
}

export interface FactorFormData {
  invoice_number: string;
  invoice_issue_at: Date | null;
  amount: number | null;
  number_water_taps: number | null;
  number_connections: number | null;
  pipe_length: number | null;
  shop_name: string;
  seller_phone: string;
  seller_address: string;
  photoFile: File | null;
  photoPreview: string | null;
}