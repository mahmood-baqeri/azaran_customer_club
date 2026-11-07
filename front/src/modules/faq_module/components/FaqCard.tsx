// src/modules/faq_module/components/FaqCard.tsx
import { useNavigate } from "react-router-dom";
import { convertToJalaliDateMonth } from "../../../shared/utils/date";
import type { FAQ } from "../interface/faq.types";
import { FAQ_ROUTES } from "../routes";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

export default function FaqCard({ faq }: { faq: FAQ }) {
     const navigate = useNavigate();

     return (
          <div className="faq-card color-primary" onClick={() => navigate(FAQ_ROUTES.detail(faq.id))}>
               <div className="faq-card-header">
                    <span className="faq-user fs-11">{faq.user.name}</span>
                    <span className="faq-date fs-10">{convertToJalaliDateMonth(faq.created_at ?? "")}</span>
               </div>
               <p className="faq-question">{faq.question}</p>
               <div className="faq-card-footer">
                    <span className="faq-answers-count">
                         <MyImage src={ICONS.messages_2} className="w__20" />
                         {faq.answers_count} پاسخ
                    </span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6" /></svg>

               </div>
          </div>
     );
}