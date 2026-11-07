// src/modules/faq_module/screen/faq-list.screen.tsx
import { useState } from "react";
import Header from "../../../app/layouts/header";
import { useCategories } from "../hooks/use-categories";
import { useFaqs } from "../hooks/use-faqs";
import { useCreateAction } from "../hooks/use-create-action";
import CategoryPills from "../components/CategoryPills";
import FaqCard from "../components/FaqCard";
import AskQuestionModal from "../components/AskQuestionModal";
import FilterModal from "../components/FilterModal"; // ✅ اضافه شد
import type { FaqFilterType } from "../interface/faq.types"; // ✅ اضافه شد
import "../../../shared/styles/faq.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

// برای نمایش متن روی دکمه فیلتر
const FILTER_LABELS: Record<FaqFilterType, string> = {
     newest: "جدیدترین",
     most_answered: "بیشترین پاسخ",
     my_questions: "سوالات من",
};

export default function FaqListScreen() {
     const { categories } = useCategories();
     const [selectedCat, setSelectedCat] = useState<number | undefined>(undefined);

     // ✅ استیت‌های فیلتر
     const [sort, setSort] = useState<FaqFilterType>("newest");
     const [showFilterModal, setShowFilterModal] = useState(false);

     // ✅ پاس دادن sort به هوک
     const { faqs, loading, refresh } = useFaqs(selectedCat, sort);
     const { submitting, askQuestion } = useCreateAction();
     const [showAskModal, setShowAskModal] = useState(false);

     const handleAsk = async (question: string, catId: number) => {
          const success = await askQuestion(question, catId);
          if (success) refresh();
          return success;
     };

     return (
          <>
               <Header title="پرسش از اهل فن" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="faq-body" style={{ paddingBottom: 100 }}>
                    <CategoryPills categories={categories} selectedId={selectedCat} onSelect={setSelectedCat} />

                    {/* ✅ دکمه فیلتر با متن داینامیک */}
                    <div className="faq-sort-row" onClick={() => setShowFilterModal(true)}>
                         <span>{FILTER_LABELS[sort]}</span>
                         <MyImage src={ICONS.sort} className="w__20" />
                    </div>

                    {loading && faqs.length === 0 && <p className="text-center text-muted mt-4">در حال بارگذاری…</p>}

                    <div className="faq-list">
                         {faqs.map((faq) => (
                              <FaqCard key={faq.id} faq={faq} />
                         ))}
                    </div>
               </div>

               <div className="faq-sticky-bottom">
                    <button className="faq-fake-input" onClick={() => setShowAskModal(true)}>
                         <span>سوال خود را بنویسید و امتیاز بگیرید</span>
                         <div className="faq-fake-send-btn">
                              <MyImage src={ICONS.edit} className="" />
                         </div>
                    </button>
               </div>

               <AskQuestionModal
                    isOpen={showAskModal}
                    onClose={() => setShowAskModal(false)}
                    categories={categories}
                    defaultCategoryId={selectedCat}
                    onSubmit={handleAsk}
                    submitting={submitting}
               />

               {/* ✅ مودال فیلتر */}
               <FilterModal
                    isOpen={showFilterModal}
                    onClose={() => setShowFilterModal(false)}
                    currentSort={sort}
                    onSelect={setSort}
               />
          </>
     );
}