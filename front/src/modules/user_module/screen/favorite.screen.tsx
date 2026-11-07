// front/src/modules/user_module/screen/favorite.screen.tsx

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../hooks/use-user";
import { userRepository } from "../repository/user.repository";
import Header from "../../../app/layouts/header";
import { MyNotification } from "../../../shared/utils/notification";
import { PROFILE_ROUTES } from "../routes";
import { getErrorMessage } from "../../../shared/api/errors";
import type { FavoriteQuestion, FavoriteAnswerValue } from "../interface/user.types";
import { FavoriteSlider } from "../components/FavoriteSlider";


// ==========================================
// صفحه  علایق و سلایق کاربر
// ==========================================
export default function FavoriteScreen() {
     const { user } = useUser();
     const navigate = useNavigate();

     const [questions, setQuestions] = useState<FavoriteQuestion[]>([]);
     const [loading, setLoading] = useState(true);
     const [savingId, setSavingId] = useState<number | null>(null);

     // State مربوط به صفحه‌بندی
     const [currentPage, setCurrentPage] = useState(0);
     const ITEMS_PER_PAGE = 4;

     // دریافت سوالات
     useEffect(() => {
          let mounted = true;
          const fetchQuestions = async () => {
               try {
                    setLoading(true);
                    const data = await userRepository.getFavoriteQuestions();
                    if (mounted) setQuestions(data);
               } catch (err) {
                    MyNotification("", getErrorMessage(err, "خطا در دریافت سوالات علاقه‌مندی"), "error");
               } finally {
                    if (mounted) setLoading(false);
               }
          };
          fetchQuestions();
          return () => {
               mounted = false;
          };
     }, []);

     // محاسبات صفحه‌بندی
     const totalPages = Math.ceil(questions.length / ITEMS_PER_PAGE);
     const currentQuestions = questions.slice(
          currentPage * ITEMS_PER_PAGE,
          (currentPage + 1) * ITEMS_PER_PAGE
     );

     // ذخیره پاسخ در بک‌اند (با هر کلیک)
     const handleAnswerChange = async (questionId: number, answer: FavoriteAnswerValue) => {
          setQuestions((prev) =>
               prev.map((q) =>
                    q.id === questionId
                         ? {
                              ...q,
                              user_answer: {
                                   id: q.user_answer?.id || 0,
                                   answer,
                                   answer_display: "",
                                   updated_at: new Date().toISOString(),
                              },
                         }
                         : q
               )
          );

          setSavingId(questionId);
          try {
               await userRepository.submitFavoriteAnswer({ question_id: questionId, answer });
          } catch (err) {
               MyNotification("", getErrorMessage(err, "خطا در ذخیره پاسخ"), "error");
          } finally {
               setSavingId(null);
          }
     };

     // دکمه بعدی
     const handleNext = () => {
          if (currentPage < totalPages - 1) {
               setCurrentPage((prev) => prev + 1);
               window.scrollTo({ top: 0, behavior: "smooth" }); // اسکرول به بالا هنگام تغییر صفحه
          }
     };

     // دکمه قبلی
     const handlePrev = () => {
          if (currentPage > 0) {
               setCurrentPage((prev) => prev - 1);
               window.scrollTo({ top: 0, behavior: "smooth" });
          }
     };

     // دکمه ذخیره (در صفحه آخر)
     const handleSave = () => {
          MyNotification("", "علایق و سلایق شما با موفقیت ذخیره شد.", "success");
          navigate(PROFILE_ROUTES.favorite); // یا هر مسیری که قرار است بعد از این مرحله برود
     };

     if (!user) return null;

     return (

          <>
               <Header
                    title="علایق و سلایق"
                    showBack={true}
                    showLogo={false}
                    menuBg="f7f8fb"
                    buttonBg="white"
                    action={
                         <span className="me-auto small fw-medium color-primary fs-12">
                              مرحله {currentPage + 1} از {totalPages || 1}
                         </span>
                    }
               />

               <div dir="rtl" className="bg-white1 pt-1">


                    {/* نوار پیشرفت داینامیک */}
                    <div className="d-flex gap-2 px-3">
                         {Array.from({ length: totalPages || 1 }).map((_, index) => (
                              <div
                                   key={index}
                                   className="rounded-pill flex-fill"
                                   style={{
                                        height: "6px",
                                        backgroundColor: index <= currentPage ? "#0d3b66" : "#DCECFC",
                                        transition: "background-color 0.3s",
                                   }}
                              />
                         ))}
                    </div>

                    {/* محتوای سوالات */}
                    <div className="px-0 mt-2" style={{ minHeight: "60vh" }}>
                         {loading ? (
                              <div className="d-flex justify-content-center py-5">
                                   <div className="spinner-border" style={{ color: "#0d3b66" }} role="status">
                                        <span className="visually-hidden">در حال بارگذاری...</span>
                                   </div>
                              </div>
                         ) : (
                              <div className="d-flex flex-column gap-1">
                                   {currentQuestions.map((q) => (
                                        <div
                                             key={q.id}
                                             className="card border-0"
                                             style={{

                                                  opacity: savingId === q.id ? 0.6 : 1,
                                                  transition: "opacity 0.2s",
                                             }}
                                        >
                                             <div className="card-body p-3">
                                                  <h3 className="fw-bold color-primary mb-2 fs-13" style={{ lineHeight: "1.8" }}>
                                                       {q.question}
                                                  </h3>
                                                  <FavoriteSlider
                                                       options={q.answer_options}
                                                       value={q.user_answer?.answer}
                                                       onChange={(val) => handleAnswerChange(q.id, val)}
                                                  />
                                             </div>
                                        </div>
                                   ))}
                              </div>
                         )}
                    </div>

                    {/* دکمه‌های پایین صفحه (ثابت) */}
                    <div
                         className=" bottom-0 start-0 end-0 p-3"
                         style={{
                              zIndex: 1050,
                              background: "linear-gradient(to top, #f8f9fa 80%, transparent)",
                         }}
                    >
                         <div className="d-flex gap-2">
                              {/* دکمه قبلی (فقط اگر صفحه اول نباشیم) */}
                              {currentPage > 0 && (
                                   <button
                                        onClick={handlePrev}
                                        className="btn py-2 fw-bold"
                                        style={{
                                             backgroundColor: "#ffffff",
                                             color: "#0d3b66",
                                             border: "1px solid #0d3b66",
                                             borderRadius: "12px",
                                             fontSize: "16px",
                                             flex: 1,
                                        }}
                                   >
                                        قبلی
                                   </button>
                              )}

                              {/* دکمه بعدی یا ذخیره */}
                              <button
                                   onClick={currentPage === totalPages - 1 ? handleSave : handleNext}
                                   className="btn py-2 fw-bold text-white shadow-sm"
                                   style={{
                                        backgroundColor: "#0d3b66",
                                        borderRadius: "12px",
                                        fontSize: "16px",
                                        flex: 2, // دکمه بعدی/ذخیره کمی عریض‌تر باشد بهتر است
                                   }}
                              >
                                   {currentPage === totalPages - 1 ? "ذخیره" : "بعدی"}
                              </button>
                         </div>
                    </div>
               </div>
          </>
     );
}