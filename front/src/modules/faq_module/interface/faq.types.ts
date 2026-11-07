// src/modules/faq_module/interface/faq.types.ts

export type FaqFilterType = "newest" | "most_answered" | "my_questions";

export interface Category {
  id: number;
  title: string;
}

export interface AnswerUser {
  id: number | null;
  name: string;
  avatar?: string | null;
}

export interface Answer {
  id: number;
  answer: string;
  likes_count: number;
  dislikes_count: number;
  my_reaction: "like" | "dislike" | null;
  created_at: string | null;
  user: AnswerUser;
}

export interface FAQ {
  id: number;
  question: string;
  created_at: string | null;
  category: { id: number; title: string };
  user: AnswerUser;
  answers_count: number;
  answers?: Answer[];
}