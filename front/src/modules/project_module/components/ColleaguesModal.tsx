// src/modules/project_module/components/ColleaguesModal.tsx

import { useState } from "react";
import axios from "axios";
import { useProjectDetail } from "../hooks/use-project-detail";
import { projectRepository } from "../repository/project.repository";
import { MyNotification } from "../../../shared/utils/notification";
import PhoneInput from "../../../shared/components/inputs/Phone";
import NumberInput from "../../../shared/components/inputs/Number";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     projectId: number;
}

/** استخراج پیام خطای انسانی از هر نوع خطای ناشناخته */
function extractErrorMessage(err: unknown, fallback: string): string {
     if (axios.isAxiosError(err)) {
          return err.response?.data?.message || err.message || fallback;
     }
     if (err instanceof Error) return err.message || fallback;
     if (typeof err === "object" && err !== null && "message" in err) {
          const m = (err as { message: unknown }).message;
          if (typeof m === "string") return m;
     }
     return fallback;
}

export default function ColleaguesModal({ isOpen, onClose, projectId }: Props) {
     const { project, refresh } = useProjectDetail(projectId);

     // فرم
     const [mobile, setMobile] = useState("");
     const [percent, setPercent] = useState<number | null>(10);

     // اعتبار هر فیلد (از onValidityChange کامپوننت‌ها)
     const [mobileValid, setMobileValid] = useState(false);
     const [percentValid, setPercentValid] = useState(true);

     const [loading, setLoading] = useState(false);

     if (!isOpen || !project) return null;

     const colleagues = project.colleagues || [];
     const totalPercent = colleagues
          .filter((c) => c.is_active)
          .reduce((sum, c) => sum + c.percent, 0);

     const remainingPercent = Math.max(0, 100 - totalPercent);
     const isLocked = project.status !== "pending";
     const isFull = remainingPercent === 0;

     // اعتبارسنجی نهایی — تکیه بر onValidityChange + بررسی خالی
     const isMobileEmpty = mobile.replace(/\D/g, "").length === 0;
     const isPercentEmpty = percent === null;

     const isMobileOk = mobileValid && !isMobileEmpty;
     const isPercentOk = percentValid && !isPercentEmpty && !isFull;

     const canSubmit = isMobileOk && isPercentOk && !loading && !isLocked && !isFull;

     const showMobileError = !isMobileEmpty && !mobileValid;
     const showPercentError = !isPercentEmpty && !percentValid;

     /* ------------------------------ Handlers ------------------------------ */

     const handleAdd = async () => {
          if (!isMobileOk) {
               MyNotification("خطا", "شماره موبایل نامعتبر است", "error");
               return;
          }
          if (!isPercentOk) {
               MyNotification(
                    "خطا",
                    isFull
                         ? "سقف ۱۰۰٪ تکمیل است"
                         : `درصد باید بین ۱ تا ${remainingPercent} باشد`,
                    "error"
               );
               return;
          }

          setLoading(true);
          try {
               await projectRepository.addColleague(
                    projectId,
                    mobile.replace(/\D/g, ""),
                    percent as number
               );
               setMobile("");
               setPercent(10);
               MyNotification("", "همکار با موفقیت اضافه شد", "success");
               refresh();
          } catch (err) {
               MyNotification("خطا", extractErrorMessage(err, "خطا در افزودن همکار"), "error");
          } finally {
               setLoading(false);
          }
     };

     const handleToggle = async (id: number) => {
          try {
               await projectRepository.toggleColleague(projectId, id);
               refresh();
          } catch (err) {
               MyNotification("خطا", extractErrorMessage(err, "خطا در تغییر وضعیت"), "error");
          }
     };

     const handleDelete = async (id: number) => {
          if (!window.confirm("آیا از حذف این همکار مطمئن هستید؟")) return;
          try {
               await projectRepository.deleteColleague(projectId, id);
               MyNotification("", "همکار حذف شد", "success");
               refresh();
          } catch (err) {
               MyNotification("خطا", extractErrorMessage(err, "خطا در حذف"), "error");
          }
     };

     /* ------------------------------- Render ------------------------------- */

     return (
          <div className="proj-modal-overlay" onClick={onClose}>
               <div className="proj-modal-sheet" onClick={(e) => e.stopPropagation()}>
                    <div className="proj-modal-header">
                         <h2>همکاران من در پروژه</h2>
                         <button className="close-btn" onClick={onClose}>
                              &times;
                         </button>
                    </div>

                    <div className="proj-modal-body">
                         {!isLocked && (
                              <>
                                   <div
                                        className="add-colleague-form mb-2"
                                        style={{
                                             display: "flex",
                                             alignItems: "center",
                                             gap: 6,
                                             direction: "rtl",
                                             width: "100%",
                                        }}
                                   >
                                        <div className="w-50">
                                             <PhoneInput
                                                  value={mobile}
                                                  className="colleague-input-mobile w_100 h__40"
                                                  onValidityChange={setMobileValid}
                                                  onChange={(raw) => setMobile(raw)}
                                                  errorMessage="شماره موبایل معتبر نیست"
                                                  style={{
                                                       flex: "1 1 0",
                                                       minWidth: 0,
                                                       boxSizing: "border-box",
                                                  }}
                                             />

                                        </div>

                                        <NumberInput
                                             value={percent}
                                             onChange={(v) => setPercent(v)}
                                             onValidityChange={setPercentValid}
                                             placeholder="0"
                                             min={1}
                                             max={Math.max(1, remainingPercent)}
                                             disabled={isFull}
                                             textAlign="center"
                                             errorMessage={
                                                  isFull
                                                       ? "سقف ۱۰۰٪ تکمیل است"
                                                       : `درصد باید بین ۱ تا ${remainingPercent} باشد`
                                             }
                                             className="colleague-input-percent"
                                             style={{
                                                  flex: "0 0 70px",
                                                  width: 70,
                                                  boxSizing: "border-box",
                                             }}
                                        />

                                        <button
                                             className="colleague-add-btn"
                                             onClick={handleAdd}
                                             disabled={!canSubmit}
                                             style={{ flex: "0 0 auto", whiteSpace: "nowrap" }}
                                        >
                                             {loading ? "..." : "افزودن"}
                                        </button>
                                   </div>

                                   {(showMobileError || showPercentError || isFull) && (
                                        <div
                                             style={{
                                                  color: "#d32f2f",
                                                  fontSize: 11,
                                                  marginTop: 6,
                                                  textAlign: "right",
                                             }}
                                        >
                                             {isFull && "سقف ۱۰۰٪ تکمیل است. برای افزودن، درصد یک همکار را کاهش دهید."}
                                             {!isFull && showMobileError && showPercentError && " • "}
                                             {!isFull && showPercentError &&
                                                  `درصد مجاز: ۱ تا ${remainingPercent}`}
                                        </div>
                                   )}
                              </>
                         )}

                         <div className="colleagues-list">
                              {colleagues.length === 0 ? (
                                   <p
                                        style={{
                                             textAlign: "center",
                                             fontSize: 12,
                                             color: "#8792a8",
                                             padding: "20px 0",
                                        }}
                                   >
                                        هنوز همکاری اضافه نکرده‌اید.
                                   </p>
                              ) : (
                                   colleagues.map((c) => (
                                        <div
                                             key={c.id}
                                             className={`colleague-row ${!c.is_active ? "disabled" : ""}`}
                                        >
                                             <div style={{ display: "flex", flexDirection: "column" }}>
                                                  <span className="colleague-mobile" dir="ltr">
                                                       {c.user_mobile}
                                                  </span>
                                                  <span style={{ fontSize: 10, color: "#6b7794" }}>
                                                       {c.user_name}
                                                  </span>
                                             </div>
                                             <div
                                                  style={{ display: "flex", alignItems: "center", gap: 12 }}
                                             >
                                                  <span
                                                       style={{
                                                            fontSize: 13,
                                                            fontWeight: 800,
                                                            color: "#14306b",
                                                       }}
                                                  >
                                                       {c.percent}%
                                                  </span>

                                                  <label
                                                       className="auth-switch"
                                                       aria-label={`فعال/غیرفعال کردن ${c.user_name}`}
                                                  >
                                                       <input
                                                            type="checkbox"
                                                            checked={c.is_active}
                                                            onChange={() => !isLocked && handleToggle(c.id)}
                                                            disabled={isLocked}
                                                       />
                                                       <span className="slider" />
                                                  </label>

                                                  {!isLocked && (
                                                       <button
                                                            className="colleague-delete-btn"
                                                            onClick={() => handleDelete(c.id)}
                                                            aria-label={`حذف ${c.user_name}`}
                                                       >
                                                            <svg
                                                                 width="16"
                                                                 height="16"
                                                                 viewBox="0 0 24 24"
                                                                 fill="none"
                                                                 stroke="#d32f2f"
                                                                 strokeWidth="2"
                                                            >
                                                                 <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                                            </svg>
                                                       </button>
                                                  )}
                                             </div>
                                        </div>
                                   ))
                              )}
                         </div>

                         <div className="colleagues-progress">
                              <div className="progress-bar">
                                   <div
                                        className="progress-fill"
                                        style={{ width: `${Math.min(totalPercent, 100)}%` }}
                                   />
                              </div>
                              <div className="progress-labels">
                                   <span>{totalPercent}%</span>
                                   <span>{Math.max(0, 100 - totalPercent)}%</span>
                              </div>
                         </div>
                    </div>
               </div>
          </div>
     );
}