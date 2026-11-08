// src/modules/gallery_module/screen/gallery_detail.screen.tsx

import { useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useGalleryDetail } from "../hooks/use-gallery-detail";
import { useLikeGallery } from "../hooks/use-like-gallery";
import { DOMAIN } from "../../../shared/constants/env";
import "../../../shared/styles/gallery.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

export default function GalleryDetailScreen() {
     const { id } = useParams<{ id: string }>();
     const galleryId = id ? Number(id) : null;
     const { gallery, loading, setGallery } = useGalleryDetail(galleryId);
     const { toggleLike, loadingId } = useLikeGallery();

     if (loading) {
          return (
               <>
                    <Header title="عکس نصب" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <p className="text-center mt-5 text-muted">در حال دریافت اطلاعات...</p>
               </>
          );
     }

     if (!gallery) {
          return (
               <>
                    <Header title="عکس نصب" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />
                    <p className="text-center mt-5">اطلاعات تصویر یافت نشد.</p>
               </>
          );
     }

     const full = (p: string | null | undefined) =>
          p ? (p.startsWith("http") ? p : `${DOMAIN}${p}`) : undefined;

     const handleLike = async () => {
          const res = await toggleLike(gallery.id);
          if (res) {
               setGallery((prev) =>
                    prev ? { ...prev, is_liked_by_me: res.is_liked, likes_count: res.likes_count } : null
               );
          }
     };

     return (
          <>
               <Header title="عکس نصب" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div style={{ paddingTop: 10 }}>
                    <div className="gallery-detail-image">
                         <img src={full(gallery.photo)} alt="gallery" />
                    </div>

                    <h2 className="gallery-detail-title">{gallery.caption || "بدون عنوان"}</h2>

                    <div className="gallery-detail-footer">
                         <div className="gallery-detail-user">
                              <span>{gallery.user?.name || "کاربر"}</span>
                              <span className="g-loc">
                                   <MyImage src={ICONS.location_2} className="w__20" />
                                   {gallery.location || "نامشخص"}
                              </span>
                         </div>

                         <button className="gallery-like-btn" onClick={handleLike} disabled={loadingId === gallery.id} >
                              <span className="color-primary">
                                   {gallery.likes_count.toLocaleString("fa-IR")}
                              </span>

                              <svg width="24" height="24" viewBox="0 0 24 24" fill={gallery.is_liked_by_me ? "#f44336" : "none"} stroke={gallery.is_liked_by_me ? "#f44336" : "#14306b"} strokeWidth="2">
                                   <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                              </svg>
                         </button>
                    </div>
               </div>
          </>
     );
}