// src/modules/learn_module/api/learn.api.ts

import { apiGET } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { ApiResponse, LearnItem } from "../interface/learn.types";

export const learnApi = {
  list: (size?: string): Promise<ApiResponse<LearnItem[]>> => {
    const q: Record<string, unknown> = {};
    if (size) q.size = size;
    return apiGET(`${BASE_URL}learn/list/`, q, true);
  },

  detail: (id: number): Promise<ApiResponse<LearnItem>> =>
    apiGET(`${BASE_URL}learn/${id}/`, {}, true),
};