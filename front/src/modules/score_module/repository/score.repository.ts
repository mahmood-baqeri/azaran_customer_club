// src/modules/score_module/repository/score.repository.ts

import { scoreApi } from "../api/score.api";
import type { BalanceInfo, PaginatedLogs } from "../interface/score.types";

export const scoreRepository = {
  async getBalance(): Promise<BalanceInfo | null> {
    const res = await scoreApi.getBalance();
    return res.data ?? null;
  },

  async getLogs(params: { 
    direction?: string; 
    start_date?: string; 
    end_date?: string; 
    page?: number; 
    page_size?: number 
  }): Promise<PaginatedLogs | null> {
    const res = await scoreApi.getLogs(params);
    return res.data ?? null;
  },
};