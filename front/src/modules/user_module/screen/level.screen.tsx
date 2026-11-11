// src/modules/user_module/screen/level.screen.tsx

import Header from "../../../app/layouts/header";
import { useLevel } from "../hooks/use-level";
import "../../../shared/styles/level.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import { usePageContentClass } from "../../../shared/hooks/use-page-content-class";

export default function LevelProfileScreen() {
     usePageContentClass("review-active-wrapper");
     const { profile, loading } = useLevel();

     if (loading) {
          return (
               <>
                    <Header title="سطح من" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <p className="text-center mt-5 text-muted">در حال دریافت اطلاعات...</p>
               </>
          );
     }

     if (!profile) return null;

     const { levelInfo } = profile;
     const isOstadkar = levelInfo.current_level === "ostadkar";

     return (
          <>
               <Header title="" showBack showLogo={false} menuBg="transparent" buttonBg="white" />

               <div className="level-body">
                    {/* هدر */}
                    <div className="level-header">
                         <div className="lh-avatar">
                              {isOstadkar ? <MyImage src={ICONS.ostadkar_2} className="w__100" /> : <MyImage src={ICONS.ostadkar_1} className="w__100" />}

                         </div>
                         <div className="lh-info">
                              <span className="lh-name">سطح شما: {levelInfo.current_level_display}</span>

                              {/* نوار پیشرفت */}
                              <div className="lh-progress-track">
                                   <div
                                        className="lh-progress-fill"
                                        style={{ width: `${levelInfo.progress_percentage}%` }}
                                   />
                                   {isOstadkar &&
                                        <MyImage src={ICONS.star_2} className="w__15 lh-progress-img" />
                                   }
                              </div>

                              <span className="lh-next-level">
                                   {isOstadkar
                                        ? "شما جزو ۱۰٪ برتر باشگاه هستید"
                                        : `${levelInfo.points_needed_for_next.toLocaleString("fa-IR")} امتیاز تا سطح استادکار`}
                              </span>
                         </div>
                    </div>

                    {/* مزایای سطح فعلی */}
                    <div className="level-section mt-3">
                         <h3 className="level-section-title">مزایای سطح فعلی شما</h3>
                         <div className="perks-list">
                              {profile.activePerks.map((perk) => (
                                   <a key={perk.id} className="perk-item active" href={perk.href}>
                                        <MyImage src={perk.icon} className="w__20 perk-icon" />
                                        <span className="perk-title fw-600">{perk.title}</span>
                                        {perk.help != "" && <span className="perk-help">{perk.help}</span>}
                                        <span className="perk-arrow">
                                             <i className="icon-arrow-left-2 color-primary fw-800"></i>
                                        </span>
                                   </a>
                              ))}
                         </div>
                    </div>

                    {/* مزایای قفل‌شده (فقط برای کاردان) */}
                    {profile.lockedPerks.length > 0 && (
                         <div className="level-section">
                              <p className="level-locked-hint">با رسیدن به سطح استادکار باز می‌شود</p>
                              <div className="perks-list">
                                   {profile.lockedPerks.map((perk) => (
                                        <div key={perk.id} className="perk-item locked">
                                             <MyImage src={perk.icon} className="w__20 perk-icon" />
                                             <span className="perk-title fw-600">{perk.title}</span>
                                             {perk.help != "" && <span className="perk-help">{perk.help}</span>}
                                        </div>
                                   ))}
                              </div>
                         </div>
                    )}
               </div>
          </>
     );
}