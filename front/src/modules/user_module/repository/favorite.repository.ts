// src/modules/user_module/repository/favorite.repository.ts

import { favoriteApi, type SubmitFavoriteAnswerInput } from "../api/favorite.api";
import type { FavoriteQuestion } from "../interface/user.types";

export const favoriteRepository = {
  async listQuestions(): Promise<FavoriteQuestion[]> {
    const res = await favoriteApi.listQuestions();
    return res.data;
  },

  async submitAnswer(input: SubmitFavoriteAnswerInput): Promise<{
    id: number;
    question_id: number;
    answer: string;
    answer_display: string;
  }> {
    const res = await favoriteApi.submitAnswer(input);
    return res.data;
  },
};