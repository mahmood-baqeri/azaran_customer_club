// src/modules/factor_module/hooks/use-factors.ts
import { useCallback, useEffect, useState } from "react";
import { factorRepository } from "../repository/factor.repository";
import type { Factor } from "../interface/factor.types";

export const useFactors = () => {
  const [factors, setFactors] = useState<Factor[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setFactors(await factorRepository.list());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return { factors, loading, refresh };
};