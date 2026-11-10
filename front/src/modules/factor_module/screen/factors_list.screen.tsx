// src/modules/factor_module/screen/factors_list.screen.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useFactors } from "../hooks/use-factors";
import { factorRepository } from "../repository/factor.repository";
import { MyNotification } from "../../../shared/utils/notification";
import { convertToJalaliDate } from "../../../shared/utils/date";
import { FACTOR_ROUTES } from "../routes";
import { DOMAIN } from "../../../shared/constants/env";
import "../../../shared/styles/project.css";
import { DeleteModal } from "../../../shared/components/modal/deleteModal";

export default function FactorsListScreen() {
     const navigate = useNavigate();
     const { factors, loading, refresh } = useFactors();
     const [deletingId, setDeletingId] = useState<number | null>(null);

     const handleDelete = async (id: number) => {
          setDeletingId(id);
          try {
               await factorRepository.deleteFactor(id);
               MyNotification("", "فاکتور با موفقیت حذف شد", "success");
               refresh();
          } catch (err: unknown) {
               let msg = "خطا در حذف فاکتور";
               if (err instanceof Error) msg = err.message;
               MyNotification("خطا", msg, "error");
          } finally {
               setDeletingId(null);
          }
     };

     // ✅ کدوم مودال بازه (null = هیچ‌کدام)
     const [deleteId, setDeleteId] = useState<number | null>(null);

     if (loading) return <p className="text-center mt-5">در حال بارگذاری...</p>;

     return (
          <>
               <Header
                    title="فاکتورهای من"
                    showBack
                    showLogo={false}
                    menuBg="f7f8fb" buttonBg="e8eefc"
                    action={
                         <a href={FACTOR_ROUTES.create} className="header-action-btn">
                              <span className="color-primary fw-400 me-1">ثبت فاکتور</span>
                         </a>
                    }
               />

               <div className="proj-body" style={{ paddingBottom: 40 }}>
                    <div className="proj-history-list">
                         {factors.length === 0 ? (
                              <p className="text-center text-muted mt-4">هنوز فاکتوری ثبت نکرده‌اید.</p>
                         ) : (
                              factors.map(f => {
                                   const isEditable = f.status === 'pending';
                                   const isDeletable = f.status === 'pending';
                                   const isDeleting = deletingId === f.id;

                                   return (
                                        <div key={f.id} className="proj-history-card">
                                             <div className="ph-header">
                                                  <span className="ph-title">فاکتور {f.invoice_number ? `#${f.invoice_number}` : `#${f.id}`}</span>
                                                  <span className={`ph-status ${f.status}`}>{f.status_display}</span>
                                             </div>

                                             <div style={{ display: 'flex', gap: 10, marginTop: 10, alignItems: 'center' }}>
                                                  <div style={{ width: 50, height: 50, borderRadius: 8, overflow: 'hidden', background: '#f4f5f9' }}>
                                                       {f.photo && <img src={f.photo.startsWith("http") ? f.photo : `${DOMAIN}${f.photo}`} alt="factor" style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
                                                  </div>
                                                  <div>
                                                       <div style={{ fontSize: 12, color: "#14306b", fontWeight: 700 }}>
                                                            مبلغ: {f.amount?.toLocaleString("fa-IR")} ریال
                                                       </div>
                                                       <div className="ph-footer" style={{ marginTop: 4 }}>
                                                            <span>تاریخ ثبت: {convertToJalaliDate(f.created_at ?? "")}</span>
                                                       </div>
                                                  </div>
                                             </div>

                                             <div className="ph-actions">
                                                  {isEditable && (
                                                       <button
                                                            type="button"
                                                            className="ph-btn ph-btn-edit"
                                                            onClick={(e) => {
                                                                 e.stopPropagation();
                                                                 navigate(FACTOR_ROUTES.edit(f.id));
                                                            }}
                                                       >
                                                            ویرایش
                                                       </button>
                                                  )}

                                                  {isDeletable && (
                                                       <button
                                                            type="button"
                                                            className="ph-btn ph-btn-delete"
                                                            disabled={isDeleting}
                                                            onClick={(e) => {
                                                                 e.stopPropagation();
                                                                 setDeleteId(f.id);   // ✅ باز کردن مودال
                                                            }}
                                                       >
                                                            {isDeleting ? 'در حال حذف...' : 'حذف'}
                                                       </button>
                                                  )}
                                             </div>

                                        </div>
                                   );
                              })
                         )}
                    </div>
               </div>


               <DeleteModal
                    isOpen={deleteId !== null}
                    id={deleteId ?? 0}
                    onClose={() => setDeleteId(null)}
                    onApply={handleDelete}
               />

          </>
     );
}