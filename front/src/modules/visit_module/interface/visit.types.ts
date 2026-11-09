// src/modules/visit_module/interface/visit.types.ts

export type VisitStatus = "pending" | "approved" | "rejected";

export interface AvailableVisit {
  id: number;
  date: string;
  capacity: number | null;
  remaining_capacity: number | null;
  is_full: boolean;
}

export interface Companion {
  name: string;
  family: string;
  mobile: string;
}

export interface RequestVisit {
  id: number;
  status: VisitStatus;
  status_display: string;
  created_at: string | null;
  approved_at: string | null;
  rejected_at: string | null;
  rejection_reason: string | null;
  have_companion: boolean;
  companion: Companion | null;
  visit: {
    id: number;
    date: string; // ISO Date String
  };
}