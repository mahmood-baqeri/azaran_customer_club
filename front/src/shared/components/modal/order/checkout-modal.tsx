// src/modules/gift_module/components/checkout-modal.tsx

import { useState } from "react";
import { useUser } from "../../../../modules/user_module/hooks/use-user";
import { convertPersianToEnglish } from "../../../utils/slug";
import "../../../styles/gift.css";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     onConfirm: (data: {
          receiver_name: string;
          receiver_phone: string;
          address: string;
          postal_code: string;
     }) => void;
     submitting: boolean;
}

export default function OrderCheckoutModal({ isOpen, onClose, onConfirm, submitting }: Props) {
     const { user } = useUser();

     const [form, setForm] = useState({
          receiver_name: user?.name || "",
          receiver_phone: convertPersianToEnglish(user?.mobile || ""),
          address: user?.profile?.address || "",
          postal_code: convertPersianToEnglish(user?.profile?.post_code || ""),
     });

     if (!isOpen) return null;

     // ✅ اعتبارسنجی دقیق ساختار
     const isPhoneValid = /^09\d{9}$/.test(form.receiver_phone);
     const isPostalValid = /^\d{10}$/.test(form.postal_code);

     const isValid =
          form.receiver_name.trim().length > 2 &&
          isPhoneValid &&
          form.address.trim().length > 5 &&
          isPostalValid;

     // ✅ هندلر اختصاصی برای شماره موبایل (فقط عدد و حداکثر ۱۱ رقم)
     const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
          const raw = convertPersianToEnglish(e.target.value);
          // فقط اعداد را نگه می‌داریم
          const digits = raw.replace(/\D/g, "");
          // محدودیت ۱۱ رقم
          if (digits.length <= 11) {
               setForm({ ...form, receiver_phone: digits });
          }
     };

     // ✅ هندلر اختصاصی برای کد پستی (فقط عدد و حداکثر ۱۰ رقم)
     const handlePostalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
          const raw = convertPersianToEnglish(e.target.value);
          // فقط اعداد را نگه می‌داریم
          const digits = raw.replace(/\D/g, "");
          // محدودیت ۱۰ رقم
          if (digits.length <= 10) {
               setForm({ ...form, postal_code: digits });
          }
     };

     return (
          <div className="checkout-overlay">
               <div className="checkout-sheet">
                    <div className="checkout-header">
                         <h2>اطلاعات ارسال</h2>
                         <button type="button" className="close-btn" onClick={onClose}>&times;</button>
                    </div>

                    <div className="checkout-body">
                         <div className="auth-label">نام گیرنده</div>
                         <div className="auth-field">
                              <input
                                   type="text"
                                   value={form.receiver_name}
                                   onChange={(e) => setForm({ ...form, receiver_name: e.target.value })}
                                   placeholder="نام و نام خانوادگی گیرنده"
                                   style={{ padding: "0 16px" }}
                              />
                         </div>

                         <div className="auth-label">شماره تماس گیرنده</div>
                         <div className="auth-field">
                              <input
                                   type="tel"
                                   inputMode="numeric"
                                   dir="ltr"
                                   maxLength={11}
                                   value={form.receiver_phone}
                                   onChange={handlePhoneChange}
                                   placeholder="09123456789"
                                   className={form.receiver_phone && !isPhoneValid ? "input-error" : ""}
                                   style={{ padding: "0 16px", textAlign: "left" }}
                              />
                         </div>
                         {/* ✅ نمایش خطا برای شماره نامعتبر */}
                         {form.receiver_phone && !isPhoneValid && (
                              <span className="error-text">شماره باید با 09 شروع شده و ۱۱ رقم باشد.</span>
                         )}

                         <div className="auth-label">آدرس دقیق</div>
                         <div className="auth-field">
                              <textarea
                                   className="auth-textarea"
                                   value={form.address}
                                   onChange={(e) => setForm({ ...form, address: e.target.value })}
                                   placeholder="استان، شهر، خیابان، کوچه، پلاک، واحد"
                              />
                         </div>

                         <div className="auth-label">کد پستی (۱۰ رقم)</div>
                         <div className="auth-field">
                              <input
                                   type="text"
                                   inputMode="numeric"
                                   dir="ltr"
                                   maxLength={10}
                                   value={form.postal_code}
                                   onChange={handlePostalChange}
                                   placeholder="1234567890"
                                   className={form.postal_code && !isPostalValid ? "input-error" : ""}
                                   style={{ padding: "0 16px", textAlign: "left" }}
                              />
                         </div>
                         {/* ✅ نمایش خطا برای کد پستی نامعتبر */}
                         {form.postal_code && !isPostalValid && (
                              <span className="error-text">کد پستی باید دقیقاً ۱۰ رقم باشد.</span>
                         )}
                    </div>

                    <div className="checkout-footer">
                         <button
                              type="button"
                              className="auth-btn"
                              disabled={!isValid || submitting}
                              onClick={() => onConfirm(form)}
                         >
                              {submitting ? "در حال ثبت..." : "تایید و ثبت سفارش"}
                         </button>
                    </div>
               </div>
          </div>
     );
}