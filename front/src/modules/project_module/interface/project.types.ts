// src/modules/project_module/interface/project.types.ts

export type ProjectType = "water" | "gas";
export type ProjectStatus = "pending" | "approved" | "rejected";

export interface Colleague {
  id: number;
  user_uuid: string;
  user_mobile: string;
  user_name: string;
  avatar: string;
  percent: number;
  is_active: boolean;
}

export type AttachmentType =
  | "exterior_view_building"
  | "azar_products_installed"
  | "azar_products_depot"
  | "Invoice";

export interface Attachment {
  id: number;
  type: AttachmentType;
  type_display: string;
  file: string;
  file_size: number;
  status: ProjectStatus; 
  status_display: string;
}

export interface Project { 
  id: number;
  type: ProjectType;
  type_display: string;
  title: string;
  status: ProjectStatus;
  status_display: string;
  completion_at: string | null;
  address: string | null;
  owner_mobile: string | null;
  unit_count: number | null;
  created_at: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
  
  meterage?: {
    number_water_taps: number | null;
    number_gas_taps: number | null;
    number_connections: number | null;
    pipe_length: number | null;
  };
  owner?: {
    uuid: string;
    name: string;
    mobile: string;
  };
  colleagues?: Colleague[];
  attachments?: Attachment[];
}

export interface CreateProjectPayload {
  type: ProjectType;
  title: string;
  address?: string;
  owner_mobile?: string;
  unit_count?: number;
  number_water_taps?: number;
  number_gas_taps?: number;
  number_connections?: number;
  pipe_length?: number;
  completion_at?: Date | null;
}