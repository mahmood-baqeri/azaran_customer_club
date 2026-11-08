// src/modules/support_module/screen/tickets_list.screen.tsx

import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useTickets } from "../hooks/use-tickets";
import { SUPPORT_ROUTES } from "../routes";
import { convertToJalaliDateTime } from "../../../shared/utils/date";
import "../../../shared/styles/support.css";

export default function TicketsListScreen() {
     const navigate = useNavigate();
     const { tickets, loading } = useTickets();

     return (
          <>
               <Header
                    title="تیکت‌های من"
                    showBack
                    showLogo={false}
                    menuBg="f7f8fb"
                    action={
                         <a href={SUPPORT_ROUTES.create} className="header-action-btn">
                              <span className="color-primary fs-14 fw-400 me-1">تیکت جدید</span>
                         </a>
                    }
               />

               <div className="support-body" style={{ paddingBottom: 40 }}>
                    {loading && <p className="text-center mt-4">در حال بارگذاری...</p>}

                    {!loading && tickets.length === 0 && (
                         <p className="text-center text-muted mt-4">هنوز تیکتی ثبت نکرده‌اید.</p>
                    )}

                    <div className="support-tickets-list">
                         {tickets.map((t) => (
                              <div
                                   key={t.id}
                                   className="support-ticket-card"
                                   onClick={() => navigate(SUPPORT_ROUTES.detail(t.id))}
                              >
                                   <div className="st-header">
                                        <span className="st-subject">{t.subject}</span>
                                        <span className={`st-status ${t.status}`}>{t.status_display}</span>
                                   </div>
                                   <div className="st-footer">
                                        <span>{t.category_display}</span>
                                        <span>{convertToJalaliDateTime(t.last_message_at ?? "")}</span>
                                   </div>
                              </div>
                         ))}
                    </div>
               </div>
          </>
     );
}