// src/modules/project_module/hooks/use-create-project.ts

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { projectRepository } from "../repository/project.repository";
import type { CreateProjectPayload } from "../interface/project.types";
import { MyNotification } from "../../../shared/utils/notification";
import { PROJECT_ROUTES } from "../routes";

export const useCreateProject = () => {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  const createProject = async (payload: CreateProjectPayload) => {
    setSubmitting(true);
    try {
      const project = await projectRepository.create(payload);
      if (project) {
        MyNotification("", "پروژه با موفقیت ثبت شد. لطفاً تصاویر را بارگذاری کنید.", "success");
        navigate(PROJECT_ROUTES.upload(project.id));
      }
    } catch (err: unknown) {
      let msg = "خطا در ثبت پروژه";
      if (axios.isAxiosError(err) && err.response?.data?.message) {
        msg = err.response.data.message;
      }
      MyNotification("خطا", msg, "error");
    } finally {
      setSubmitting(false);
    }
  };

  return { createProject, submitting };
};