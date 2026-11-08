// src/modules/gallery_module/screen/create_gallery.screen.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Header from "../../../app/layouts/header";
import { galleryRepository } from "../repository/gallery.repository";
import { MyNotification } from "../../../shared/utils/notification";
import { GALLERY_ROUTES } from "../routes";
import "../../../shared/styles/gallery.css";
import ImageUpload from "../../../shared/components/inputs/Image";
import TextInput from "../../../shared/components/inputs/Text";

export default function CreateGalleryScreen() {
     const navigate = useNavigate();
     const [photo, setPhoto] = useState<File | null>(null);
     const [caption, setCaption] = useState("");
     const [location, setLocation] = useState("");
     const [submitting, setSubmitting] = useState(false);


     const handleSubmit = async () => {
          if (!photo) {
               MyNotification("خطا", "لطفاً تصویر نصب را انتخاب کنید.", "error");
               return;
          }

          setSubmitting(true);
          try {
               const fd = new FormData();
               fd.append("photo", photo);
               if (caption.trim()) fd.append("caption", caption.trim());
               if (location.trim()) fd.append("location", location.trim());

               await galleryRepository.create(fd);
               MyNotification("", "عکس با موفقیت ارسال شد و در انتظار تایید است.", "success");
               navigate(GALLERY_ROUTES.list);
          } catch (err: unknown) {
               let msg = "خطا در ثبت تصویر";
               if (axios.isAxiosError(err) && err.response?.data?.message) {
                    msg = err.response.data.message;
               } else if (err instanceof Error) {
                    msg = err.message;
               }
               MyNotification("خطا", msg, "error");
          } finally {
               setSubmitting(false);
          }
     };

     return (
          <>
               <Header title="بارگذاری عکس نصب" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="gallery-body display-grid">
                    <div>
                         <h2 className="fs-13 fw-600">
                              عکس نصب خود را ثبت کنید
                         </h2>

                         <ImageUpload
                              value={photo}
                              onChange={(file) => {
                                   setPhoto(file);
                              }}
                              label="عکس عمودی بگیرید"
                         />

                         <label className="proj-label mt-4 fs-12 color-primary fw-600">کپشن</label>
                         <TextInput
                              value={caption}
                              onChange={setCaption}
                              minLength={3}
                              maxLength={200}
                              className="proj-input"
                              placeholder="مثلا نصب لوله کشی ساختمان مسکونی"

                         />

                         <label className="proj-label mt-3 fs-12 color-primary fw-600">لوکیشن</label>
                         <TextInput
                              value={location}
                              onChange={setLocation}
                              minLength={3}
                              maxLength={200}
                              className="proj-input"
                              placeholder="مثلا اصفهان"
                         />
                    </div>

                    <div className="proj-sticky-bottom">
                         <button className="auth-btn" onClick={handleSubmit} disabled={!photo || submitting}>
                              {submitting ? "در حال ارسال..." : "ارسال عکس"}
                         </button>
                    </div>
               </div>
          </>
     );
}