// src/app/layouts/sidebar-menu.tsx

import { useEffect } from "react";
import "../../shared/styles/sidebar-menu.css";
import MyImage from "../../shared/components/image-show";
import ImageCropModal from "../../shared/components/image-crop-modal";
import { useAvatarUpload } from "../../modules/user_module/hooks/use-avatar-upload";
import { DOMAIN } from "../../shared/constants/env";
import { useUser } from "../../modules/user_module/hooks/use-user";
import { NOTIFICATIONS_ROUTES } from "../../modules/notifications_module/routes";
import { ICONS } from "../../shared/constants/icons";

interface SidebarMenuProps {
     isOpen: boolean;
     onClose: () => void;
     displayName: string;
     displayScore: string | number;
     displayAvatar?: string;
     onLogout: () => void;
     onNavigate: (route: string) => void;
}

export default function SidebarMenu({
     isOpen,
     onClose,
     displayName,
     displayScore,
     displayAvatar,
     onLogout,
     onNavigate,
}: SidebarMenuProps) {
     const { user } = useUser();

     const {
          fileInputRef,
          cropImage,
          uploading,
          pickFile,
          handleFileChange,
          cancelCrop,
          confirmCrop,
     } = useAvatarUpload();

     // ✅ آواتار: اگر نسبی بود، DOMAIN اضافه شود
     // (پس Header باید فقط user.avatar خام را بفرستد)
     const rawAvatar = displayAvatar;
     const finalAvatar: string | undefined =
          typeof rawAvatar === "string" && rawAvatar.length > 0
               ? rawAvatar.startsWith("http") || rawAvatar.startsWith("blob:")
                    ? rawAvatar
                    : `${DOMAIN}${rawAvatar}`
               : undefined;

     // قفل اسکرول بدنه
     useEffect(() => {
          if (isOpen) document.body.style.overflow = "hidden";
          else document.body.style.overflow = "";
          return () => {
               document.body.style.overflow = "";
          };
     }, [isOpen]);

     // بستن با Escape
     useEffect(() => {
          const onKey = (e: KeyboardEvent) => {
               if (e.key === "Escape") onClose();
          };
          if (isOpen) window.addEventListener("keydown", onKey);
          return () => window.removeEventListener("keydown", onKey);
     }, [isOpen, onClose]);


     const MENU_ITEMS = [
          { label: "اعلان ها", text: "", icon: ICONS.notification, haveBadge: true, route: NOTIFICATIONS_ROUTES.all },
          { label: "اطلاعات کاربری", text: "", icon: ICONS.user_edit, haveBadge: false, route: "/profile" },
          { label: "سطح و مزایا", text: user?.profile?.job_title, icon: ICONS.level, haveBadge: false, route: "/profile" },
     ] as const;

     return (
          <>
               <button
                    type="button"
                    className={`menu-overlay ${isOpen ? "is-open" : ""}`}
                    onClick={onClose}
                    aria-label="بستن منو"
                    tabIndex={-1}
               />

               <aside
                    className={`app-sidebar ${isOpen ? "is-open" : ""}`}
                    role="dialog"
                    aria-modal="true"
                    aria-label="منوی کاربر"
               >
                    <div className="sidebar-head">
                         <div className="sidebar-avatar-wrap">
                              <MyImage
                                   src={finalAvatar}
                                   className="rounded-100 user-avatar"
                                   def="/assets/avatar.png"
                                   alt="avatar"
                              />
                              <button
                                   type="button"
                                   className="avatar-edit-btn"
                                   onClick={pickFile}
                                   disabled={uploading}
                                   aria-label="تغییر آواتار"
                              >
                                   {uploading ? "…" : <i className="icon-camera"></i>}
                              </button>
                              <input
                                   ref={fileInputRef}
                                   type="file"
                                   accept="image/*"
                                   hidden
                                   onChange={handleFileChange}
                              />
                         </div>
                         <p className="fs-10">افزودن عکس پروفایل</p>

                         <div className="info">
                              <p className="name">{displayName}</p>
                              <div>
                                   <p className="fs-12">موجودی من</p>
                                   <div>
                                        <span>{displayScore}</span>
                                        <img src="/assets/coin_17.png" alt="coin" />
                                   </div>
                              </div>
                         </div>
                    </div>

                    <div className="sidebar-body">
                         <ul className="sidenav-nav">
                              {MENU_ITEMS.map((item) => (
                                   <li key={item.label}>
                                        <button
                                             type="button"
                                             className="nav-link-btn color-primary"
                                             onClick={() => onNavigate(item.route)}
                                        >
                                             <MyImage
                                                  src={item.icon}
                                                  className=""
                                                  def="/assets/none.png"
                                                  alt="avatar"
                                                  width={22}
                                             />
                                             <span className="ml-auto">{item.label}</span>
                                             {item.text && <span className="_text">{item.text}</span>}
                                             {item.haveBadge && <i className="badge_element"></i>}

                                             <i className="icon-arrow-left-2 ml-0 fs-12 color-primary"></i>
                                        </button>
                                   </li>
                              ))}

                              <li className="nav-spacer" aria-hidden="true" />

                              <li className="logout-item">
                                   <button type="button" className="logout-btn" onClick={onLogout}>
                                        <i className="icon-arrow-right-1"></i>
                                        خروج از حساب
                                   </button>
                              </li>
                         </ul>
                    </div>
               </aside>

               {/* مودال کراپ */}
               {cropImage && (
                    <ImageCropModal
                         imageSrc={cropImage}
                         onCancel={cancelCrop}
                         onConfirm={confirmCrop}
                         aspect={1}
                    />
               )}
          </>
     );
}