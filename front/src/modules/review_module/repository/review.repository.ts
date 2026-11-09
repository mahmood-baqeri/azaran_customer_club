// src/modules/review_module/repository/review.repository.ts

import { reviewApi } from "../api/review.api";
import type { ReviewQuestion, SubmitReviewPayload } from "../interface/review.types";

export const reviewRepository = {
  async getQuestions(): Promise<ReviewQuestion[]> {
    const res = await reviewApi.getQuestions();
    return Array.isArray(res.data) ? res.data : [];
  },

  async submitAnswers(answers: SubmitReviewPayload[]): Promise<boolean> {
    const res = await reviewApi.submitAnswers(answers);
    if (res.status === "Error") throw new Error(res.message);
    return true;
  },
};