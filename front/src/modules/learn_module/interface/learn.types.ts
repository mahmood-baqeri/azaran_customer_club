// src/modules/learn_module/interface/learn.types.ts

export type LearnSize = "short" | "full";

export interface LearnItem {
  id: number;
  title: string;
  sub_text: string | null;
  photo: string | null;
  size: LearnSize;
  size_display: string;
  time: number | null;
  created_at: string | null;
  
  // فقط در حالت جزئیات
  caption?: string | null;
  full_text?: string | null;
}

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}