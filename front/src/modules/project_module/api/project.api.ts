// src/modules/project_module/api/project.api.ts

import { apiGET, apiPOST, apiDELETE } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { Project, CreateProjectPayload, Colleague, Attachment, AttachmentType } from "../interface/project.types";

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export const projectApi = {
  create: (payload: CreateProjectPayload): Promise<ApiResponse<Project>> =>
    apiPOST(`${BASE_URL}projects/create/`, payload, true),

  list: (): Promise<ApiResponse<Project[]>> =>
    apiGET(`${BASE_URL}projects/list/`, {}, true),

  detail: (id: number): Promise<ApiResponse<Project>> =>
    apiGET(`${BASE_URL}projects/${id}/`, {}, true),

  // ✅ اصلاح غلط املایی: project -> projects
  update: (id: number, payload: CreateProjectPayload): Promise<ApiResponse<Project>> =>
    apiPOST(`${BASE_URL}projects/${id}/update/`, payload, true),

  deleteProject: (id: number): Promise<ApiResponse<Record<string, never>>> =>
    apiDELETE(`${BASE_URL}projects/${id}/`, true),

  uploadAttachment: (projectId: number, type: AttachmentType, file: File): Promise<ApiResponse<Attachment>> => {
    const fd = new FormData();
    fd.append("type", type);
    fd.append("file", file);
    return apiPOST(`${BASE_URL}projects/${projectId}/attachments/`, fd, true);
  },

  // ✅ این متد از قبل بود، اما در ریپازیتوری استفاده نشده بود
  deleteAttachment: (
    projectId: number,
    attachmentId: number,
  ): Promise<ApiResponse<Record<string, never>>> =>
    apiDELETE(`${BASE_URL}projects/${projectId}/attachments/${attachmentId}/`, true),

  addColleague: (projectId: number, mobile: string, percent: number): Promise<ApiResponse<Colleague>> =>
    apiPOST(`${BASE_URL}projects/${projectId}/colleagues/`, { mobile, percent }, true),

  toggleColleague: (projectId: number, colleagueId: number): Promise<ApiResponse<Colleague>> =>
    apiPOST(`${BASE_URL}projects/${projectId}/colleagues/${colleagueId}/toggle/`, {}, true),

  deleteColleague: (projectId: number, colleagueId: number): Promise<ApiResponse<Record<string, never>>> =>
    apiDELETE(`${BASE_URL}projects/${projectId}/colleagues/${colleagueId}/`, true),
  
  
   // ✅ متد جدید: آپلود یکجای همه فایل‌ها
  uploadAttachmentsBatch: (
    projectId: number,
    files: { [key in AttachmentType]?: File }
  ): Promise<ApiResponse<Record<string, never>>> => {
    const fd = new FormData();
    (Object.entries(files) as [AttachmentType, File | undefined][]).forEach(([key, file]) => {
      if (file) fd.append(key, file);
    });
    return apiPOST(`${BASE_URL}projects/${projectId}/attachments/batch/`, fd, true);
  },
  
};