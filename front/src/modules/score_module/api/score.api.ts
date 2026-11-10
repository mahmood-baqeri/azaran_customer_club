// src/modules/score_module/api/score.api.ts

import { apiGET } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { ApiResponse, BalanceInfo, PaginatedLogs } from "../interface/score.types";

export const scoreApi = {
  getBalance: (): Promise<ApiResponse<BalanceInfo>> =>
    apiGET(`${BASE_URL}score/balance/`, {}, true),

  // ✅ اضافه شدن پارامترهای start_date و end_date
  getLogs: (params: { 
    direction?: string; 
    start_date?: string; 
    end_date?: string; 
    page?: number; 
    page_size?: number 
  }): Promise<ApiResponse<PaginatedLogs>> =>
    apiGET(`${BASE_URL}score/logs/`, params, true),
};