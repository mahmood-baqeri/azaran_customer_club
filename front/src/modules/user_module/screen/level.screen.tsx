// src/modules/user_module/screen/level.screen.tsx

import Header from "../../../app/layouts/header";
import { useLevel } from "../hooks/use-level";
import "../../../shared/styles/level.css";

export default function LevelProfileScreen() {
     const { profile, loading } = useLevel();

     if (loading) {
          return (
               <>
                    <Header title="سطح من" showBack showLogo={false} menuBg="f7f8fb" />
                    <p className="text-center mt-5 text-muted">در حال دریافت اطلاعات...</p>
               </>
          );
     }

     if (!profile) return null;

     const { levelInfo } = profile;
     const isOstadkar = levelInfo.current_level === "ostadkar";

     return (
          <>
               <Header title="" showBack showLogo={false} menuBg="f7f8fb" />

               <div className="level-body">
                    {/* هدر */}
                    <div className="level-header">
                         <div className="lh-avatar">
                              <img src={profile.avatar || "/assets/avatar.png"} alt="avatar" />
                         </div>
                         <div className="lh-info">
                              <span className="lh-name">سطح شما: {levelInfo.current_level_display}</span>

                              {/* نوار پیشرفت */}
                              <div className="lh-progress-track">
                                   <div
                                        className="lh-progress-fill"
                                        style={{ width: `${levelInfo.progress_percentage}%` }}
                                   />
                              </div>

                              <span className="lh-next-level">
                                   {isOstadkar
                                        ? "شما جزو ۱۰٪ برتر باشگاه هستید"
                                        : `${levelInfo.points_needed_for_next.toLocaleString("fa-IR")} امتیاز تا سطح استادکار`}
                              </span>
                         </div>
                    </div>

                    {/* مزایای سطح فعلی */}
                    <div className="level-section">
                         <h3 className="level-section-title">مزایای سطح فعلی شما</h3>
                         <div className="perks-list">
                              {profile.activePerks.map((perk) => (
                                   <div key={perk.id} className="perk-item active">
                                        <div className="perk-icon">
                                             <i className={perk.icon_name}></i>
                                        </div>
                                        <span className="perk-title">{perk.title}</span>
                                        <span className="perk-arrow">
                                             <i className="icon-arrow-left-3"></i>
                                        </span>
                                   </div>
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
                                             <div className="perk-icon locked-icon">
                                                  <i className={perk.icon_name}></i>
                                             </div>
                                             <span className="perk-title">{perk.title}</span>
                                             <span className="perk-lock">
                                                  <i className="icon-lock"></i>
                                             </span>
                                        </div>
                                   ))}
                              </div>
                         </div>
                    )}
               </div>
          </>
     );
}