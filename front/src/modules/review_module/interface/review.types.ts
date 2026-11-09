// src/modules/review_module/interface/review.types.ts

export type AnswerValue = "very_little" | "little" | "average" | "a_lot" | "very_much";

export interface ReviewQuestion {
  id: number;
  question: string;
  is_answered: boolean;
}

export interface SubmitReviewPayload {
  question_id: number;
  answer: AnswerValue;
}

export interface ApiResponse<T = Record<string, never>> {
  status: "Success" | "Error";
  message: string;
  data: T;
}