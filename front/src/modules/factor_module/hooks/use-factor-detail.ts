// src/modules/factor_module/hooks/use-factor-detail.ts
import { useCallback, useEffect, useState } from "react";
import { factorRepository } from "../repository/factor.repository";
import type { Factor } from "../interface/factor.types";

export const useFactorDetail = (id: number | null) => {
  const [factor, setFactor] = useState<Factor | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setFactor(await factorRepository.detail(id));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { refresh(); }, [refresh]);

  return { factor, loading, refresh };
};