// src/modules/score_module/screen/score_history.screen.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useScore } from "../hooks/use-score";
import FilterModal from "../components/FilterModal";
import { convertToJalaliDateTime } from "../../../shared/utils/date";
import { GIFT_ROUTES } from "../../gift_module/routes";
import "../../../shared/styles/score.css";
import { ICONS } from "../../../shared/constants/icons";
import MyImage from "../../../shared/components/image-show";
import Pagination from "../../../shared/components/Pagination";
import { LEARN_ROUTES } from "../../learn_module/routes";

export default function ScoreHistoryScreen() {
     const navigate = useNavigate();
     const { balance, logs, loading, filters, setFilters, page, setPage, totalPages } = useScore();
     const [showFilter, setShowFilter] = useState(false);

     return (
          <>
               <Header title="سوابق امتیازات" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="score-body">


                    <div className="score-balance-card">
                         <span className="sbc-label">موجودی من:</span>
                         <div>
                              <span className="sbc-value mx-2">
                                   {balance ? balance.current_balance.toLocaleString("fa-IR") : "..."}
                              </span>
                              <MyImage src={ICONS.coin_40} className="" />
                         </div>
                    </div>


                    {/* ✅ دکمه‌های میانبر */}
                    <div className="score-actions-grid">
                         <div className="score-action-btn" onClick={() => navigate(GIFT_ROUTES.list)}>
                              <MyImage src={ICONS.gift} className="w__25" />
                              <span>دریافت هدیه</span>
                         </div>

                         <div className="score-action-btn" onClick={() => navigate(LEARN_ROUTES.list)}>
                              <MyImage src={ICONS.information} className="w__25" />
                              <span>راهنمای امتیاز گیری</span>
                         </div>
                    </div>

                    {/* ✅ هدر لیست و فیلتر */}
                    <div className="score-list-header">
                         <span className="slh-title">:: سوابق امتیاز </span>
                         <button className="slh-filter" onClick={() => setShowFilter(true)}>
                              فیلتر
                              {/* <MyImage src={ICONS.sort} className="w__30" /> */}
                         </button>
                    </div>

                    {/* ✅ لیست تراکنش‌ها */}
                    <div className="score-logs-list">
                         {loading && logs.length === 0 && (
                              <p className="text-center text-muted mt-4 fs-12">در حال بارگذاری...</p>
                         )}

                         {!loading && logs.length === 0 && (
                              <p className="text-center text-muted mt-4 fs-12">هیچ تراکنشی با این فیلترها یافت نشد.</p>
                         )}

                         {logs.map((log) => {
                              const isEarned = log.direction === "earned";
                              return (
                                   <div key={log.id} className={`score-log-item ${isEarned ? "earned" : "spent"}`}>
                                        <div className="sli-content">
                                             <span className="sli-title">{log.reason || log.code_display}</span>
                                             <span className="sli-date">{convertToJalaliDateTime(log.created_at)}</span>
                                        </div>
                                        <div className="sli-amount">
                                             <span className="fs-18">{log.amount.toLocaleString("fa-IR")} {isEarned ? "+" : "-"} </span>
                                             <MyImage src={ICONS.coin} className="w__25" />
                                        </div>
                                   </div>
                              );
                         })}

                         {/* ✅ کامپوننت صفحه‌بندی */}
                         {totalPages > 1 && (
                              <Pagination
                                   currentPage={page}
                                   totalPages={totalPages}
                                   onPageChange={setPage}
                                   disabled={loading}
                              />
                         )}
                    </div>
               </div>


               {/* مودال فیلتر */}
               <FilterModal
                    isOpen={showFilter}
                    onClose={() => setShowFilter(false)}
                    currentFilters={filters}
                    onApply={setFilters}
               />
          </>
     );
}