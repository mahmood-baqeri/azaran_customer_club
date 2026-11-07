// src/modules/project_module/screen/upload_attachments.screen.tsx

import { useState, useEffect, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useProjectDetail } from "../hooks/use-project-detail";
import { projectRepository } from "../repository/project.repository";
import { MyNotification } from "../../../shared/utils/notification";
import type { AttachmentType } from "../interface/project.types";
import { PROJECT_ROUTES } from "../routes";
import "../../../shared/styles/project.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import FileCard from "../components/FileCard";

/* -------------------------------------------------------------------------- */
/*                                 Constants                                  */
/* -------------------------------------------------------------------------- */

const UPLOAD_TYPES: { key: AttachmentType; title: string; help: string }[] = [
     { key: "exterior_view_building", title: "نمای خارجی ساختمان", help: "(تابلو پروژه با پلاک مشخص)" },
     { key: "azar_products_installed", title: "محصولات آذر نصب شده ", help: "(لوگو آذر خوانا باشد)" },
     { key: "azar_products_depot", title: "دپو محصولات آذر قبل از نصب ", help: "(حضور مجری در عکس)" },
];

const MAX_SIZE = 5 * 1024 * 1024;
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

/* -------------------------------------------------------------------------- */
/*                                  Helpers                                   */
/* -------------------------------------------------------------------------- */

function validateFile(file: File): boolean {
     if (!ALLOWED_TYPES.includes(file.type)) {
          MyNotification("خطا", "فقط فرمت‌های JPG، PNG و WEBP مجاز هستند.", "error");
          return false;
     }
     if (file.size > MAX_SIZE) {
          MyNotification("خطا", "حجم تصویر نباید بیشتر از ۵ مگابایت باشد.", "error");
          return false;
     }
     return true;
}

type FileState = { [key in AttachmentType]?: File };

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export default function UploadAttachmentsScreen() {
     const { id } = useParams<{ id: string }>();
     const projectId = id ? Number(id) : null;
     const navigate = useNavigate();

     const { project, loading, refresh } = useProjectDetail(projectId);

     /* ----------------------------- Derive state --------------------------- */
     // ✅ هر فایلی که قبلاً آپلود شده باشد = حالت ویرایش
     const isEditMode = (project?.attachments?.length ?? 0) > 0;

     /* ------------------------------- State -------------------------------- */
     const [files, setFiles] = useState<FileState>({});
     const [hasInvoice, setHasInvoice] = useState(false);
     const [checkedSelf, setCheckedSelf] = useState(false);
     const [submitting, setSubmitting] = useState(false);

     /* ------------------------------- Effects ------------------------------ */
     // ✅ ۱. اگر فاکتور از قبل وجود داشت، سوییچ را روشن کن
     useEffect(() => {
          if (project?.attachments?.some((a) => a.type === "Invoice")) {
               setHasInvoice(true);
          }
     }, [project]);

     // ✅ ۲. اگر در حالت ویرایش هستیم، چک‌باکس را خودکار تیک بزن
     useEffect(() => {
          if (isEditMode) {
               setCheckedSelf(true);
          }
     }, [isEditMode]);

     // پاک‌سازی ObjectURL ها در unmount
     useEffect(() => {
          return () => {
               Object.values(files).forEach((f) => {
                    if (f) URL.revokeObjectURL(URL.createObjectURL(f));
               });
          };
          // eslint-disable-next-line react-hooks/exhaustive-deps
     }, []);

     /* ------------------------------ Handlers ------------------------------ */
     const handleSelect = useCallback((type: AttachmentType, file: File | undefined) => {
          if (!file) return;
          if (!validateFile(file)) return;
          setFiles((prev) => ({ ...prev, [type]: file }));
     }, []);

     const handleRemove = useCallback((type: AttachmentType) => {
          setFiles((prev) => {
               const next = { ...prev };
               delete next[type];
               return next;
          });
     }, []);

     // حذف فایل موجود در سرور
     const handleDeleteExisting = async (attachId: number) => {
          if (!projectId) return;
          if (!window.confirm("آیا از حذف این تصویر مطمئن هستید؟")) return;

          try {
               await projectRepository.deleteAttachment(projectId, attachId);
               MyNotification("", "تصویر با موفقیت حذف شد", "success");
               refresh();
          } catch (err: unknown) {
               const msg = err instanceof Error ? err.message : "خطا در حذف تصویر";
               MyNotification("خطا", msg, "error");
          }
     };

     /* --------------------------- Guard: loading --------------------------- */
     if (loading || !project) return null;

     if (project.status !== "pending") {
          navigate(PROJECT_ROUTES.detail(project.id), { replace: true });
          return null;
     }

     /* --------------------------- Derived render --------------------------- */
     const existing = project.attachments || [];
     const existingByType = (type: AttachmentType) => existing.find((a) => a.type === type);

     const hasAllRequired = UPLOAD_TYPES.every(
          (t) => !!files[t.key] || !!existingByType(t.key)
     );
     const invoiceMissing = hasInvoice && !files.Invoice && !existingByType("Invoice");

     // ✅ ۳. checkedSelf فقط در حالت ثبت جدید اجباری است
     const selfCheckRequired = !isEditMode;
     const isSelfCheckedOk = selfCheckRequired ? checkedSelf : true;

     const canSubmit = hasAllRequired && !invoiceMissing && isSelfCheckedOk && !submitting;

     const hasNewFiles = Object.keys(files).length > 0;

     /* ------------------------------ Submit -------------------------------- */
     const handleSubmit = async () => {
          if (!canSubmit || !projectId) return;

          // ✅ ایراد ۱: اگر هیچ فایلی برای آپلود انتخاب نشده، خطا بده
          if (!hasNewFiles) {
               MyNotification("", "هیچ فایلی برای آپلود انتخاب نکرده‌اید", "warning");
               return;
          }


          setSubmitting(true);
          try {
               await projectRepository.uploadAttachmentsBatch(projectId, files);
               MyNotification("", "تصاویر با موفقیت ثبت شدند", "success");
               navigate(PROJECT_ROUTES.detail(projectId), { replace: true });
          } catch (err: unknown) {
               const msg = err instanceof Error ? err.message : "خطا در ثبت تصاویر";
               MyNotification("خطا", msg, "error");
          } finally {
               setSubmitting(false);
          }
     };

     /* ------------------------------- Render ------------------------------- */
     return (
          <>
               <Header title="تصاویر پروژه" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="display-grid">
                    <div className="proj-body">
                         <p className={`proj-error-title ${hasAllRequired ? "color-primary" : ""}`}>
                              بارگذاری حداقل سه تصویر الزامی است
                         </p>

                         <div style={{ display: "flex", flexDirection: "column", gap: 20, marginTop: 16 }}>
                              {UPLOAD_TYPES.map((item) => {
                                   const ex = existingByType(item.key);
                                   const newFile = files[item.key];
                                   const isUploaded = !!(ex || newFile);

                                   return (
                                        <div key={item.key} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                             <p className="mb-0">
                                                  <span className="fs-14 fw-600">{item.title}</span>
                                                  <span className="fs-11 text-dark opacity-50">{item.help}</span>
                                             </p>

                                             {!isUploaded ? (
                                                  <label className="project-label-upload-file">
                                                       <input
                                                            type="file"
                                                            accept="image/jpeg,image/png,image/webp"
                                                            hidden
                                                            onChange={(e) => {
                                                                 handleSelect(item.key, e.target.files?.[0]);
                                                                 e.target.value = "";
                                                            }}
                                                       />
                                                       <MyImage src={ICONS.upload_1} className="w__20" />
                                                       <span style={{ fontSize: 13, color: "#14306b", fontWeight: 400 }}>
                                                            آپلود عکس
                                                       </span>
                                                  </label>
                                             ) : (
                                                  <FileCard
                                                       name={newFile?.name || `${item.key}.jpg`}
                                                       sizeInBytes={newFile?.size ?? ex?.file_size}
                                                       status={ex ? ex.status : undefined}
                                                       onRemove={
                                                            newFile
                                                                 ? () => handleRemove(item.key)
                                                                 : ex && ex.status === "pending"
                                                                      ? () => handleDeleteExisting(ex.id)
                                                                      : undefined
                                                       }
                                                  />
                                             )}
                                        </div>
                                   );
                              })}
                         </div>

                         {/* سوییچ فاکتور */}
                         <div style={{ display: "flex", alignItems: "center", marginTop: 24 }}>
                              <label className="auth-switch ms-2">
                                   <input
                                        type="checkbox"
                                        checked={hasInvoice}
                                        onChange={(e) => {
                                             setHasInvoice(e.target.checked);
                                             if (!e.target.checked) handleRemove("Invoice");
                                        }}
                                   />
                                   <span className="slider" />
                              </label>
                              <label className="auth-label fw-500" style={{ margin: 0 }}>
                                   آیا فاکتور محصولات را دارید؟
                                   <small className="text-dark opacity-50">(اختیاری)</small>
                              </label>
                         </div>

                         {hasInvoice && (() => {
                              const ex = existingByType("Invoice");
                              const newFile = files.Invoice;
                              const isUploaded = !!(ex || newFile);

                              return (
                                   <div style={{ marginTop: 10 }}>
                                        {!isUploaded ? (
                                             <label className="project-label-upload-file">
                                                  <input
                                                       type="file"
                                                       accept="image/jpeg,image/png,image/webp"
                                                       hidden
                                                       onChange={(e) => {
                                                            handleSelect("Invoice", e.target.files?.[0]);
                                                            e.target.value = "";
                                                       }}
                                                  />
                                                  <span style={{ fontSize: 13, color: "#1e293b", fontWeight: 600 }}>
                                                       آپلود فاکتور
                                                  </span>
                                                  <MyImage src={ICONS.upload_1} className="w__20" />
                                             </label>
                                        ) : (
                                             <FileCard
                                                  name={newFile?.name || "Invoice.jpg"}
                                                  sizeInBytes={newFile?.size ?? ex?.file_size}
                                                  status={ex ? ex.status : undefined}
                                                  onRemove={
                                                       newFile
                                                            ? () => handleRemove("Invoice")
                                                            : ex && ex.status === "pending"
                                                                 ? () => handleDeleteExisting(ex.id)
                                                                 : undefined
                                                  }
                                             />
                                        )}
                                   </div>
                              );
                         })()}
                    </div>

                    <div>
                         <label
                              className="proj-checkbox-row"
                              style={{
                                   marginBottom: 24,
                                   opacity: isEditMode ? 0.7 : 1,
                                   cursor: isEditMode ? "not-allowed" : "pointer",
                              }}
                         >
                              <input
                                   type="checkbox"
                                   checked={checkedSelf}
                                   onChange={(e) => setCheckedSelf(e.target.checked)}
                                   disabled={isEditMode}
                              />
                              <span>این پروژه را خودم اجرا کرده‌ام و قبلا ثبت نشده است</span>
                         </label>

                         <div className="proj-sticky-bottom">
                              <button className="auth-btn" disabled={!canSubmit} onClick={handleSubmit}>
                                   {submitting ? "در حال ثبت..." : "ثبت تصاویر"}
                              </button>
                         </div>
                    </div>
               </div>
          </>
     );
}