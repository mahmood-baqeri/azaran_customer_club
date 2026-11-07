// src/modules/faq_module/hooks/use-create-action.ts
import { useState } from "react";
import { faqRepository } from "../repository/faq.repository";
import { MyNotification } from "../../../shared/utils/notification";

export const useCreateAction = () => {
  const [submitting, setSubmitting] = useState(false);

  const askQuestion = async (question: string, categoryId: number) => {
    setSubmitting(true);
    try {
      const faq = await faqRepository.createFaq({ question, category_id: categoryId });
      if (faq) MyNotification("", "پرسش شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود.", "success");
      return !!faq;
    } catch {
      MyNotification("خطا", "خطا در ثبت پرسش", "error");
      return false;
    } finally {
      setSubmitting(false);
    }
  };

  const submitAnswer = async (faqId: number, answer: string) => {
    setSubmitting(true);
    try {
      const success = await faqRepository.createAnswer(faqId, answer);
      if (success) MyNotification("", "پاسخ شما ثبت شد.", "success");
      return success;
    } catch {
      MyNotification("خطا", "خطا در ثبت پاسخ", "error");
      return false;
    } finally {
      setSubmitting(false);
    }
  };

  return { submitting, askQuestion, submitAnswer };
};