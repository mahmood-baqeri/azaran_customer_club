// src/modules/learn_module/screen/learns_list.screen.tsx

import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useLearns } from "../hooks/use-learns";
import { LEARN_ROUTES } from "../routes";
import { DOMAIN } from "../../../shared/constants/env";
import "../../../shared/styles/learn.css";
import MyImage from "../../../shared/components/image-show";
import { SUPPORT_ROUTES } from "../../support_module/routes";

export default function LearnsListScreen() {
     const navigate = useNavigate();
     const { learns, loading } = useLearns();

     const full = (p: string | null | undefined) => p ? (p.startsWith("http") ? p : `${DOMAIN}${p}`) : undefined;

     return (
          <>
               <Header title="آموزش باشگاه" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc"
                    action={
                         <span className="text-muted me-auto">۲ از ۷ دیده شده</span>
                    }
               />

               <div className="display-grid">
                    {loading && learns.length === 0 && (<p className="text-center text-muted mt-4">در حال بارگذاری...</p>)}

                    {/* ✅ گرید کارت‌ها */}
                    <div className="learn-grid">
                         {learns.map((item) => (
                              <div key={item.id} className={`learn-card ${item.size === 'full' ? 'card-full' : 'card-half'}`}
                                   onClick={() => navigate(LEARN_ROUTES.detail(item.id))} >

                                   {item.time && (
                                        <span className="lc-badge">{item.time} دقیقه </span>
                                   )}

                                   <MyImage src={full(item.photo)} className="w-100" alt={item.title} />

                                   <div className="p-2 lc-content">
                                        {item.caption != "" && <span className="lc-caption">{item.caption}</span>}
                                        <h3 className="lc-title">{item.title}</h3>
                                        {item.sub_text && <p className="lc-sub">{item.sub_text}</p>}
                                   </div>


                              </div>
                         ))}
                    </div>

                    {/* ✅ دکمه پشتیبانی پایین صفحه */}
                    <button className="learn-support-btn fs-12" onClick={() => navigate(SUPPORT_ROUTES.create)}>
                         <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                         </svg>
                         سوالی دارید؟ با پشتیبانی تماس بگیرید
                    </button>
               </div>
          </>
     );
}