// src/modules/user_module/api/favorite.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { FavoriteQuestion, FavoriteAnswerValue } from "../interface/user.types";

export interface FavoriteQuestionsResponse {
  status: "Success" | "Error";
  message: string;
  data: FavoriteQuestion[];
}

export interface FavoriteAnswerResponse {
  status: "Success" | "Error";
  message: string;
  data: {
    id: number;
    question_id: number;
    answer: FavoriteAnswerValue;
    answer_display: string;
  };
}

export interface SubmitFavoriteAnswerInput {
  question_id: number;
  answer: FavoriteAnswerValue;
}

export const favoriteApi = {
  listQuestions: (): Promise<FavoriteQuestionsResponse> =>
    apiGET(`${BASE_URL}user/favorite-questions/`, {}, true),

  submitAnswer: (input: SubmitFavoriteAnswerInput): Promise<FavoriteAnswerResponse> =>
    apiPOST(`${BASE_URL}user/favorite-questions/answer/`, input, true),
};