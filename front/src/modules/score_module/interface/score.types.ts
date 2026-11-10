// src/modules/score_module/interface/score.types.ts

export type Direction = "earned" | "spent";

export interface ScoreLog {
  id: number;
  code: string;
  code_display: string;
  direction: Direction;
  amount: number;
  balance_before: number;
  balance_after: number;
  reason: string | null;
  created_at: string;
}

export interface PaginatedLogs {
  total: number;
  page: number;
  page_size: number;
  items: ScoreLog[];
}

export interface BalanceInfo {
  current_balance: number;
  total_earned: number;
  total_spent: number;
}

export interface FilterState {
  direction: Direction | "all";
  startDate: Date | null;
  endDate: Date | null;
}

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}