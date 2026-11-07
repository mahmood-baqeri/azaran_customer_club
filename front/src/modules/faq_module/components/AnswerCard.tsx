// src/modules/faq_module/components/AnswerCard.tsx
import { useState } from "react";
import { convertToJalaliDateMonth } from "../../../shared/utils/date";
import { faqRepository } from "../repository/faq.repository";
import type { Answer } from "../interface/faq.types";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

interface Props {
     answer: Answer;
     onUpdate: () => void;
}

export default function AnswerCard({ answer, onUpdate }: Props) {
     const [loading, setLoading] = useState(false);

     const handleReact = async (type: "like" | "dislike") => {
          if (loading) return;
          setLoading(true);
          // اگر کاربر روی همان دکمه کلیک کرد، ری‌اکشن حذف می‌شود
          const newReaction = answer.my_reaction === type ? null : type;

          const success = await faqRepository.reactToAnswer(answer.id, newReaction);
          if (success) onUpdate();
          setLoading(false);
     };

     return (
          <div className="answer-card">
               <div className="answer-header">
                    <span className="answer-user fs-11">{answer.user.name}</span>
                    <span className="answer-date fs-10">{convertToJalaliDateMonth(answer.created_at ?? "")}</span>
               </div>
               <p className="answer-text">{answer.answer}</p>
               <div className="answer-footer">
                    <div className="reaction-box">
                         {/* دکمه لایک */}
                         <button
                              className={`reaction-btn ${answer.my_reaction === "like" ? "active-like" : ""}`}
                              onClick={() => handleReact("like")}
                              disabled={loading}
                         >
                              {answer.my_reaction === "like" ? <MyImage src={ICONS.like_2} className="w__15" /> : <MyImage src={ICONS.like_1} className="w__15" />}
                              {/* <span>{answer.likes_count}</span> */}
                         </button>

                         {/* دکمه دیس‌لایک */}
                         <button
                              className={`reaction-btn ${answer.my_reaction === "dislike" ? "active-dislike" : ""}`}
                              onClick={() => handleReact("dislike")}
                              disabled={loading}
                         >
                              {answer.my_reaction === "dislike" ? <MyImage src={ICONS.dislike_2} className="w__15" /> : <MyImage src={ICONS.dislike_1} className="w__15" />}
                              {/* <span>{answer.dislikes_count}</span> */}
                         </button>
                    </div>
               </div>
          </div>
     );
}