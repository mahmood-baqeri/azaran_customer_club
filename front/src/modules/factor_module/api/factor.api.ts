// src/modules/factor_module/api/factor.api.ts

import { apiGET, apiPOST, apiDELETE } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { Factor } from "../interface/factor.types";

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export const factorApi = {
  create: (formData: FormData): Promise<ApiResponse<Factor>> =>
    apiPOST(`${BASE_URL}factors/create/`, formData, true),

  list: (): Promise<ApiResponse<Factor[]>> =>
    apiGET(`${BASE_URL}factors/list/`, {}, true),

  detail: (id: number): Promise<ApiResponse<Factor>> =>
    apiGET(`${BASE_URL}factors/${id}/`, {}, true),

  update: (id: number, formData: FormData): Promise<ApiResponse<Factor>> =>
    apiPOST(`${BASE_URL}factors/${id}/update/`, formData, true),

  deleteFactor: (id: number): Promise<ApiResponse<Record<string, never>>> =>
    apiDELETE(`${BASE_URL}factors/${id}/`, true),
};