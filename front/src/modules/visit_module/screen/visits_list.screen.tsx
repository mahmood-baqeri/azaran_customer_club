// src/modules/visit_module/screen/visits_list.screen.tsx

import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useVisits } from "../hooks/use-visits";

import { VISIT_ROUTES } from "../routes";
import "../../../shared/styles/visit.css";
import VisitCard from "../components/VisitCard";

export default function VisitsListScreen() {
     const navigate = useNavigate();
     const { visits, loading } = useVisits();

     return (
          <>
               <Header title="درخواست‌های بازدید" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="visit-body" style={{ paddingBottom: 40 }}>
                    {loading && <p className="text-center mt-4">در حال بارگذاری...</p>}

                    {!loading && visits.length === 0 && (
                         <div style={{ textAlign: "center", marginTop: 50 }}>
                              <p className="text-muted">هنوز درخواستی ثبت نکرده‌اید.</p>
                              <button className="btn___main mt-4" onClick={() => navigate(VISIT_ROUTES.create)}>
                                   ثبت درخواست جدید
                              </button>
                         </div>
                    )}

                    {!loading && visits.length > 0 && (
                         <>
                              <div className="visit-tickets-list">
                                   {visits.map((v) => (
                                        <div key={v.id} className="visit-list-card" onClick={() => navigate(VISIT_ROUTES.detail(v.id))}>
                                             <VisitCard visit={v} />
                                        </div>
                                   ))}
                              </div>

                              <button className="btn___main mt-4" onClick={() => navigate(VISIT_ROUTES.create)}>
                                   ثبت درخواست جدید
                              </button>
                         </>
                    )}
               </div>
          </>
     );
}