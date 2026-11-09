// src/modules/review_module/hooks/use-review.ts

import { useCallback, useEffect, useState } from "react";
import { reviewRepository } from "../repository/review.repository";
import type { ReviewQuestion } from "../interface/review.types";

export const useReview = () => {
  const [questions, setQuestions] = useState<ReviewQuestion[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await reviewRepository.getQuestions();
      // فقط سوالاتی که کاربر به آن‌ها پاسخ نداده است را نمایش می‌دهیم
      setQuestions(data.filter(q => !q.is_answered));
    } catch (err) {
      console.error("[review] fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  return { questions, loading };
};