// src/modules/project_module/screen/create_project.screen.tsx

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Header from "../../../app/layouts/header";
import { projectRepository } from "../repository/project.repository";
import { MyNotification } from "../../../shared/utils/notification";
import ColleaguesModal from "../components/ColleaguesModal";
import { PROJECT_ROUTES } from "../routes";
import { getCookie, setCookie } from "../../../shared/hooks/use-cookie";
import ProjectForm, { type ProjectFormData } from "../components/ProjectForm";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import type { Project, CreateProjectPayload } from "../interface/project.types";
import "../../../shared/styles/project.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

const COOKIE_NAME = "draft_project_id";

export default function CreateProjectScreen() {
     const navigate = useNavigate();
     const [loading, setLoading] = useState(true);
     const [submitting, setSubmitting] = useState(false);

     const [savedProjectId, setSavedProjectId] = useState<number | null>(null);
     const [showColleagues, setShowColleagues] = useState(false);

     // ✅ جایگزینی any با Project | null
     const [initialData, setInitialData] = useState<Project | null>(null);
     const [formData, setFormData] = useState<ProjectFormData | null>(null);
     const [isValid, setIsValid] = useState(false);

     // ۱. بررسی کوکی در هنگام رفرش
     useEffect(() => {
          const cookieVal = getCookie(COOKIE_NAME);
          if (cookieVal) {
               const id = Number(cookieVal);
               if (!isNaN(id)) {
                    setSavedProjectId(id);
                    projectRepository
                         .detail(id)
                         .then((p) => {
                              if (p) setInitialData(p);
                         })
                         .finally(() => setLoading(false));
                    return;
               }
          }
          setLoading(false);
     }, []);

     const handleFormChange = useCallback((data: ProjectFormData, valid: boolean) => {
          setFormData(data);
          setIsValid(valid);
     }, []);

     const handleSave = async () => {
          if (!formData || !isValid) return;
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

               if (savedProjectId) {
                    // ویرایش پیش‌نویس
                    await projectRepository.update(savedProjectId, payload);
                    MyNotification("", "تغییرات با موفقیت ذخیره شد", "success");
               } else {
                    // ثبت جدید
                    const project = await projectRepository.create(payload);
                    if (project) {
                         setSavedProjectId(project.id);
                         setCookie(COOKIE_NAME, String(project.id), 5); // ✅ ست کردن کوکی ۵ دقیقه‌ای
                         MyNotification("", "فاکتور ثبت شد. اکنون می‌توانید همکار اضافه کنید یا تصاویر را بارگذاری نمایید.", "success");
                    }
               }
          } catch (err: unknown) {
               let msg = "خطا در ثبت اطلاعات";
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
               <Header title={savedProjectId ? "ویرایش پروژه" : "ثبت پروژه"} showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               {savedProjectId && (
                    <div className="proj-body" style={{ paddingBottom: 0 }}>
                         <div className="proj-success-banner mt-3">
                              ✅ اطلاعات ذخیره شده است. می‌توانید ویرایش کنید یا تصاویر را بارگذاری نمایید.
                         </div>
                    </div>
               )}

               <ProjectForm initialData={initialData} onChange={handleFormChange} />

               <label htmlFor="" className="fs-12">همکاران این پروژه (اختیاری)</label>
               <div className="proj-body mb-5">
                    <button
                         disabled={savedProjectId ? false : true}
                         className="proj-add-colleague-btn mb-3"
                         onClick={() => setShowColleagues(true)}
                         style={{ border: "1.5px dashed #14306b", color: "#14306b" }}
                    >
                         <MyImage src={ICONS.user_add} className="w__20 " />

                         <span className="mt-1"> افزودن همکاران</span>
                    </button>
               </div>

               <div className="proj-sticky-bottom mb-4" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {savedProjectId ? (
                         <>
                              <button
                                   className="project-btn"
                                   onClick={handleSave}
                                   disabled={submitting || !isValid}
                                   style={{ background: "#fff", color: "#14306b", border: "1.5px solid #14306b" }}
                              >
                                   {submitting ? "در حال ذخیره..." : "ذخیره تغییرات"}
                              </button>
                              <button className="project-btn" onClick={() => navigate(PROJECT_ROUTES.detail(savedProjectId))}>
                                   بارگذاری تصاویر
                              </button>
                         </>
                    ) : (
                         <button className="project-btn" onClick={handleSave} disabled={submitting || !isValid}>
                              {submitting ? "در حال ثبت..." : "ثبت پروژه"}
                         </button>
                    )}
               </div>

               {savedProjectId && (
                    <ColleaguesModal isOpen={showColleagues} onClose={() => setShowColleagues(false)} projectId={savedProjectId} />
               )}
          </>
     );
}