// src/modules/faq_module/hooks/use-faqs.ts
import { useCallback, useEffect, useState } from "react";
import { faqRepository } from "../repository/faq.repository";
import type { FAQ, FaqFilterType } from "../interface/faq.types";

export const useFaqs = (categoryId?: number, sort: FaqFilterType = "newest") => {
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loading, setLoading] = useState(true);

 const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setFaqs(await faqRepository.getFaqs(categoryId, sort)); // ✅ پاس دادن sort
    } finally {
      setLoading(false);
    }
  }, [categoryId, sort]); // ✅ sort به dependencyه

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { faqs, loading, refresh };
};