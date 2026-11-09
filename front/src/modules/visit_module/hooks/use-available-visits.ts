// src/modules/visit_module/hooks/use-available-visits.ts

import { useCallback, useEffect, useState } from "react";
import { visitRepository } from "../repository/visit.repository";
import type { AvailableVisit } from "../interface/visit.types";

export const useAvailableVisits = () => {
  const [visits, setVisits] = useState<AvailableVisit[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setVisits(await visitRepository.listAvailable());
    } catch (err) {
      console.error("[available visits] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { visits, loading, refresh };
};