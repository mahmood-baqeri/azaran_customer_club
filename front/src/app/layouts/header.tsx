// src/app/layouts/header.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSettings } from "../../modules/settings_module/hooks/use-settings";
import { useAuth } from "../../modules/auth_module/hooks/use-auth";
import { useUser } from "../../modules/user_module/hooks/use-user";
import MyImage from "../../shared/components/image-show";
import { DOMAIN } from "../../shared/constants/env";
import SidebarMenu from "./sidebar-menu";
import "../../shared/styles/header.css";
import { ICONS } from "../../shared/constants/icons";

type MenuBg = "white" | "f7f8fb" | "e8eefc";
type ButtonBg = "f7f8fb" | "white" | "e8eefc";

interface HeaderProps {
     /** عنوان وسط هدر (اختیاری) */
     title?: string;
     /** نمایش دکمه بازگشت (اختیاری، پیش‌فرض false) */
     showBack?: boolean;
     /** نمایش لوگو (اختیاری، پیش‌فرض true) */
     showLogo?: boolean;
     /** مسیر بازگشت؛ اگر مشخص نشود از تاریخچه مرورگر استفاده می‌شود */
     backTo?: string;
     /** رنگ پس‌زمینه دکمه منو (آواتار) — سفید یا شفاف */
     menuBg?: MenuBg;
     /** رنگ پس‌زمینه دکمه بازگشت — f7f8fb یا سفید */
     buttonBg?: ButtonBg;

     action?: React.ReactNode;
}

export default function Header({
     title,
     showBack = false,
     backTo,
     showLogo = true,
     menuBg = "white",
     buttonBg = "f7f8fb",
     action,
}: HeaderProps) {
     const navigate = useNavigate();
     const { settings } = useSettings();
     const { user } = useUser();
     const { logout } = useAuth();

     const [isMenuOpen, setIsMenuOpen] = useState(false);

     const closeMenu = () => setIsMenuOpen(false);

     const handleNavigate = (route: string): void => {
          setIsMenuOpen(false);
          setTimeout(() => navigate(route), 280);
     };

     const handleLogout = () => {
          setIsMenuOpen(false);
          setTimeout(() => logout(), 280);
     };

     const handleBack = (): void => {
          if (backTo) {
               navigate(backTo);
          } else {
               navigate(-1);
          }
     };

     const displayName = user?.name || "کاربر عزیز";

     const avatarRaw = user?.avatar ?? null;
     const displayAvatar: string | undefined =
          typeof avatarRaw === "string" && avatarRaw.length > 0
               ? avatarRaw.startsWith("http")
                    ? avatarRaw
                    : `${DOMAIN}${avatarRaw}`
               : undefined;

     const displayScore: string | number = user?.score && typeof user.score === "object" ? user.score.current_balance ?? 0 : 0;

     const logo = settings?.Logo;

     if (!user && !settings) {
          return (
               <div className="header-area">
                    <div className="container header-inner">
                         <div className="header-side header-side--start">
                              <div className="skeleton-avatar" />
                         </div>
                         <div className="header-center" />
                         <div className="header-side header-side--end">
                              <div className="skeleton-logo" />
                         </div>
                    </div>
               </div>
          );
     }

     return (
          <>
               <div className={`header-area header-area--${menuBg}`}>
                    <div className={`container header-inner ${!showBack ? "header-inner-grid" : ""}`}>
                         {/* سمت راست: دکمه بازگشت یا منو/آواتار */}
                         <div className="header-side header-side--start">
                              {showBack ? (
                                   <button
                                        type="button"
                                        className={`back-button back-button--${buttonBg}`}
                                        onClick={handleBack}
                                        aria-label="بازگشت"
                                   >
                                        <i className="icon-arrow-right-3 fw-800"></i>
                                   </button>
                              ) : (
                                   <div className="menu-btn">
                                        <button
                                             type="button"
                                             className="menu-toggle"
                                             onClick={() => setIsMenuOpen(true)}
                                             aria-label="باز کردن منو"
                                             aria-expanded={isMenuOpen}
                                        >
                                             <MyImage
                                                  src={displayAvatar}
                                                  className="rounded-100 user-avatar"
                                                  def="/assets/avatar.png"
                                                  alt="avatar"
                                             />
                                        </button>

                                        <div className="user-info">
                                             <h1>{user?.name}</h1>
                                             <div>
                                                  <span className="job">{user?.profile?.job_title}</span>
                                                  <span className="score">{user?.score?.current_balance}</span>
                                                  <img src={ICONS.coin_15} alt="coin" />
                                             </div>

                                        </div>
                                   </div>
                              )}
                         </div>

                         {/* وسط: تایتل */}
                         <div className="header-center">
                              {title ? (
                                   <h1 className="header-title color-primary" title={title}>
                                        {title}
                                   </h1>
                              ) : null}
                         </div>

                         {/* سمت چپ: لوگو */}
                         {showLogo ? <>
                              <div className="header-side header-side--end">
                                   <div className="logo-wrapper">
                                        <a href="/" aria-label="خانه">
                                             {logo && <img src={DOMAIN + logo} alt="logo" />}
                                        </a>
                                   </div>
                              </div>
                         </> : (action ? action : "")
                         }
                    </div>
               </div>

               <SidebarMenu
                    isOpen={isMenuOpen}
                    onClose={closeMenu}
                    displayName={displayName}
                    displayScore={displayScore}
                    displayAvatar={typeof avatarRaw === "string" ? avatarRaw : undefined}
                    onLogout={handleLogout}
                    onNavigate={handleNavigate}
               />
          </>
     );
}