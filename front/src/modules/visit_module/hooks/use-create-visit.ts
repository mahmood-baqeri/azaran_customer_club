// src/modules/visit_module/hooks/use-create-visit.ts

import { useState } from "react";
import { visitRepository } from "../repository/visit.repository";
import { MyNotification } from "../../../shared/utils/notification";

export const useCreateVisit = () => {
  const [submitting, setSubmitting] = useState(false);

  const createVisit = async (payload: Parameters<typeof visitRepository.create>[0]): Promise<boolean> => {
    setSubmitting(true);
    try {
      await visitRepository.create(payload);
      MyNotification("", "درخواست بازدید شما با موفقیت ثبت شد", "success");
      return true;
    } catch (err: unknown) {
      let msg = "خطا در ثبت درخواست";
      if (err instanceof Error) msg = err.message;
      MyNotification("خطا", msg, "error");
      return false;
    } finally {
      setSubmitting(false);
    }
  };

  return { createVisit, submitting };
};