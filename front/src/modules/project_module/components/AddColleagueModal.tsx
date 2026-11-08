// src/modules/project_module/components/AddColleagueModal.tsx

import { useState } from "react";
import axios from "axios";
import { useProjectDetail } from "../hooks/use-project-detail";
import { projectRepository } from "../repository/project.repository";
import { MyNotification } from "../../../shared/utils/notification";
import MobileNumberInput from "../../../shared/components/inputs/Mobile";
import NumberInput from "../../../shared/components/inputs/Number";
import GlobalModal from "../../../shared/components/GlobalModal";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     projectId: number;
     onAdded?: () => void;
}

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

export default function AddColleagueModal({
     isOpen,
     onClose,
     projectId,
     onAdded,
}: Props) {
     const { project, refresh } = useProjectDetail(projectId);

     const [mobile, setMobile] = useState("");
     const [percent, setPercent] = useState<number | null>(10);
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

     const isMobileEmpty = mobile.replace(/\D/g, "").length === 0;
     const isPercentEmpty = percent === null;

     const isMobileOk = mobileValid && !isMobileEmpty;
     const isPercentOk = percentValid && !isPercentEmpty && !isFull;

     const canSubmit = isMobileOk && isPercentOk && !loading && !isLocked && !isFull;

     const showMobileError = !isMobileEmpty && !mobileValid;
     const showPercentError = !isPercentEmpty && !percentValid;

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
               onAdded?.();       // ✅ باعث رفرش صفحه زیرین هم می‌شود
               onClose();
          } catch (err) {
               MyNotification(
                    "خطا",
                    extractErrorMessage(err, "خطا در افزودن همکار"),
                    "error"
               );
          } finally {
               setLoading(false);
          }
     };

     return (
          < GlobalModal isOpen={isOpen} onClose={onClose} >

               <div onClick={(e) => e.stopPropagation()}>
                    <div className="proj-modal-header">
                         <h2>افزودن همکار</h2>
                         <button className="close-btn" onClick={onClose}>
                              &times;
                         </button>
                    </div>

                    <div className="proj-modal-body">
                         {isLocked ? (
                              <p
                                   style={{
                                        fontSize: 12,
                                        color: "#8792a8",
                                        textAlign: "center",
                                        padding: "20px 0",
                                   }}
                              >
                                   امکان افزودن همکار پس از تأیید پروژه وجود ندارد.
                              </p>
                         ) : (
                              <>
                                   <div
                                        className="add-colleague-form"
                                        style={{
                                             display: "flex",
                                             alignItems: "center",
                                             gap: 6,
                                             direction: "rtl",
                                             width: "100%",
                                        }}
                                   >
                                        <div className="w-50">
                                             <MobileNumberInput
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
                                             style={{
                                                  flex: "0 0 auto",
                                                  whiteSpace: "nowrap",
                                             }}
                                        >
                                             {loading ? "..." : "افزودن"}
                                        </button>
                                   </div>

                                   {(showMobileError ||
                                        showPercentError ||
                                        isFull) && (
                                             <div
                                                  style={{
                                                       color: "#d32f2f",
                                                       fontSize: 11,
                                                       marginTop: 6,
                                                       textAlign: "right",
                                                  }}
                                             >
                                                  {isFull &&
                                                       "سقف ۱۰۰٪ تکمیل است. برای افزودن، درصد یک همکار را کاهش دهید."}
                                                  {!isFull &&
                                                       showMobileError &&
                                                       showPercentError &&
                                                       " • "}
                                                  {!isFull &&
                                                       showPercentError &&
                                                       `درصد مجاز: ۱ تا ${remainingPercent}`}
                                             </div>
                                        )}

                                   <div
                                        className="colleagues-progress"
                                        style={{ marginTop: 20 }}
                                   >
                                        <div className="progress-bar">
                                             <div
                                                  className="progress-fill"
                                                  style={{
                                                       width: `${Math.min(
                                                            totalPercent,
                                                            100
                                                       )}%`,
                                                  }}
                                             />
                                        </div>
                                        <div className="progress-labels">
                                             <span>{totalPercent}%</span>
                                             <span>{remainingPercent}%</span>
                                        </div>
                                   </div>
                              </>
                         )}
                    </div>
               </div>

          </GlobalModal>
     );
}