// src/modules/gallery_module/api/gallery.api.ts

import { apiGET, apiPOST, apiDELETE } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { Gallery, LikeResponse } from "../interface/gallery.types";

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export const galleryApi = {
  create: (formData: FormData): Promise<ApiResponse<Gallery>> => apiPOST(`${BASE_URL}gallery/create/`, formData, true),

  list: (filterType: string): Promise<ApiResponse<Gallery[]>> => apiGET(`${BASE_URL}gallery/list/`, { filter_type: filterType }, true),

  detail: (id: number): Promise<ApiResponse<Gallery>> => apiGET(`${BASE_URL}gallery/${id}/`, {}, true),
  
  delete: (id: number): Promise<ApiResponse<Record<string, never>>> => apiDELETE(`${BASE_URL}gallery/${id}/`, true),

  like: (id: number): Promise<ApiResponse<LikeResponse>> => apiPOST(`${BASE_URL}gallery/${id}/like/`, {}, true),
};