/* eslint-disable @typescript-eslint/no-explicit-any */
// src/modules/visit_module/screen/visit_detail.screen.tsx

import { useNavigate, useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useVisitDetail } from "../hooks/use-visit-detail";
import VisitTimeline from "../components/VisitTimeline";
import "../../../shared/styles/visit.css";
import VisitCard from "../components/VisitCard";
import { visitRepository } from "../repository/visit.repository";
import { DeleteModal } from "../../../shared/components/modal/deleteModal";
import { useState } from "react";
import { VISIT_ROUTES } from "../routes";

export default function VisitDetailScreen() {
     const { id } = useParams<{ id: string }>();
     const visitId = id ? Number(id) : null;
     const { visit, loading } = useVisitDetail(visitId);


     const navigate = useNavigate();

     const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
     const [isDeleting, setIsDeleting] = useState(false);

     const handleCancelRequest = async (requestId: number) => {
          try {
               setIsDeleting(true);
               const isSuccess = await visitRepository.delete(requestId);

               if (isSuccess) {
                    setIsCancelModalOpen(false);
                    navigate(-1);
               }
          } catch (error: any) {
               console.error("خطا در لغو درخواست:", error);
               alert(error.message || "خطا در لغو درخواست");
          } finally {
               setIsDeleting(false);
          }
     };


     if (loading) {
          return (
               <>
                    <Header title="جزئیات درخواست" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <p className="text-center mt-5 text-muted fs-12">در حال دریافت اطلاعات...</p>
               </>
          );
     }

     if (!visit) {
          return (
               <>
                    <Header title="جزئیات درخواست" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <p className="text-center mt-5 fs-12">درخواست یافت نشد.</p>
               </>
          );
     }

     return (
          <>
               <Header title="جزئیات درخواست بازدید" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="display-grid">
                    <div>
                         <div className="visit-summary-card mb-4">
                              <VisitCard visit={visit} />
                         </div>

                         {/* ۳. نمایش مشخصات همراه (در صورت وجود) */}
                         {visit.have_companion && visit.companion && (
                              <div className="visit-companion-form mt-1 box___main">
                                   <h4 className="vcf-title">مشخصات همراه</h4>
                                   <div className="vsc-row" style={{ marginBottom: 8 }}>
                                        <span>نام و نام خانوادگی:</span>
                                        <strong>{visit.companion.name} {visit.companion.family}</strong>
                                   </div>
                                   <div className="vsc-row">
                                        <span>شماره موبایل:</span>
                                        <strong style={{ direction: "ltr" }}>{visit.companion.mobile}</strong>
                                   </div>
                              </div>
                         )}

                         <VisitTimeline visit={visit} />
                    </div>


                    {/* ۵. دکمه‌های عملیات */}
                    <div style={{ marginTop: 24 }}>
                         {visit.status === "rejected" && <a href={VISIT_ROUTES.create} className="btn___main">درخواست برای دوشنبه‌ی دیگر</a>}
                         {visit.status === "pending" && <button className="btn w-100 h__40 btn___danger" onClick={() => setIsCancelModalOpen(true)} disabled={isDeleting}>لغو درخواست</button>}
                    </div>
               </div>

               {/* 👈 اضافه کردن مودال به پایین صفحه */}
               <DeleteModal
                    isOpen={isCancelModalOpen}
                    onClose={() => setIsCancelModalOpen(false)}
                    onApply={handleCancelRequest}
                    id={visit.id}
                    title="لغو درخواست بازدید"
                    h1="آیا از لغو این درخواست اطمینان دارید؟"
                    p="با لغو این درخواست، سابقه آن حذف شده و امکان بازگردانی وجود ندارد."
               />
          </>
     );
}