// src/modules/score_module/components/FilterModal.tsx

import { useState } from "react";
import { PersianDatePicker } from "../../../shared/utils/persianDatePicker";
import type { Direction, FilterState } from "../interface/score.types";
import GlobalModal from "../../../shared/components/GlobalModal";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     currentFilters: FilterState;
     onApply: (filters: FilterState) => void;
}

export default function FilterModal({ isOpen, onClose, currentFilters, onApply }: Props) {
     const [direction, setDirection] = useState<Direction | "all">(currentFilters.direction);
     const [startDate, setStartDate] = useState<Date | null>(currentFilters.startDate);
     const [endDate, setEndDate] = useState<Date | null>(currentFilters.endDate);

     const handleApply = () => {
          onApply({ direction, startDate, endDate });
          onClose();
     };

     const handleReset = () => {
          setDirection("all");
          setStartDate(null);
          setEndDate(null);
          onApply({ direction: "all", startDate: null, endDate: null });
          onClose();
     };

     return (
          // ✅ استفاده از GlobalModal به جای divهای دستی
          <GlobalModal isOpen={isOpen} onClose={onClose}>

               {/* بخش هدر */}
               <div className="score-modal-header">
                    <h2>فیلتر سوابق</h2>
                    <button className="close-btn" onClick={onClose}>&times;</button>
               </div>

               {/* بخش بدنه */}
               <div className="score-modal-body">
                    <label className="proj-label">نوع تراکنش</label>
                    <div className="score-filter-chips">
                         <button className={`s-chip ${direction === "all" ? "active" : ""}`} onClick={() => setDirection("all")}>
                              همه
                         </button>
                         <button className={`s-chip ${direction === "earned" ? "active" : ""}`} onClick={() => setDirection("earned")}>
                              کسب امتیاز
                         </button>
                         <button className={`s-chip ${direction === "spent" ? "active" : ""}`} onClick={() => setDirection("spent")}>
                              خرج امتیاز
                         </button>
                    </div>

                    <label className="proj-label fs-12" style={{ marginTop: 20 }}>از تاریخ</label>
                    <PersianDatePicker value={startDate} onChange={setStartDate} placeholder="انتخاب تاریخ شروع" />

                    <label className="proj-label fs-12" style={{ marginTop: 16 }}>تا تاریخ</label>
                    <PersianDatePicker value={endDate} onChange={setEndDate} placeholder="انتخاب تاریخ پایان" />
               </div>

               {/* بخش فوتر */}
               <div className="score-modal-footer">
                    <button className="btn___main" onClick={handleApply}>اعمال فیلتر</button>
                    <button className="auth-btn-link" onClick={handleReset} style={{ marginTop: 12 }}>
                         حذف فیلترها
                    </button>
               </div>

          </GlobalModal>
     );
}