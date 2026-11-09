// src/modules/visit_module/hooks/use-visits.ts

import { useCallback, useEffect, useState } from "react";
import { visitRepository } from "../repository/visit.repository";
import type { RequestVisit } from "../interface/visit.types";

export const useVisits = () => {
  const [visits, setVisits] = useState<RequestVisit[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setVisits(await visitRepository.list());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { visits, loading, refresh };
};