/* eslint-disable react-refresh/only-export-components */
// front/src/modules/profile_module/components/ProfileForms.tsx

import { useMemo, useRef, useState } from "react";
import { useCities, useProvinces } from "../../settings_module/hooks/use-locations";
import SelectElement, { type Option } from "../../../shared/tools/select";
import { PersianDatePicker } from "../../../shared/utils/persianDatePicker";
import { MyNotification } from "../../../shared/utils/notification";
import type { JobCertificateType, UserMe } from "../../user_module/interface/user.types";
import { FaCloudUploadAlt, FaFileAlt, FaFileImage, FaFilePdf, FaFileWord } from "react-icons/fa";
import { getErrorMessage } from "../../../shared/api/errors";
import { certificateRepository } from "../repository/certificate.repository";

// ============================================================
// Types
// ============================================================
export interface ProfileFormState {
     firstname: string;
     lastname: string;
     gender: "male" | "female" | "";
     mobile: string;
     birth_day: Date | null;
     national_code: string;
     address: string;
     post_code: string;
     job_title: string;
     company_name: string;
     province: Option | null;
     city: Option | null;
}

export const EMPTY_FORM: ProfileFormState = {
     firstname: "",
     lastname: "",
     gender: "",
     mobile: "",
     birth_day: null,
     national_code: "",
     address: "",
     post_code: "",
     job_title: "",
     company_name: "",
     province: null,
     city: null,
};

// تابع کمکی برای تبدیل خروجی فرم به دیتای ارسالی به سرور
export const mapFormToApiPayload = (form: ProfileFormState) => ({
     firstname: form.firstname,
     lastname: form.lastname,
     gender: form.gender === "" ? undefined : form.gender,
     mobile: form.mobile || undefined,
     birth_day: form.birth_day ? form.birth_day.toISOString().split("T")[0] : undefined,
     national_code: form.national_code || undefined,
     address: form.address || undefined,
     post_code: form.post_code || undefined,
     job_title: form.job_title || undefined,
     company_name: form.company_name || undefined,
     province_id: form.province ? Number(form.province.value) : null,
     city_id: form.city ? Number(form.city.value) : null,
});

// ============================================================
// Shared Input Component
// ============================================================
export const EditInput = ({ label, value, onChange, ltr, type = "text", placeholder }: {
     label: string;
     value: string;
     onChange: (v: string) => void;
     ltr?: boolean;
     type?: string;
     placeholder?: string;
}) => (
     <div style={{ marginBottom: 10 }}>
          <div className="auth-label" style={{ fontSize: 12 }}>{label}</div>
          <div className="auth-field" style={{ marginBottom: 0 }}>
               <input
                    type={type}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder || ""}
                    dir={ltr ? "ltr" : "rtl"}
                    style={{ paddingRight: 16, paddingLeft: 16, textAlign: ltr ? "left" : "right" }}
               />
          </div>
     </div>
);

// ============================================================
// 1. Personal Form
// ============================================================
export const PersonalForm = ({ form, update }: { form: ProfileFormState, update: <K extends keyof ProfileFormState>(k: K, v: ProfileFormState[K]) => void }) => {
     return (
          <>
               <div className="auth-form-row cols-2">
                    <EditInput label="نام" value={form.firstname} onChange={(v) => update("firstname", v)} />
                    <EditInput label="نام خانوادگی" value={form.lastname} onChange={(v) => update("lastname", v)} />
               </div>
               <div className="auth-form-row cols-2">
                    <EditInput label="کد ملی" value={form.national_code} onChange={(v) => update("national_code", v)} ltr />

                    <div style={{ marginBottom: 10 }}>
                         <div className="auth-label" style={{ fontSize: 12 }}>جنسیت</div>
                         <div className="auth-select">
                              <select value={form.gender} onChange={(e) => update("gender", e.target.value as ProfileFormState["gender"])}>
                                   <option value="">انتخاب کنید</option>
                                   <option value="male">مرد</option>
                                   <option value="female">زن</option>
                              </select>
                         </div>
                    </div>
               </div>
          </>
     );
};

// ============================================================
// 2. Birth Day Form
// ============================================================
export const BirthDayForm = ({ form, update }: { form: ProfileFormState, update: <K extends keyof ProfileFormState>(k: K, v: ProfileFormState[K]) => void }) => {
     return (
          <>
               <div className="auth-form-row cols-1">
                    <PersianDatePicker value={form.birth_day} onChange={(d) => update("birth_day", d)} placeholder="انتخاب تاریخ تولد" />
               </div>
          </>
     );
};

// ============================================================
// 2. Job Info Form (فرم قبلی - بعدا کامل میشه)
// ============================================================
export const JobInfoForm = ({ form, update }: { form: ProfileFormState, update: <K extends keyof ProfileFormState>(k: K, v: ProfileFormState[K]) => void }) => {
     return (
          <>
               <EditInput label="عنوان شغلی" value={form.job_title} onChange={(v) => update("job_title", v)} />
               <EditInput label="نام شرکت" value={form.company_name} onChange={(v) => update("company_name", v)} />
          </>
     );
};

// ============================================================
// 3. Address Form
// ============================================================
export const AddressForm = ({ form, update }: { form: ProfileFormState, update: <K extends keyof ProfileFormState>(k: K, v: ProfileFormState[K]) => void }) => {
     const { provinces, loading: provincesLoading } = useProvinces();

     const provinceId = form.province ? Number(form.province.value) : null;
     const { cities, loading: citiesLoading } = useCities(provinceId);

     const provinceOptions: Option[] = useMemo(() =>
          provinces.map((p) => ({ label: p.name, value: p.id })), [provinces]
     );
     const cityOptions: Option[] = useMemo(() =>
          cities.map((c) => ({ label: c.name, value: c.id })), [cities]
     );

     return (
          <>
               <div className="auth-form-row cols-2">
                    <div>
                         <div className="auth-label" style={{ fontSize: 12 }}>استان</div>
                         <SelectElement
                              options={provinceOptions}
                              value={form.province}
                              onChange={(val) => { update("province", val); update("city", null); }}
                              placeholder="انتخاب کنید"
                              isLoading={provincesLoading}
                         />
                    </div>
                    <div>
                         <div className="auth-label" style={{ fontSize: 12 }}>شهر</div>
                         <SelectElement
                              options={cityOptions}
                              value={form.city}
                              onChange={(val) => update("city", val)}
                              placeholder="انتخاب کنید"
                              isLoading={citiesLoading}
                              isDisabled={!provinceId}
                         />
                    </div>
               </div>
               <div style={{ marginBottom: 10 }}>
                    <div className="auth-label" style={{ fontSize: 12 }}>نشانی دقیق</div>
                    <textarea
                         className="auth-textarea"
                         value={form.address}
                         onChange={(e) => update("address", e.target.value)}
                         placeholder="خیابان، کوچه، پلاک، واحد"
                    />
               </div>
               <EditInput label="کد پستی" value={form.post_code} onChange={(v) => update("post_code", v)} ltr />
          </>
     );
};
// ============================================================
// 4. Job Certificates Form (جدید - طبق تصویر)
// ============================================================
export const JobCertificatesForm = ({ user, onUserUpdate }: { user: UserMe, onUserUpdate: (u: UserMe) => void }) => {
     const [uploadingType, setUploadingType] = useState<string | null>(null);
     const fileInputRefs = {
          valid_business_license: useRef<HTMLInputElement>(null),
          technical_professional_certificate: useRef<HTMLInputElement>(null),
          letter_of_introduction: useRef<HTMLInputElement>(null),
     };

     const handleFileSelect = async (type: JobCertificateType, e: React.ChangeEvent<HTMLInputElement>) => {
          const file = e.target.files?.[0];
          if (!file) return;

          if (file.size > 10 * 1024 * 1024) {
               MyNotification("خطا", "حجم فایل باید کمتر از 10 مگابایت باشد.", "error");
               return;
          }

          setUploadingType(type);
          try {
               const updatedCert = await certificateRepository.upload({ type, file });
               if (updatedCert) {
                    // 🆕 آپدیت لیست مدارک
                    const currentCerts = user.job_certificates || [];
                    const newCerts = currentCerts.filter(c => c.type !== type).concat(updatedCert);
                    onUserUpdate({ ...user, job_certificates: newCerts });
                    MyNotification("", "مدرک با موفقیت آپلود شد.", "success");
               }
          } catch (err) {
               console.error("[job-cert] upload failed:", err);
               MyNotification("خطا", "آپلود مدرک ناموفق بود.", "error");
          } finally {
               setUploadingType(null);
               if (fileInputRefs[type].current) fileInputRefs[type].current!.value = "";
          }
     };

     const handleDelete = async (type: JobCertificateType) => {
          if (!window.confirm("آیا از حذف این مدرک مطمئن هستید؟")) return;
          try {
               await certificateRepository.delete(type);
               // 🆕 حذف از لیست
               const currentCerts = user.job_certificates || [];
               const newCerts = currentCerts.filter(c => c.type !== type);
               onUserUpdate({ ...user, job_certificates: newCerts });
               MyNotification("", "مدرک حذف شد.", "success");
          } catch (err) {
               console.error("[job-cert] delete failed:", err);
               MyNotification("اخطار ! ", getErrorMessage(err, "حذف مدرک ناموفق بود."), "error");
          }
     };

     const formatSize = (bytes: number) => {
          if (!bytes) return "0 KB";
          const k = 1024;
          const sizes = ["بایت", "کیلوبایت", "مگابایت"];
          const i = Math.floor(Math.log(bytes) / Math.log(k));
          return parseFloat((bytes / Math.pow(k, i)).toFixed(0)) + " " + sizes[i];
     };

     const getFileIcon = (mimeType?: string) => {
          if (!mimeType) return <FaFileAlt size={24} className="text-muted" />;
          if (mimeType.includes("pdf")) return <FaFilePdf size={24} className="text-danger" />;
          if (mimeType.includes("image")) return <FaFileImage size={24} className="text-primary" />;
          if (mimeType.includes("word") || mimeType.includes("document")) return <FaFileWord size={24} className="text-primary" />;
          return <FaFileAlt size={24} className="text-muted" />;
     };

     const renderUploadBox = (type: JobCertificateType, title: string) => {
          // 🆕 پیدا کردن مدرک از لیست بر اساس نوع
          const currentCert = user.job_certificates?.find(c => c.type === type);
          const isUploading = uploadingType === type;
          const isLocked = currentCert?.is_verified;

          if (currentCert) {
               return (
                    <div className="border rounded-4 p-3 d-flex align-items-center justify-content-between mb-4" style={{ borderColor: "#e5e7eb" }}>
                         <div className="d-flex align-items-center gap-2">
                              {getFileIcon(currentCert.file_type)}
                              <div>
                                   <div className="fs-12 fw-bold color-primary  short_text max_165" style={{ direction: "ltr" }}>
                                        {currentCert.file?.split("/").pop()?.split("_").slice(1).join("_") || "document"}
                                   </div>
                                   <div className="fs-10 text-muted">
                                        {formatSize(currentCert.file_size)}
                                   </div>
                              </div>
                         </div>

                         <div className="d-flex align-items-center gap-2">
                              {isLocked ? (
                                   <span className="badge rounded-5 bg-success-2 bg-opacity-10 text-dark px-3 py-2 fs-11">تایید شده</span>
                              ) : (
                                   <button
                                        type="button"
                                        className="btn btn-sm btn-outline-danger rounded-pill fs-11"
                                        onClick={() => handleDelete(type)}
                                   >
                                        حذف
                                   </button>
                              )}
                         </div>
                    </div>
               );
          }

          return (
               <div className="mb-4">
                    <div className="fs-12 fw-bold color-primary mb-2 text-end">{title}</div>
                    <input
                         type="file"
                         ref={fileInputRefs[type]}
                         onChange={(e) => handleFileSelect(type, e)}
                         accept="image/*,application/pdf"
                         style={{ display: "none" }}
                    />
                    <button
                         type="button"
                         className="btn w-100 rounded-4 d-flex align-items-center justify-content-center gap-2 py-3"
                         style={{
                              border: "1px dashed #cbd5e1",
                              backgroundColor: "#f8fafc",
                              color: "#0a387c",
                              fontSize: "13px"
                         }}
                         onClick={() => fileInputRefs[type].current?.click()}
                         disabled={isUploading}
                    >
                         {isUploading ? "در حال آپلود..." : "آپلود فایل"}
                         <FaCloudUploadAlt size={20} />
                    </button>
               </div>
          );
     };

     return (
          <div>
               {/* <p className="fs-12 text-end mb-4" style={{ color: "#4b5563" }}>
                    بارگذاری حداقل یکی از مدارک زیر الزامی است
               </p> */}

               {renderUploadBox("valid_business_license", "جواز کسب معتبر")}
               {renderUploadBox("technical_professional_certificate", "مدرک فنی و حرفه ای")}
               {renderUploadBox("letter_of_introduction", "معرفی‌نامه از نمایندگی آذر")}

               {/* {(!user.job_certificates || user.job_certificates.length === 0) && (
                    <div className="alert alert-warning py-2 fs-11 text-end mt-3 mb-0">
                         برای ثبت، حداقل یکی از مدارک بالا را آپلود کنید.
                    </div>
               )} */}
          </div>
     );
};