/* eslint-disable @typescript-eslint/no-unused-vars */
// src/modules/visit_module/hooks/use-visit-detail.ts

import { useCallback, useEffect, useState } from "react";
import { visitRepository } from "../repository/visit.repository";
import type { RequestVisit } from "../interface/visit.types";

export const useVisitDetail = (id: number | null) => {
  const [visit, setVisit] = useState<RequestVisit | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setVisit(await visitRepository.detail(id));
    } catch (err) {
      setVisit(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { visit, loading, refresh };
};