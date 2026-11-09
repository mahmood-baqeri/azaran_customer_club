// src/modules/review_module/screen/review.screen.tsx

import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useReview } from "../hooks/use-review";
import { reviewRepository } from "../repository/review.repository";
import { MyNotification } from "../../../shared/utils/notification";
import type { AnswerValue, SubmitReviewPayload } from "../interface/review.types";
import "../../../shared/styles/review.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import { usePageContentClass } from "../../../shared/hooks/use-page-content-class";

// تعریف گزینه‌های نظرسنجی
const OPTIONS: { value: AnswerValue; label: string; background: string; svg: React.ReactNode }[] = [
     { value: "very_little", label: "خیلی ناراضی", background: "#ff8080", svg: <MyImage src={ICONS.emoji_png_001} className="w__30 faq-replay-icon" /> },
     { value: "little", label: "ناراضی", background: "#F8BCBC", svg: <MyImage src={ICONS.emoji_png_002} className="w__30 faq-replay-icon" /> },
     { value: "average", label: "متوسط", background: "#feea8b", svg: <MyImage src={ICONS.emoji_png_003} className="w__30 faq-replay-icon" /> },
     { value: "a_lot", label: "راضی", background: "#CFF9F6", svg: <MyImage src={ICONS.emoji_png_004} className="w__30 faq-replay-icon" /> },
     { value: "very_much", label: "خیلی راضی", background: "#8ceae3", svg: <MyImage src={ICONS.emoji_svg_005} className="w__30 faq-replay-icon" /> },
];

const QUESTIONS_PER_PAGE = 3;

export default function ReviewScreen() {
     usePageContentClass("review-active-wrapper");

     const navigate = useNavigate();
     const { questions, loading } = useReview();

     // ✅ استیت صفحه فعلی (به جای سوال فعلی)
     const [currentPage, setCurrentPage] = useState(0);
     const [answers, setAnswers] = useState<Record<number, AnswerValue>>({});
     const [submitting, setSubmitting] = useState(false);

     const totalPages = Math.ceil(questions.length / 3);

     // استخراج سوالات مربوط به صفحه فعلی
     const currentQuestions = useMemo(() => {
          const start = currentPage * QUESTIONS_PER_PAGE;
          return questions.slice(start, start + QUESTIONS_PER_PAGE);
     }, [questions, currentPage]);


     if (loading) {
          return (
               <>
                    <Header title="نظرسنجی" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <p className="text-center mt-5 text-muted">در حال دریافت سوالات...</p>
               </>
          );
     }

     if (questions.length === 0) {
          return (
               <>
                    <Header title="نظرسنجی" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <div className="review-empty-state">
                         <div className="res-icon">✨</div>
                         <h2>با تشکر از شما</h2>
                         <p>شما به تمام سوالات نظرسنجی پاسخ داده‌اید.</p>
                         <button className="auth-btn mt-4" onClick={() => navigate("/")}>بازگشت به صفحه اصلی</button>
                    </div>
               </>
          );
     }

     // آیا کاربر به تمام سوالات این صفحه پاسخ داده است؟
     const isCurrentPageValid = currentQuestions.every(q => answers[q.id]);
     const isLastPage = currentPage === totalPages - 1;

     const handleSelect = (questionId: number, value: AnswerValue) => {
          setAnswers((prev) => ({ ...prev, [questionId]: value }));
     };

     const handleNext = () => {
          if (!isCurrentPageValid) {
               MyNotification("", "لطفاً به تمام سوالات این صفحه پاسخ دهید", "error");
               return;
          }

          if (isLastPage) {
               handleSubmit();
          } else {
               setCurrentPage((p) => p + 1);
               window.scrollTo(0, 0); // اسکرول به بالا در صفحه بعد
          }
     };

     const handlePrev = () => {
          if (currentPage > 0) {
               setCurrentPage((p) => p - 1);
               window.scrollTo(0, 0);
          }
     };

     const handleSubmit = async () => {
          const payload: SubmitReviewPayload[] = Object.entries(answers).map(([id, ans]) => ({
               question_id: Number(id),
               answer: ans,
          }));

          setSubmitting(true);
          try {
               await reviewRepository.submitAnswers(payload);
               MyNotification("", "نظرسنجی شما با موفقیت ثبت شد", "success");
               navigate("/");
          } catch (err: unknown) {
               let msg = "خطا در ثبت نظرسنجی";
               if (err instanceof Error) msg = err.message;
               MyNotification("خطا", msg, "error");
          } finally {
               setSubmitting(false);
          }
     };


     return (
          <>
               <Header showBack showLogo={false} menuBg="transparent" buttonBg="white" />

               <div className="w-100">
                    <MyImage src={ICONS.satisfaction_header} className="ص-100" />
               </div>

               <div className="review-body">
                    {/* تصویر بالای صفحه */}

                    {/* ✅ اسلایدر (نوار پیشرفت طبق تصویر) */}
                    <div className="review-progress-segments">
                         {Array.from({ length: totalPages }).map((_, idx) => (
                              <div
                                   key={idx}
                                   className={`rp-segment ${idx <= currentPage ? "active" : ""}`}
                              />
                         ))}
                    </div>

                    {/* ✅ کارت سوالات (۳ سوال در هر صفحه) */}
                    <div className="review-questions-list">
                         {currentQuestions.map((q) => {
                              const selectedAnswer = answers[q.id];

                              return (
                                   <div key={q.id} className="review-card">
                                        <div className="review-question-header">
                                             <span className="rq-arrow">◀</span>
                                             <h3 className="rq-text">{q.question}</h3>
                                        </div>

                                        <div className="review-options">
                                             {OPTIONS.map((opt) => {
                                                  const isSelected = selectedAnswer === opt.value;
                                                  return (
                                                       <div key={opt.value}
                                                            className={`review-option ${isSelected ? "selected" : ""}`}
                                                            onClick={() => handleSelect(q.id, opt.value)} >

                                                            <div className="ro-icon"
                                                                 style={{
                                                                      color: isSelected ? "" : "#a0aec0",
                                                                      background: isSelected ? `${opt.background}` : "#fff" // 15% opacity
                                                                 }}
                                                            >
                                                                 {opt.svg}
                                                            </div>
                                                            <span className="ro-label">{opt.label}</span>
                                                       </div>
                                                  );
                                             })}
                                        </div>
                                   </div>
                              );
                         })}
                    </div>
               </div>

               {/* ✅ دکمه‌های ناوبری */}
               <div className="review-actions">
                    <button
                         className="review-btn secondary"
                         onClick={handlePrev}
                         disabled={currentPage === 0 || submitting}
                    >
                         <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M9 18l6-6-6-6" />
                         </svg>
                         قبلی
                    </button>


                    <button
                         className="review-btn primary"
                         onClick={handleNext}
                         disabled={submitting}
                    >
                         {isLastPage
                              ? (submitting ? "در حال ارسال..." : "ثبت نهایی")
                              : "بعدی"}
                         {!isLastPage && (
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                   <path d="M15 18l-6-6 6-6" />
                              </svg>
                         )}
                    </button>

               </div>
          </>
     );
}