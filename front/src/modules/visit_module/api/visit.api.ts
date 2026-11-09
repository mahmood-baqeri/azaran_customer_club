// src/modules/visit_module/api/visit.api.ts

import { apiGET, apiPOST, apiDELETE } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { AvailableVisit, RequestVisit } from "../interface/visit.types";

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export const visitApi = {
  listAvailable: (): Promise<ApiResponse<AvailableVisit[]>> =>
    apiGET(`${BASE_URL}visit/list-available/`, {}, true),

  create: (payload: {
    visit_id: number;
    have_companion: boolean;
    companion_name?: string;
    companion_family?: string;
    companion_mobile?: string;
  }): Promise<ApiResponse<RequestVisit>> =>
    apiPOST(`${BASE_URL}visit/create/`, payload, true),

  list: (): Promise<ApiResponse<RequestVisit[]>> =>
    apiGET(`${BASE_URL}visit/list/`, {}, true),

  detail: (id: number): Promise<ApiResponse<RequestVisit>> =>
    apiGET(`${BASE_URL}visit/${id}/`, {}, true),

  delete: (id: number): Promise<ApiResponse<Record<string, never>>> =>
    apiDELETE(`${BASE_URL}visit/${id}/`, true),
};