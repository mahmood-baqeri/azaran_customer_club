/* eslint-disable react-hooks/exhaustive-deps */
// src/modules/profile_module/screens/profile.screen.tsx

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useUser } from "../../user_module/hooks/use-user";
import { userRepository } from "../../user_module/repository/user.repository";
import { useCities, useProvinces } from "../../settings_module/hooks/use-locations";
import { MyNotification } from "../../../shared/utils/notification";
import Header from "../../../app/layouts/header";
import SelectElement, { type Option } from "../../../shared/tools/select";
import { PersianDatePicker } from "../../../shared/utils/persianDatePicker";
import "../../../shared/styles/AuthTemplate.css";
import "../../../shared/styles/react-select.css";
import { convertToJalaliDate } from "../../../shared/utils/date";
import { getErrorMessage } from "../../../shared/api/errors";

// ------- Types & constants -------
interface FormState {
     firstname: string;
     lastname: string;
     gender: "male" | "female" | "";
     mobile: string;
     birth_day: Date | null;
     national_code: string;
     address: string;
     post_code: string;
}

const EMPTY: FormState = {
     firstname: "", lastname: "", gender: "", mobile: "",
     birth_day: null, national_code: "", address: "", post_code: "",
};

// ------- Helpers -------
const ViewField = ({ label, value, ltr }: { label: string; value: string | null | undefined; ltr?: boolean }) => (
     <div style={{ marginBottom: 10 }}>
          <div className="auth-label" style={{ fontSize: 12 }}>{label}</div>
          <div style={{
               fontFamily: "Yekan Bakh FaNum, Yekan Bakh",
               height: 44, display: "flex", alignItems: "center",
               padding: "0 16px", background: "#f6f8fc",
               border: "1.5px solid #eef1f7", borderRadius: 12,
               fontSize: 13, color: value ? "#14306b" : "#b8c0d2",
               direction: ltr ? "ltr" : "rtl",
               textAlign: ltr ? "left" : "right",
          }}>{value || "—"}</div>
     </div>
);

const EditInput = ({ label, value, onChange, ltr, type = "text", placeholder }: {
     label: string; value: string; onChange: (v: string) => void;
     ltr?: boolean; type?: string; placeholder?: string;
}) => (
     <div style={{ marginBottom: 10 }}>
          <div className="auth-label" style={{ fontSize: 12 }}>{label}</div>
          <div className="auth-field" style={{ marginBottom: 0 }}>
               <input type={type} value={value} onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder || ""} dir={ltr ? "ltr" : "rtl"}
                    style={{ paddingRight: 16, paddingLeft: 16, textAlign: ltr ? "left" : "right" }} />
          </div>
     </div>
);

const parseBirthDate = (iso: string | null | undefined): Date | null => {
     if (!iso) return null;
     const d = new Date(iso);
     return isNaN(d.getTime()) ? null : d;
};

const toIsoDateString = (d: Date | null): string | undefined =>
     d ? d.toISOString().split("T")[0] : undefined;

// ------- Screen -------
export default function ProfileScreen() {
     const { user, setUser } = useUser();
     const { provinces, loading: provincesLoading } = useProvinces();

     const [editing, setEditing] = useState(false);
     const [saving, setSaving] = useState(false);
     const [form, setForm] = useState<FormState>(EMPTY);

     const [selectedProvince, setSelectedProvince] = useState<Option | null>(null);
     const [selectedCity, setSelectedCity] = useState<Option | null>(null);
     const provinceId = selectedProvince ? Number(selectedProvince.value) : null;
     const { cities, loading: citiesLoading } = useCities(provinceId);

     // ⚠️ وضعیت دریافت اطلاعات کامل
     const [loadingFull, setLoadingFull] = useState(false);
     const [fullError, setFullError] = useState(false);
     const fetchedFor = useRef<string | null>(null);

     const provinceOptions: Option[] = useMemo(
          () => provinces.map((p) => ({ label: p.name, value: p.id })), [provinces]
     );
     const cityOptions: Option[] = useMemo(
          () => cities.map((c) => ({ label: c.name, value: c.id })), [cities]
     );

     // ✅ یک بار در ورود به صفحه، اطلاعات کامل را بگیر (چون base کافی نیست)
     useEffect(() => {
          if (!user) return;
          if (fetchedFor.current === user.uuid) return;   // یک بار برای هر کاربر
          if (user.stats !== undefined) {                 // اگر از قبل full است، نیاز نیست
               fetchedFor.current = user.uuid;
               return;
          }

          fetchedFor.current = user.uuid;
          setLoadingFull(true);
          setFullError(false);

          userRepository.loadFullInformation()
               .then((full) => setUser(full))
               .catch((err) => {
                    console.error("[profile] full info load failed:", err);
                    setFullError(true);
               })
               .finally(() => setLoadingFull(false));
     }, [user?.uuid, setUser]);

     // مقداردهی فرم از user (چه base چه full)
     useEffect(() => {
          if (!user) return;
          setForm({
               firstname: user.firstname ?? "",
               lastname: user.lastname ?? "",
               gender: user.profile?.gender ?? "",
               mobile: user.mobile ?? "",
               birth_day: parseBirthDate(user.profile?.birth_date),
               national_code: user.profile?.national_code ?? "",
               address: user.profile?.address ?? "",
               post_code: user.profile?.post_code ?? "",
          });

          setSelectedProvince(user.profile?.province?.id
               ? { label: user.profile.province.name ?? "", value: user.profile.province.id }
               : null);
          setSelectedCity(user.profile?.city?.id
               ? { label: user.profile.city.name ?? "", value: user.profile.city.id }
               : null);
     }, [user]);

     const update = <K extends keyof FormState>(k: K, v: FormState[K]) =>
          setForm((prev) => ({ ...prev, [k]: v }));

     const handleSave = async () => {
          if (!user) return;
          setSaving(true);
          try {
               const updated = await userRepository.updateProfile({
                    firstname: form.firstname,
                    lastname: form.lastname,
                    gender: form.gender || undefined,
                    mobile: form.mobile || undefined,
                    birth_day: toIsoDateString(form.birth_day),
                    national_code: form.national_code || undefined,
                    address: form.address || undefined,
                    post_code: form.post_code || undefined,
                    province_id: selectedProvince ? Number(selectedProvince.value) : null,
                    city_id: selectedCity ? Number(selectedCity.value) : null,
               });
               // ✅ merge: پاسخ بک‌اند فقط base است؛ فیلدهای full (profile, stats, ...) حفظ شوند
               setUser({ ...user, ...updated });
               MyNotification("", "اطلاعات با موفقیت ذخیره شد.", "success");
               setEditing(false);
          } catch (err) {
               console.error("[profile] save failed:", err);
               MyNotification("اخطار ! ", getErrorMessage(err, "ذخیره اطلاعات ناموفق بود."), "error");
          } finally {
               setSaving(false);
          }
     };

     const handleCancel = () => {
          setEditing(false);
          if (user) {
               setForm({
                    firstname: user.firstname ?? "",
                    lastname: user.lastname ?? "",
                    gender: user.profile?.gender ?? "",
                    mobile: user.mobile ?? "",
                    birth_day: parseBirthDate(user.profile?.birth_date),
                    national_code: user.profile?.national_code ?? "",
                    address: user.profile?.address ?? "",
                    post_code: user.profile?.post_code ?? "",
               });
          }
     };

     const copyReferral = useCallback(async () => {
          if (!user?.referral_code) return;
          try {
               await navigator.clipboard.writeText(user.referral_code);
               MyNotification("", "کد معرف کپی شد.", "success");
          } catch {
               MyNotification("", "کپی ناموفق بود.", "error");
          }
     }, [user?.referral_code]);

     // 🔴 اگر در حال دریافت اطلاعات کامل هستیم یا خطا داریم، بلاک کن
     if (!user || loadingFull || (user.stats === undefined && !fullError)) {
          return (
               <div className="auth-root">
                    <div className="auth-shell">
                         <Header title="پروفایل" showBack={true} />
                         <div className="auth-body" style={{ paddingTop: 20 }}>
                              <p className="text-center text-muted">در حال بارگذاری…</p>
                         </div>
                    </div>
               </div>
          );
     }

     if (fullError && user.stats === undefined) {
          return (
               <div className="auth-root">
                    <div className="auth-shell">
                         <Header title="پروفایل" showBack={true} />
                         <div className="auth-body" style={{ paddingTop: 20 }}>
                              <p className="text-center text-muted">خطا در دریافت اطلاعات پروفایل.</p>
                              <button
                                   className="auth-btn"
                                   style={{ marginTop: 12 }}
                                   onClick={() => {
                                        fetchedFor.current = null;
                                        setFullError(false);
                                   }}
                              >
                                   تلاش مجدد
                              </button>
                         </div>
                    </div>
               </div>
          );
     }

     return (
          <>
               <Header title="تنظیمات حساب" showLogo={false} showBack={true} menuBg="f7f8fb" buttonBg="white" />
               <div className="auth-root mb-4">
                    <div className="auth-shell rounded-10">
                         <div className="auth-body" style={{ paddingTop: 16 }}>
                              {user.referral_code && (
                                   <div style={{
                                        background: "#f6f8fc", border: "1px solid #dfe4ee",
                                        borderRadius: 12, padding: 12, display: "flex",
                                        justifyContent: "space-between", alignItems: "center",
                                        marginBottom: 18,
                                   }}>
                                        <div>
                                             <p style={{ fontSize: 11, color: "#8792a8", margin: 0 }}>کد معرف شما</p>
                                             <p style={{ fontSize: 14, fontWeight: 800, color: "#14306b", margin: 0, direction: "ltr" }}>
                                                  {user.referral_code}
                                             </p>
                                        </div>
                                        <button type="button" className="auth-link" onClick={copyReferral} style={{ fontSize: 12 }}>
                                             کپی
                                        </button>
                                   </div>
                              )}

                              {!editing && (
                                   <button type="button" className="auth-btn" style={{ marginBottom: 18 }} onClick={() => setEditing(true)}>
                                        ویرایش اطلاعات
                                   </button>
                              )}

                              <div className="auth-section-title">اطلاعات شخصی</div>
                              {editing ? (
                                   <>
                                        <div className="auth-form-row cols-2">
                                             <EditInput label="نام " value={form.firstname} onChange={(v) => update("firstname", v)} />
                                             <EditInput label="نام خانوادگی" value={form.lastname} onChange={(v) => update("lastname", v)} />
                                        </div>
                                        <div className="auth-form-row cols-2">
                                             <EditInput label="کد ملی" value={form.national_code} onChange={(v) => update("national_code", v)} ltr />
                                             <div style={{ marginBottom: 10 }}>
                                                  <div className="auth-label" style={{ fontSize: 12 }}>تاریخ تولد</div>
                                                  <PersianDatePicker value={form.birth_day} onChange={(d) => update("birth_day", d)} placeholder="انتخاب تاریخ تولد" />
                                             </div>
                                        </div>
                                        <div style={{ marginBottom: 10 }}>
                                             <div className="auth-label" style={{ fontSize: 12 }}>جنسیت</div>
                                             <div className="auth-select">
                                                  <select value={form.gender} onChange={(e) => update("gender", e.target.value as FormState["gender"])}>
                                                       <option value="">انتخاب کنید</option>
                                                       <option value="male">مرد</option>
                                                       <option value="female">زن</option>
                                                  </select>
                                             </div>
                                        </div>
                                   </>
                              ) : (
                                   <>
                                        <div className="auth-form-row cols-2">
                                             <ViewField label="نام" value={user.firstname} />
                                             <ViewField label="نام خانوادگی" value={user.lastname} />
                                        </div>
                                        <div className="auth-form-row cols-2">
                                             <ViewField label="کد ملی" value={user.profile?.national_code} ltr />
                                             <ViewField label="تاریخ تولد" value={user.profile?.birth_date ? convertToJalaliDate(user.profile?.birth_date?.split("T")[0]) : "-"} ltr />
                                        </div>
                                        <ViewField label="جنسیت" value={user.profile?.gender_display} />
                                   </>
                              )}

                              <div className="auth-section-title">آدرس و شغل</div>
                              {editing ? (
                                   <>
                                        <div className="auth-form-row cols-2">
                                             <div>
                                                  <div className="auth-label" style={{ fontSize: 12 }}>استان</div>
                                                  <SelectElement options={provinceOptions} value={selectedProvince} onChange={setSelectedProvince} placeholder="انتخاب کنید" isLoading={provincesLoading} />
                                             </div>
                                             <div>
                                                  <div className="auth-label" style={{ fontSize: 12 }}>شهر</div>
                                                  <SelectElement options={cityOptions} value={selectedCity} onChange={setSelectedCity} placeholder="انتخاب کنید" isLoading={citiesLoading} isDisabled={!provinceId} />
                                             </div>
                                        </div>
                                        <div style={{ marginBottom: 10 }}>
                                             <div className="auth-label" style={{ fontSize: 12 }}>نشانی دقیق</div>
                                             <textarea className="auth-textarea" value={form.address} onChange={(e) => update("address", e.target.value)} placeholder="خیابان، کوچه، پلاک، واحد" />
                                        </div>
                                        <div className="auth-form-row cols-2">
                                             <EditInput label="کد پستی" value={form.post_code} onChange={(v) => update("post_code", v)} ltr />
                                        </div>
                                   </>
                              ) : (
                                   <>
                                        <div className="auth-form-row cols-2">
                                             <ViewField label="استان" value={user.profile?.province?.name} />
                                             <ViewField label="شهر" value={user.profile?.city?.name} />
                                        </div>
                                        <ViewField label="نشانی دقیق" value={user.profile?.address} />
                                        <div className="auth-form-row cols-2">
                                             <ViewField label="کد پستی" value={user.profile?.post_code} ltr />
                                        </div>
                                   </>
                              )}

                              {editing && (
                                   <div style={{ display: "flex", gap: 10, marginTop: 22 }}>
                                        <button type="button" className="auth-btn" style={{ flex: 1 }} onClick={handleSave} disabled={saving}>
                                             {saving ? "در حال ذخیره..." : "ذخیره تغییرات"}
                                        </button>
                                        <button type="button" className="auth-btn" style={{ flex: 1, background: "#c5cee0", color: "#fff" }} onClick={handleCancel} disabled={saving}>
                                             انصراف
                                        </button>
                                   </div>
                              )}
                         </div>
                    </div>
               </div>
          </>
     );
}