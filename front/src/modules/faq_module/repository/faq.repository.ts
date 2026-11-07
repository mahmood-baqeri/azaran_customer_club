// src/modules/faq_module/repository/faq.repository.ts

import { faqApi } from "../api/faq.api";
import type { Category, FAQ, FaqFilterType } from "../interface/faq.types";

export const faqRepository = {
  async getCategories(): Promise<Category[]> {
    const res = await faqApi.getCategories();
    return Array.isArray(res.data) ? res.data : [];
  },

async getFaqs(categoryId?: number, sort?: FaqFilterType): Promise<FAQ[]> {
    const res = await faqApi.getFaqs(categoryId, sort);
    return Array.isArray(res.data) ? res.data : [];
  },

  async getFaqDetail(id: number): Promise<FAQ | null> {
    const res = await faqApi.getFaqDetail(id);
    return res.data ?? null;
  },

  async createFaq(payload: { question: string; category_id: number }): Promise<FAQ | null> {
    const res = await faqApi.createFaq(payload);
    return res.data ?? null;
  },
  
  async createAnswer(faqId: number, answer: string): Promise<boolean> {
    const res = await faqApi.createAnswer(faqId, answer);
    return res.status === "Success";
  },

  async reactToAnswer(answerId: number, reaction: "like" | "dislike" | null): Promise<boolean> {
    const res = await faqApi.reactToAnswer(answerId, reaction);
    return res.status === "Success";
  }
};