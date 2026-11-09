// src/modules/review_module/api/review.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { ApiResponse, ReviewQuestion, SubmitReviewPayload } from "../interface/review.types";

export const reviewApi = {
  getQuestions: (): Promise<ApiResponse<ReviewQuestion[]>> =>
    apiGET(`${BASE_URL}review/questions/`, {}, true),

  submitAnswers: (answers: SubmitReviewPayload[]): Promise<ApiResponse> =>
    apiPOST(`${BASE_URL}review/submit/`, { answers }, true),
};