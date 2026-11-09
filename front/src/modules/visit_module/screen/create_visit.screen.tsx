// src/modules/visit_module/screen/create_visit.screen.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useCreateVisit } from "../hooks/use-create-visit";
import { useAvailableVisits } from "../hooks/use-available-visits";
import { VISIT_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import { convertToJalaliDate } from "../../../shared/utils/date";
import "../../../shared/styles/visit.css";
import TextInput from "../../../shared/components/inputs/Text";
import MobileNumberInput from "../../../shared/components/inputs/Mobile";

export default function CreateVisitScreen() {
     const navigate = useNavigate();
     const { createVisit, submitting } = useCreateVisit();
     const { visits, loading: loadingVisits } = useAvailableVisits();

     // شبیه‌سازی وضعیت کاربر (اصفهان بودن یا نبودن)
     const [isEligible] = useState(true);

     const [selectedDateId, setSelectedDateId] = useState<number | null>(null);
     const [hasCompanion, setHasCompanion] = useState(false);

     const [compName, setCompName] = useState("");
     const [compFamily, setCompFamily] = useState("");
     const [compMobile, setCompMobile] = useState("");

     const isCompanionValid = !hasCompanion || (
          compName.trim().length > 0 &&
          compFamily.trim().length > 0 &&
          /^09\d{9}$/.test(convertPersianToEnglish(compMobile))
     );

     const canSubmit = isEligible && selectedDateId !== null && isCompanionValid && !submitting;

     const handleSubmit = async () => {
          if (!canSubmit || !selectedDateId) return;

          const payload = {
               visit_id: selectedDateId,
               have_companion: hasCompanion,
               companion_name: hasCompanion ? compName : undefined,
               companion_family: hasCompanion ? compFamily : undefined,
               companion_mobile: hasCompanion ? convertPersianToEnglish(compMobile) : undefined,
          };

          const success = await createVisit(payload);
          if (success) {
               navigate(VISIT_ROUTES.list);
          }
     };

     // تابع کمکی برای گرفتن نام روز هفته (اگر بک‌اند حتما دوشنبه‌ها را می‌دهد، می‌توانید ثابت بگذارید)
     const getDayName = (dateString: string) => {
          const date = new Date(dateString);
          // استفاده از Intl برای گرفتن نام روز هفته به فارسی
          return new Intl.DateTimeFormat("fa-IR", { weekday: "long" }).format(date);
     };

     return (
          <>
               <Header title="درخواست بازدید از کارخانه" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="display-grid">
                    <div className="visit-body">

                         {/* بنر وضعیت */}
                         {isEligible ? (
                              <div className="visit-banner green">
                                   <div className="vb-icon">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
                                   </div>
                                   <div className="vb-text">
                                        <strong>ویژه اعضای اصفهان</strong>
                                        <span className="text-dark">آدرس ثبت شده شما در اصفهان است</span>
                                   </div>
                              </div>
                         ) : (
                              <div className="visit-banner red">
                                   <div className="vb-icon">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>
                                   </div>
                                   <div className="vb-text">
                                        <strong>ویژه اعضای اصفهان</strong>
                                        <span>آدرس ثبت شده شما در اصفهان نیست</span>
                                   </div>
                              </div>
                         )}

                         <h3 className="visit-section-title fs-13">تاریخ بازدید <span className="fs-12 fw-500 text-dark opacity-50">(فقط دو شنبه ها)</span></h3>

                         {loadingVisits ? (
                              <p className="text-center text-muted fs-12" style={{ marginBottom: 24 }}>در حال دریافت تاریخ‌ها...</p>
                         ) : visits.length === 0 ? (
                              <p className="text-center text-muted fs-12" style={{ marginBottom: 24 }}>در حال حاضر تاریخ بازدیدی تعریف نشده است.</p>
                         ) : (
                              <div className="visit-dates-grid">
                                   {visits.map((v) => (
                                        <button
                                             key={v.id}
                                             className={`visit-date-btn ${selectedDateId === v.id ? "selected" : ""} ${v.is_full || !isEligible ? "disabled" : ""}`}
                                             disabled={v.is_full || !isEligible}
                                             onClick={() => setSelectedDateId(v.id)}
                                        >
                                             <span className="vd-day">{v.is_full ? " تکمیل شد" : getDayName(v.date)}</span>
                                             <span className="vd-date fs-12">{convertToJalaliDate(v.date)}</span>
                                        </button>
                                   ))}
                              </div>
                         )}

                         <div className="visit-companion">
                              <div className="visit-companion-row">
                                   <span className="vcr-label">همراه دارم</span>
                                   <label className="auth-switch">
                                        <input
                                             type="checkbox"
                                             checked={hasCompanion}
                                             onChange={(e) => setHasCompanion(e.target.checked)}
                                             disabled={!isEligible}
                                        />
                                        <span className="slider" />
                                   </label>
                              </div>
                              <p className="vcr-hint m-0">حداکثر 2 نفر (شما و یک همراه)</p>
                         </div>

                         {hasCompanion && (
                              <div className="visit-companion-form mt-3 box___main bg-white">
                                   <h4 className="vcf-title">مشخصات همراه</h4>
                                   <div className="row">
                                        <div className="col">
                                             <label className="label___main">نام</label>
                                             <TextInput
                                                  value={compName}
                                                  onChange={setCompName}
                                                  minLength={3}
                                                  maxLength={200}
                                                  className="input___main"
                                                  required
                                                  placeholder="نام "
                                                  errorMessage="نام باید بین ۳ تا ۲۰۰ کاراکتر باشد"
                                             />
                                        </div>
                                        <div className="col">
                                             <label className="label___main">نام خانوادگی</label>
                                             <TextInput
                                                  value={compFamily}
                                                  onChange={setCompFamily}
                                                  minLength={3}
                                                  maxLength={200}
                                                  className="input___main"
                                                  required
                                                  placeholder="نام "
                                                  errorMessage="نام باید بین ۳ تا ۲۰۰ کاراکتر باشد"
                                             />
                                        </div>
                                   </div>
                                   <label className="label___main" style={{ marginTop: 12 }}>شماره موبایل همراه</label>

                                   <MobileNumberInput
                                        value={compMobile}
                                        className="input___main text-center"
                                        onChange={(raw) => setCompMobile(raw)}
                                        errorMessage="شماره موبایل معتبر نیست"
                                   />
                              </div>
                         )}

                    </div>

                    <div className="sticky-bottom">
                         <button className="btn___main" onClick={handleSubmit} disabled={!canSubmit}>
                              {submitting ? "در حال ثبت..." : "ثبت درخواست"}
                         </button>
                    </div>
               </div>
          </>
     );
}