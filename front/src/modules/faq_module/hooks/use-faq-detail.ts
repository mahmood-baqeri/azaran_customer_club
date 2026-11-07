// src/modules/faq_module/hooks/use-faq-detail.ts
import { useCallback, useEffect, useState } from "react";
import { faqRepository } from "../repository/faq.repository";
import type { FAQ } from "../interface/faq.types";

export const useFaqDetail = (id: number | null) => {
  const [faq, setFaq] = useState<FAQ | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setFaq(await faqRepository.getFaqDetail(id));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { faq, loading, refresh, setFaq };
};