// src/modules/learn_module/hooks/use-learns.ts

import { useCallback, useEffect, useState } from "react";
import { learnRepository } from "../repository/learn.repository";
import type { LearnItem } from "../interface/learn.types";

export const useLearns = (size?: string) => {
  const [learns, setLearns] = useState<LearnItem[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setLearns(await learnRepository.list(size));
    } catch (err) {
      console.error("[learns] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, [size]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { learns, loading, refresh };
};