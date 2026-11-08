// src/modules/support_module/api/support.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { SupportTicket } from "../interface/support.types";

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export const supportApi = {
  createTicket: (formData: FormData): Promise<ApiResponse<SupportTicket>> =>
    apiPOST(`${BASE_URL}support/create/`, formData, true),

  listTickets: (): Promise<ApiResponse<SupportTicket[]>> =>
    apiGET(`${BASE_URL}support/list/`, {}, true),

  getTicket: (id: number): Promise<ApiResponse<SupportTicket>> =>
    apiGET(`${BASE_URL}support/${id}/`, {}, true),
};