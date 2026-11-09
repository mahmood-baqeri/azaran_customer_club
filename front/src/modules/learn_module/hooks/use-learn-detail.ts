// src/modules/learn_module/hooks/use-learn-detail.ts

import { useCallback, useEffect, useState } from "react";
import { learnRepository } from "../repository/learn.repository";
import type { LearnItem } from "../interface/learn.types";

export const useLearnDetail = (id: number | null) => {
  const [learn, setLearn] = useState<LearnItem | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setLearn(await learnRepository.detail(id));
    } catch (err) {
      console.error("[learn detail] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { learn, loading };
};