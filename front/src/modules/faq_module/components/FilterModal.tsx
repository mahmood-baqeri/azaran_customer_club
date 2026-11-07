// src/modules/faq_module/components/FilterModal.tsx

import type { FaqFilterType } from "../interface/faq.types";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     currentSort: FaqFilterType;
     onSelect: (sort: FaqFilterType) => void;
}

const FILTERS: { id: FaqFilterType; label: string }[] = [
     { id: "newest", label: "جدیدترین سوالات" },
     { id: "most_answered", label: "بیشترین پاسخ" },
     { id: "my_questions", label: "سوالات من" },
];

export default function FilterModal({ isOpen, onClose, currentSort, onSelect }: Props) {
     if (!isOpen) return null;

     return (
          <div className="filter-modal-overlay" onClick={onClose}>
               <div className="filter-modal-sheet" onClick={(e) => e.stopPropagation()}>
                    <div className="filter-modal-header">
                         <h2>مرتب‌سازی و فیلتر</h2>
                         <button className="close-btn" onClick={onClose}>&times;</button>
                    </div>

                    <div className="filter-modal-body">
                         {FILTERS.map((f) => (
                              <label key={f.id} className="filter-radio-row">
                                   <span>{f.label}</span>
                                   <input
                                        type="radio"
                                        name="faq_filter"
                                        checked={currentSort === f.id}
                                        onChange={() => {
                                             onSelect(f.id);
                                             onClose();
                                        }}
                                   />
                                   <div className={`custom-radio-faq ${currentSort === f.id ? "checked" : ""}`} />
                              </label>
                         ))}
                    </div>
               </div>
          </div>
     );
}