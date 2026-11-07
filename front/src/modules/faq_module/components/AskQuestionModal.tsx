// src/modules/faq_module/components/AskQuestionModal.tsx

import { useState } from "react";
import type { Category } from "../interface/faq.types";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     categories: Category[];
     defaultCategoryId?: number;
     onSubmit: (question: string, categoryId: number) => Promise<boolean>;
     submitting: boolean;
}

export default function AskQuestionModal({
     isOpen,
     onClose,
     categories,
     defaultCategoryId,
     onSubmit,
     submitting,
}: Props) {
     const [question, setQuestion] = useState("");
     const [categoryId, setCategoryId] = useState<number | undefined>(defaultCategoryId || categories[0]?.id);

     if (!isOpen) return null;

     const handleSubmit = async () => {
          if (!question.trim() || !categoryId) return;
          const success = await onSubmit(question.trim(), categoryId);
          if (success) {
               setQuestion("");
               onClose();
          }
     };

     return (
          <div className="ask-modal-overlay" onClick={onClose}>
               <div className="ask-modal-sheet" onClick={(e) => e.stopPropagation()}>
                    <div className="ask-modal-header">
                         <h2>ثبت پرسش جدید</h2>
                         <button className="close-btn" onClick={onClose}>&times;</button>
                    </div>

                    <div className="ask-modal-body">
                         <div className="auth-label">دسته‌بندی سوال</div>
                         <div className="auth-select">
                              <select
                                   value={categoryId}
                                   onChange={(e) => setCategoryId(Number(e.target.value))}
                              >
                                   {categories.map((c) => (
                                        <option key={c.id} value={c.id}>
                                             {c.title}
                                        </option>
                                   ))}
                              </select>
                         </div>

                         <div className="auth-label" style={{ marginTop: 16 }}>متن سوال</div>
                         <textarea
                              className="auth-textarea"
                              value={question}
                              onChange={(e) => setQuestion(e.target.value)}
                              placeholder="سوال خود را با جزئیات کامل بنویسید..."
                              rows={4}
                         />
                    </div>

                    <div className="ask-modal-footer">
                         <button
                              className="auth-btn"
                              onClick={handleSubmit}
                              disabled={!question.trim() || !categoryId || submitting}
                         >
                              {submitting ? "در حال ثبت..." : "ثبت سوال و دریافت امتیاز"}
                         </button>
                    </div>
               </div>
          </div>
     );
}