// src/modules/gallery_module/screen/galleries_list.screen.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useGalleries } from "../hooks/use-galleries";
import { GALLERY_ROUTES } from "../routes";
import { DOMAIN } from "../../../shared/constants/env";
import "../../../shared/styles/gallery.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

const FILTERS = [
     { key: "popular", label: "محبوب‌ترین" },
     { key: "newest", label: "جدیدترین" },
     { key: "mine", label: "عکس‌های من" },
] as const;

export default function GalleriesListScreen() {
     const navigate = useNavigate();
     const [filter, setFilter] = useState<"popular" | "newest" | "mine">("popular");
     const { galleries, loading } = useGalleries(filter);

     const full = (p: string | null | undefined) =>
          p ? (p.startsWith("http") ? p : `${DOMAIN}${p}`) : undefined;

     return (
          <>
               <Header title="گالری مجریان" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="gallery-body">
                    <button className="btn___main mb-3" onClick={() => navigate(GALLERY_ROUTES.create)} >
                         <MyImage src={ICONS.camera_2} className="w__20" />
                         افزودن عکس
                    </button>

                    <p className="fs-12 text-center mb-4 mt-2">
                         عکس بهترین نصب هفته جایزه می‌گیرد
                    </p>

                    <div className="gallery-tabs">
                         {FILTERS.map((f) => (
                              <button
                                   key={f.key}
                                   className={`gallery-tab ${filter === f.key ? "active" : ""}`}
                                   onClick={() => setFilter(f.key)}
                              >
                                   {f.label}
                              </button>
                         ))}
                    </div>

                    {loading && galleries.length === 0 && (
                         <p className="text-center text-muted mt-4 fs-14">در حال بارگذاری...</p>
                    )}

                    {!loading && galleries.length === 0 && (
                         <p className="text-center text-muted mt-4 fs-14">تصویری برای نمایش وجود ندارد.</p>
                    )}

                    <div className="gallery-grid">
                         {galleries.map((g) => (
                              <div key={g.id} className="gallery-card" onClick={() => navigate(GALLERY_ROUTES.detail(g.id))} >
                                   <div className="gallery-img-wrapper">
                                        {g.photo && <img src={full(g.photo)} alt="gallery" loading="lazy" className="gallery" />}
                                        <div className="gallery-card-overlay">
                                             <div className="gallery-user-info">
                                                  <span className="g-name">{g.user?.name || "کاربر"}</span>
                                                  {g.location ?
                                                       <span className="g-loc">
                                                            <MyImage src={ICONS.location} className="w__10" />
                                                            {g.location}
                                                       </span>
                                                       : ""}
                                             </div>
                                             <div className="gallery-like-badge">
                                                  <svg width="14" height="14" viewBox="0 0 24 24" fill={g.is_liked_by_me ? "#f44336" : "#fff"} stroke={g.is_liked_by_me ? "#f44336" : "currentColor"} strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" /></svg>
                                                  <span>{g.likes_count}</span>
                                             </div>
                                        </div>
                                   </div>
                              </div>
                         ))}
                    </div>
               </div>
          </>
     );
}