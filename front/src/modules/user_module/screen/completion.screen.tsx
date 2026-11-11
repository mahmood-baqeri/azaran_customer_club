// front/src/modules/profile_module/screens/completion.screen.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaChevronLeft, FaCheck } from "react-icons/fa";
import { useUser } from "../../user_module/hooks/use-user";
import { userRepository } from "../../user_module/repository/user.repository";
import Header from "../../../app/layouts/header";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import { MyNotification } from "../../../shared/utils/notification";
import { USER_ROUTES } from "../routes";
import {
     ProfileFormState,
     EMPTY_FORM,
     PersonalForm,
     AddressForm,
     JobCertificatesForm,
     mapFormToApiPayload,
     BirthDayForm
} from "../components/ProfileForms";
import { getErrorMessage } from "../../../shared/api/errors";

type ModalType = "personal" | "documents" | "address" | "birth_day" | null;

export default function CompletionScreen() {
     const { user, setUser } = useUser();
     const navigate = useNavigate();

     const [activeModal, setActiveModal] = useState<ModalType>(null);
     const [form, setForm] = useState<ProfileFormState>(EMPTY_FORM);
     const [saving, setSaving] = useState(false);

     if (!user) return null;

     // بررسی وضعیت تکمیل هر بخش بر اساس دیتای واقعی
     const isPersonalComplete = !!(user.profile?.national_code && user.profile?.birth_date && user.firstname);
     const isBirthDayComplete = !!(user.profile?.birth_date);
     const isDocsComplete = !!(user.job_certificates && user.job_certificates.length == 3);
     const isAddressComplete = !!(user.profile?.address && user.profile?.province && user.profile?.city);
     const isFavoriteQuestionsComplete = user.has_answered_all_favorites;
     // const isAllComplete = isPersonalComplete && isDocsComplete && isAddressComplete;

     const copyReferral = async () => {
          if (!user?.referral_code) return;
          try {
               await navigator.clipboard.writeText(user.referral_code);
               MyNotification("", "کد معرف کپی شد.", "success");
          } catch {
               MyNotification("", "کپی ناموفق بود.", "error");
          }
     };

     const handleOpenModal = (type: ModalType) => {
          setForm({
               ...EMPTY_FORM,
               firstname: user.firstname ?? "",
               lastname: user.lastname ?? "",
               gender: user.profile?.gender ?? "",
               mobile: user.mobile ?? "",
               birth_day: user.profile?.birth_date ? new Date(user.profile.birth_date) : null,
               national_code: user.profile?.national_code ?? "",
               address: user.profile?.address ?? "",
               post_code: user.profile?.post_code ?? "",
               job_title: user.profile?.job_title ?? "",
               company_name: user.profile?.company_name ?? "",
               province: user.profile?.province?.id ? { label: user.profile.province.name ?? "", value: user.profile.province.id } : null,
               city: user.profile?.city?.id ? { label: user.profile.city.name ?? "", value: user.profile.city.id } : null,
          });
          setActiveModal(type);
     };

     const updateForm = <K extends keyof ProfileFormState>(k: K, v: ProfileFormState[K]) => {
          setForm((prev) => ({ ...prev, [k]: v }));
     };

     const handleSaveModal = async () => {
          setSaving(true);
          try {
               const payload = mapFormToApiPayload(form);
               const updated = await userRepository.updateProfile(payload);
               setUser(updated);
               MyNotification("", "اطلاعات با موفقیت ذخیره شد.", "success");
               setActiveModal(null);
          } catch (err) {
               console.error("[completion] save failed:", err);
               MyNotification("", getErrorMessage(err, "خطا در به‌روزرسانی پروفایل"), "error");
          } finally {
               setSaving(false);
          }
     };

     return (
          <div dir="rtl">
               <Header
                    title="پروفایل من"
                    showBack={true}
                    showLogo={false}
                    menuBg="f7f8fb"
                    buttonBg="white"
                    action={
                         <a href={USER_ROUTES.profile} className="header-action-btn">
                              <MyImage src={ICONS.lock_2} def="/assets/none.png" alt="settings" className="img20_20" />
                              <span className="color-primary fw-400 me-1">تنظیمات حساب</span>
                         </a>
                    }
               />

               <div className="px-3 py-3">
                    {/* ۱. کارت آبی بالا */}
                    <div className="rounded-4 p-3 mb-4 text-white bg-primary">
                         <div className="d-flex justify-content-between align-items-start">
                              <div>
                                   <h6 className="fw-bold fs-14 text-white mb-2">{user.name}</h6>
                                   <p className="fs-11 opacity mb-0 text-white">{user.nature_display || "سطح کاردان"}</p>
                              </div>
                              <div className="d-grid">
                                   <div className="d-flex align-items-center gap-1 bg-opacity-10 px-2 py-1 rounded-pill justify-content-end">
                                        <span className="text-warning fw-bold fs-12">{user.score?.current_balance?.toLocaleString() || "۰"}</span>
                                        <span className="fs-10 opacity-75 text-white">امتیاز</span>
                                        <MyImage src={ICONS.coin_15} className="rounded-100" def="/assets/avatar.png" alt="coin" />
                                   </div>
                                   <div className="d-flex align-items-center gap-2 bg-opacity-10 rounded-2" style={{ width: 'fit-content' }}>
                                        <span className="fs-10 opacity-75 text-white">کد :</span>
                                        <span className="fs-12 fw-bold text-white" style={{ direction: 'ltr' }}>{user.referral_code || "ثبت نشده"}</span>
                                        <button type="button" className="auth-link" onClick={copyReferral}>
                                             <MyImage src={ICONS.copy_2} def="/assets/avatar.png" alt="copy" className="img15_15" />
                                        </button>
                                   </div>
                              </div>
                         </div>
                         <div className="row m-0 mt-1">
                              <hr />
                         </div>
                         <div className="row">
                              <div className="col text-center">
                                   <p className="text-light m-0 fs-12">10</p>
                                   <span className="fs-10 fw-100">پروژه</span>
                              </div>
                              <div className="col text-center">
                                   <p className="text-light m-0 fs-12">5</p>
                                   <span className="fs-10 fw-100">معرفی</span>
                              </div>
                              <div className="col text-center">
                                   <p className="text-light m-0 fs-12">15</p>
                                   <span className="fs-10 fw-100">عکس</span>
                              </div>
                              <div className="col text-center">
                                   <p className="text-light m-0 fs-12">8</p>
                                   <span className="fs-10 fw-100">پرسش</span>
                              </div>

                         </div>
                    </div>


                    {/* ۲. لیست تکمیل اطلاعات */}
                    <h6 className="fw-bold fs-14 mb-3 color-primary text-end">اطلاعات من</h6>

                    <div className="d-flex flex-column gap-2 mb-4">
                         <CompletionCard
                              title="مشخصات فردی"
                              status={isPersonalComplete ? "ویرایش" : "تکمیل نشده"}
                              isComplete={isPersonalComplete}
                              onClick={() => handleOpenModal("personal")}
                         />
                         <CompletionCard
                              title="تاریخ تولد"
                              status={isBirthDayComplete ? "ویرایش" : "تکمیل نشده"}
                              isComplete={isBirthDayComplete}
                              onClick={() => handleOpenModal("birth_day")}
                         />
                         <CompletionCard
                              title="مدارک شغلی"
                              status={isDocsComplete ? "ویرایش" : "تکمیل نشده"}
                              isComplete={isDocsComplete}
                              onClick={() => handleOpenModal("documents")}

                         />
                         <CompletionCard
                              title="آدرس و موقعیت"
                              status={isAddressComplete ? "ویرایش" : "تکمیل نشده"}
                              isComplete={isAddressComplete}
                              onClick={() => handleOpenModal("address")}

                         />
                         <CompletionCard
                              title="علایق و سلایق"
                              status={isFavoriteQuestionsComplete ? "ویرایش" : "تکمیل نشده"}
                              isComplete={isFavoriteQuestionsComplete}
                              onClick={() => navigate(USER_ROUTES.favorite)}

                         />

                    </div>

                    {/* ۳. بنر هدیه */}
                    <div className="rounded-4 p-3 d-grid mb-4 bg-warning">
                         <div className="d-flex mb-3">
                              <div>
                                   <h6 className="fw-bold color-primary fs-13 mb-1">هدیه خوش‌آمدگویی</h6>
                                   <p className="text-muted fs-11 mb-0 lh-base">
                                        هدیه  ات آماده سفارش شده است
                                   </p>
                              </div>
                              <div className="d-flex justify-content-center align-items-center rounded-3 me-auto">
                                   <MyImage src={ICONS.gift} def="/assets/none.png" alt="gift" className="img25_25" />
                              </div>
                         </div>

                         <button
                              onClick={() => navigate(USER_ROUTES.profile)}
                              className="btn w-100 text-white fw-bold fs-13 rounded-10 p-2 bg-primary"
                         >
                              دریافت هدیه
                         </button>
                    </div>
               </div>

               {/* ========================================== */}
               {/* مودال‌های بوت‌استرپ */}
               {/* ========================================== */}
               {activeModal && (
                    <>
                         <div className="modal-backdrop fade show" onClick={() => setActiveModal(null)}></div>
                         <div className="modal fade show d-block" tabIndex={-1} role="dialog">
                              <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                                   <div className="modal-content rounded-4 border-0 overflow-unset">
                                        <div className="modal-header border-bottom-0 pb-0">
                                             <h5 className="modal-title fw-bold fs-14 color-primary">
                                                  {activeModal === "personal" && "ویرایش مشخصات فردی"}
                                                  {activeModal === "documents" && "مدارک شغلی"}
                                                  {activeModal === "address" && "ویرایش آدرس و موقعیت"}
                                                  {activeModal === "birth_day" && "ویرایش تاریخ تولد"}
                                             </h5>
                                             <button type="button" className="btn-close" onClick={() => setActiveModal(null)} aria-label="بستن"></button>
                                        </div>
                                        <div className="modal-body py-4 overflow-unset">
                                             {activeModal === "personal" && <PersonalForm form={form} update={updateForm} />}

                                             {/* 👇 اینجا فرم جدید مدارک لود میشه */}
                                             {activeModal === "documents" && (
                                                  <JobCertificatesForm
                                                       user={user}
                                                       onUserUpdate={(newUser) => setUser(newUser)}
                                                  />
                                             )}

                                             {activeModal === "address" && <AddressForm form={form} update={updateForm} />}
                                             {activeModal === "birth_day" && <BirthDayForm form={form} update={updateForm} />}
                                        </div>
                                        <div className="modal-footer border-top-0 pt-0">
                                             <button
                                                  type="button"
                                                  className="btn btn-light rounded-3 fs-13"
                                                  onClick={() => setActiveModal(null)}
                                                  disabled={saving}
                                             >
                                                  انصراف
                                             </button>

                                             {/* دکمه ذخیره فقط برای مشخصات و آدرس نمایش داده میشه */}
                                             {activeModal !== "documents" ? (
                                                  <button
                                                       type="button"
                                                       className="btn bg-primary rounded-3 fs-13"
                                                       onClick={handleSaveModal}
                                                       disabled={saving}
                                                  >
                                                       {saving ? "در حال ذخیره..." : "ذخیره تغییرات"}
                                                  </button>
                                             ) : (<></>
                                                  // <button
                                                  //      type="button"
                                                  //      className="btn btn-primary rounded-3 fs-13"
                                                  //      onClick={() => setActiveModal(null)}
                                                  // >
                                                  //      ثبت مدارک
                                                  // </button>
                                             )}
                                        </div>
                                   </div>
                              </div>
                         </div>
                    </>
               )}
          </div>
     );
}

// ==========================================
// کامپوننت کارت‌های لیست
// ==========================================
const CompletionCard = ({ title, status, isComplete, onClick }: { title: string, status: string, isComplete: boolean, onClick: () => void }) => {
     return (
          <div
               className="bg-white rounded-4 p-3 d-flex justify-content-between align-items-center shadow-sm"
               style={{ cursor: 'pointer' }}
               onClick={onClick}
          >
               <div className="d-flex align-items-center gap-2">
                    <div className={`rounded-circle d-flex justify-content-center align-items-center ${isComplete ? 'bg-success bg-opacity-10' : 'bg-warning bg-opacity-10'}`} style={{ width: 24, height: 24 }}>
                         <FaCheck size={13} className={isComplete ? "text-white" : "text-white"} style={{ strokeWidth: 2 }} />
                    </div>
                    <div>
                         <div className="fs-12 fw-bold color-primary">{title}</div>
                    </div>
               </div>
               <div className="d-flex align-items-center gap-2">
                    <span className={`fs-10 ${isComplete ? 'text-success' : 'text-warning'}`}>{status}</span>
                    {isComplete ?
                         <MyImage src={ICONS.edit} def="/assets/none.png" alt="edit" className="img15_15" />
                         :
                         <FaChevronLeft size={12} className="text-muted" />
                    }
               </div>
          </div>
     );
}