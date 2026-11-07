// src/modules/faq_module/api/faq.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { Category, FAQ, Answer, FaqFilterType } from "../interface/faq.types"; // ✅ Answer اضافه شد

export interface ApiListResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T[];
}

export interface ApiItemResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}

export const faqApi = {
  getCategories: (): Promise<ApiListResponse<Category>> =>
    apiGET(`${BASE_URL}faq/categories/`, {}, true),

 getFaqs: (categoryId?: number, sort?: FaqFilterType): Promise<ApiListResponse<FAQ>> => {
    const q: Record<string, unknown> = {};
    if (categoryId) q.category_id = categoryId;
    if (sort) q.sort = sort; // ✅ اضافه شد
    return apiGET(`${BASE_URL}faq/`, q, true);
  },

  getFaqDetail: (id: number): Promise<ApiItemResponse<FAQ>> =>
    apiGET(`${BASE_URL}faq/${id}/`, {}, true),

  createFaq: (payload: { question: string; category_id: number }): Promise<ApiItemResponse<FAQ>> =>
    apiPOST(`${BASE_URL}faq/`, payload, true),

  // ✅ جایگزینی any با Answer
  createAnswer: (faqId: number, answer: string): Promise<ApiItemResponse<Answer>> =>
    apiPOST(`${BASE_URL}faq/${faqId}/answers/`, { answer }, true),

  // ✅ جایگزینی any با Answer
  reactToAnswer: (answerId: number, reaction: "like" | "dislike" | null): Promise<ApiItemResponse<Answer>> =>
    apiPOST(`${BASE_URL}faq/answers/${answerId}/react/`, { reaction }, true),
};