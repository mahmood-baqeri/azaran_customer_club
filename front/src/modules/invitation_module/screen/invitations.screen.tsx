// src/modules/invitation_module/screen/invitations.screen.tsx

import Header from "../../../app/layouts/header";
import { useUser } from "../../user_module/hooks/use-user";
import { useInvitations } from "../hooks/use-invitations";
import { DOMAIN } from "../../../shared/constants/env";
import { MyNotification } from "../../../shared/utils/notification";
import "../../../shared/styles/invitation.css";
import { usePageContentClass } from "../../../shared/hooks/use-page-content-class";
import { ICONS } from "../../../shared/constants/icons";
import MyImage from "../../../shared/components/image-show";

export default function InvitationsScreen() {
     usePageContentClass("review-active-wrapper");

     const { user } = useUser();
     const { invitations, loading } = useInvitations();

     // محاسبه تعداد دعوت‌شدگان و سکه‌های گرفته شده
     const totalInvited = invitations.length;
     const totalRewarded = invitations.filter((inv) => inv.is_rewarded).length;
     const totalCoins = totalRewarded * 20; // فرض: به ازای هر نفر ۲۰ سکه

     const referralCode = user?.referral_code || "-----";

     const full = (p: string | null | undefined) =>
          p ? (p.startsWith("http") ? p : `${DOMAIN}${p}`) : undefined;

     const handleCopyCode = () => {
          if (!referralCode) return;
          navigator.clipboard.writeText(referralCode);
          MyNotification("", "کد معرف کپی شد", "success");
     };

     const handleSendSms = () => {
          // ⚠️ این وب‌سرویس هنوز در بک‌اند نیست. فعلاً فقط پیام موفقیت نمایش می‌دهیم.
          MyNotification("", "لینک دعوت برای همکاران شما پیامک خواهد شد (به‌زودی)", "info");
     };

     return (
          <>
               <Header showBack showLogo={false} menuBg="transparent" buttonBg="white" />

               <div className="inv-body p-0">

                    <MyImage src={ICONS.invitation_header} className="w-100 banner" />


                    <div className="p-3">
                         {/* ✅ کارت خلاصه (Summary Card) */}
                         <div className="inv-card">
                              <div className="inv-card-header">
                                   <h2 className="inv-card-title fs-12 fw-600">همکاران دعوت شده: {totalInvited.toLocaleString("fa-IR")}</h2>
                                   {totalCoins > 0 && (
                                        <span className="inv-badge">
                                             <MyImage src={ICONS.coin} className="w__20 ms-1" />
                                             <span className="fs-11 color-primary fw-500">{totalCoins.toLocaleString("fa-IR")} سکه دریافت شد</span>

                                        </span>
                                   )}
                              </div>

                              <div className="inv-avatars-row">
                                   {loading ? (
                                        <p className="text-muted fs-12">در حال بارگذاری...</p>
                                   ) : invitations.length === 0 ? (
                                        <p className="text-muted fs-12">هنوز کسی را دعوت نکرده‌اید.</p>
                                   ) : (
                                        invitations.map((inv) => (
                                             <div key={inv.id} className="inv-avatar-item">
                                                  <div className="inv-avatar-wrap">
                                                       {inv.user?.avatar ? (
                                                            <img src={full(inv.user.avatar)} alt={inv.user.name} className="inv-avatar-img" />
                                                       ) : (
                                                            <div className="inv-avatar-placeholder">
                                                                 <svg width="24" height="24" viewBox="0 0 24 24" fill="#a0aec0" stroke="none"><circle cx="12" cy="8" r="4" /><path d="M4 20c0-4.4 3.6-8 8-8s8 3.6 8 8" /></svg>
                                                            </div>
                                                       )}

                                                       {/* نشان تایید (تیک سبز) */}
                                                       {inv.is_registered && (
                                                            <div className="inv-avatar-check">
                                                                 <svg width="12" height="12" viewBox="0 0 24 24" fill="#fff" stroke="#10b981" strokeWidth="3"><polyline points="20 6 9 17 4 12" /></svg>
                                                            </div>
                                                       )}
                                                  </div>

                                                  {/* نمایش شماره یا نام */}
                                                  <span className="inv-avatar-name">
                                                       {inv.user?.name || inv.invited_mobile}
                                                  </span>

                                                  {/* نمایش سکه برای جوایز */}
                                                  {inv.is_rewarded && (
                                                       <div className="inv-avatar-coin">
                                                            <img src="/assets/coin_15.png" alt="coin" width={12} height={12} />
                                                            <span>۲۰</span>
                                                       </div>
                                                  )}
                                             </div>
                                        ))
                                   )}
                              </div>

                              <p className="inv-hint">
                                   بعد از تایید مدارک شغلی همکاران معرفی شده، ۲۰ امتیاز به حساب شما واریز می‌شود.
                              </p>
                         </div>



                         {/* ✅ کد معرف */}
                         <div className="inv-code-box">
                              <span className="inv-code-label">کد معرف:</span>
                              <div className="inv-code-value" onClick={handleCopyCode}>
                                   <span style={{ direction: "ltr" }}>{referralCode}</span>
                                   <MyImage src={ICONS.copy} className="w__20" />
                              </div>
                         </div>



                         {/* ✅ دکمه ارسال پیامک */}
                         <button className="auth-btn mt-5" onClick={handleSendSms}>
                              ارسال پیامک دعوت
                         </button>

                    </div>
               </div>
          </>
     );
}