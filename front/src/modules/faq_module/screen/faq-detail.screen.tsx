// src/modules/faq_module/screen/faq-detail.screen.tsx

import { useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useFaqDetail } from "../hooks/use-faq-detail";
import { useCreateAction } from "../hooks/use-create-action";
import AnswerCard from "../components/AnswerCard";
import BottomInputBar from "../components/BottomInputBar";
import "../../../shared/styles/faq.css";
import FaqCard from "../components/FaqCard";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

export default function FaqDetailScreen() {
     const { id } = useParams<{ id: string }>();
     const faqId = id ? Number(id) : null;
     const { faq, loading, refresh } = useFaqDetail(faqId);
     const { submitting, submitAnswer } = useCreateAction();

     if (loading && !faq) {
          return (
               <>
                    <Header title="پاسخ به پرسش" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <p className="text-center text-muted mt-5">در حال بارگذاری…</p>
               </>
          );
     }

     if (!faq) return null;

     return (
          <>
               <Header title="پاسخ به پرسش" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="faq-body pb-5">


                    <FaqCard key={faq.id} faq={faq} />

                    <MyImage src={ICONS.replay} className="w__30 faq-replay-icon" />


                    <div className="answers-section">
                         {faq.answers?.map((ans) => (
                              <AnswerCard key={ans.id} answer={ans} onUpdate={refresh} />
                         ))}

                         {faq.answers?.length === 0 && (
                              <p className="text-center text-muted mt-4">هنوز پاسخی برای این سوال ثبت نشده است.</p>
                         )}
                    </div>
               </div>

               <BottomInputBar
                    placeholder="پاسخ خود را بنویسید و امتیاز بگیرید"
                    onSubmit={(text) => submitAnswer(faq.id, text)}
                    submitting={submitting}
               />
          </>
     );
}