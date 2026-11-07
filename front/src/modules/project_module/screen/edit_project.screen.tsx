// src/modules/project_module/screen/edit_project.screen.tsx

import { useState, useEffect, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import Header from "../../../app/layouts/header";
import { projectRepository } from "../repository/project.repository";
import { MyNotification } from "../../../shared/utils/notification";
import ProjectForm, { type ProjectFormData } from "../components/ProjectForm";
import { PROJECT_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import type { Project, CreateProjectPayload } from "../interface/project.types"; // ✅ اضافه شدن تایپ‌ها
import "../../../shared/styles/project.css";

export default function EditProjectScreen() {
     const { id } = useParams<{ id: string }>();
     const projectId = id ? Number(id) : null;
     const navigate = useNavigate();

     const [loading, setLoading] = useState(true);
     const [submitting, setSubmitting] = useState(false);
     // ✅ جایگزینی any با Project | null
     const [initialData, setInitialData] = useState<Project | null>(null);
     const [formData, setFormData] = useState<ProjectFormData | null>(null);
     const [isValid, setIsValid] = useState(false);

     useEffect(() => {
          if (!projectId) return;
          projectRepository
               .detail(projectId)
               .then((p) => {
                    if (p) setInitialData(p);
               })
               .finally(() => setLoading(false));
     }, [projectId]);

     const handleFormChange = useCallback((data: ProjectFormData, valid: boolean) => {
          setFormData(data);
          setIsValid(valid);
     }, []);

     const handleSave = async () => {
          if (!formData || !isValid || !projectId) return;
          setSubmitting(true);
          try {
               // ✅ استفاده از تایپ CreateProjectPayload و پاس دادن مستقیم Date
               const payload: CreateProjectPayload = {
                    type: formData.type,
                    title: `پروژه ${formData.type === "water" ? "آبی" : "گازی"}`,
                    address: formData.address.trim(),
                    owner_mobile: formData.owner_mobile ? convertPersianToEnglish(formData.owner_mobile) : undefined,
                    unit_count: formData.unit_count ? Number(formData.unit_count) : undefined,
                    number_water_taps: formData.number_water_taps ? Number(formData.number_water_taps) : undefined,
                    number_gas_taps: formData.number_gas_taps ? Number(formData.number_gas_taps) : undefined,
                    number_connections: formData.number_connections ? Number(formData.number_connections) : undefined,
                    pipe_length: formData.pipe_length ? Number(formData.pipe_length) : undefined,
                    completion_at: formData.completion_at, // تاریخ به صورت Date پاس داده می‌شود
               };

               await projectRepository.update(projectId, payload);
               MyNotification("", "تغییرات با موفقیت ذخیره شد", "success");
               navigate(PROJECT_ROUTES.detail(projectId));
          } catch (err: unknown) {
               let msg = "خطا در ویرایش اطلاعات";
               if (axios.isAxiosError(err) && err.response?.data?.message) {
                    msg = err.response.data.message;
               }
               MyNotification("خطا", msg, "error");
          } finally {
               setSubmitting(false);
          }
     };

     if (loading) return <div className="text-center mt-5">در حال بارگذاری...</div>;

     return (
          <>
               <Header title="ویرایش پروژه" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <ProjectForm initialData={initialData} onChange={handleFormChange} />

               <div className="proj-sticky-bottom mb-4">
                    <button className="auth-btn" onClick={handleSave} disabled={submitting || !isValid}>
                         {submitting ? "در حال ذخیره..." : "ذخیره تغییرات"}
                    </button>
               </div>
          </>
     );
}