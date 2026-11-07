// src/modules/faq_module/hooks/use-categories.ts
import {  useEffect, useState } from "react";
import { faqRepository } from "../repository/faq.repository";
import type { Category } from "../interface/faq.types";

export const useCategories = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  useEffect(() => {
    faqRepository.getCategories().then(setCategories);
  }, []);
  return { categories };
};