// src/modules/promotion_module/screen/promotions.screen.tsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { usePromotions } from "../hooks/use-promotions";
import { useBuyPromotion } from "../hooks/use-buy-promotion";
import { DOMAIN } from "../../../shared/constants/env";

import "../../../shared/styles/promotion.css";
import OrderCheckoutModal from "../../../shared/components/modal/order/checkout-modal";
import { ICONS } from "../../../shared/constants/icons";
import MyImage from "../../../shared/components/image-show";
import { PROFILE_ROUTES } from "../../user_module/routes";
import OrderCertificateModal from "../../../shared/components/modal/order/certificate-modal";
import { useUser } from "../../user_module/hooks/use-user";
import { PROMOTION_ROUTES } from "../routes";

export default function PromotionsScreen() {
     const { user } = useUser();
     const navigate = useNavigate();
     const { promotions, loading } = usePromotions();
     const { buy, submitting } = useBuyPromotion();

     const [selectedId, setSelectedId] = useState<number | null>(null);
     const [showCheckout, setShowCheckout] = useState(false);
     const [showCertModal, setShowCertModal] = useState(false);

     const full = (p: string | null | undefined) => p ? (p.startsWith("http") ? p : p.startsWith("/") ? `${DOMAIN}${p}` : `${DOMAIN}/media/${p}`) : undefined;

     // ✅ پیدا کردن پک انتخاب شده برای نمایش نام آن در بالای صفحه
     const selectedPromo = promotions.find((p) => p.id === selectedId);
     const isDisabled = !selectedId || submitting;

     const handleCheckoutConfirm = async (data: {
          receiver_name: string;
          receiver_phone: string;
          address: string;
          postal_code: string;
     }) => {
          if (!selectedId) return;

          const order = await buy({
               promotion_id: selectedId,
               ...data,
          });

          if (order) {
               setShowCheckout(false);
               navigate(PROMOTION_ROUTES.success(order.id));
          }
     };

     const handleBuyClick = () => {
          if (isDisabled) return;

          const hasJobInfo = !!(user?.job_certificates && user.job_certificates.length === 3);

          if (!hasJobInfo) {
               setShowCertModal(true);
               return;
          }

          // ✅ باز کردن مودال ارسال به جای خرید مستقیم
          setShowCheckout(true);
     };

     return (
          <>
               <Header title="اقلام تبلیغاتی" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="" style={{ paddingLeft: 15, paddingRight: 15, paddingTop: 5, paddingBottom: 100 }}>
                    {/* ✅ متن داینامیک: اگر انتخاب کرده بود، اسم پک را می‌نویسد */}
                    <p className="mb-2 fs-12">
                         {selectedPromo
                              ? <> <span className="text-primary fw-600"> "{selectedPromo.title}" </span> را انتخاب نموده اید </>
                              : "پک تبلیغاتی مورد نظر خود را انتخاب کنید"}
                    </p>

                    {loading && promotions.length === 0 && (
                         <p className="text-center text-muted">در حال بارگذاری…</p>
                    )}

                    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                         {promotions.map((promo) => {
                              const isSelected = selectedId === promo.id;
                              // ✅ اگر یک پک انتخاب شده و این پک آن نیست، کمرنگ شود
                              const isDimmed = selectedId !== null && !isSelected;

                              return (
                                   <div
                                        key={promo.id}
                                        className={`promotion-card ${isSelected ? "selected" : ""}`}
                                        onClick={() => setSelectedId(promo.id)}
                                        style={{
                                             opacity: isDimmed ? 0.4 : 1,
                                             transition: "opacity 0.3s ease, border-color 0.2s ease",
                                        }}
                                   >
                                        {/* هدر کارت: عنوان و رادیو باتن */}
                                        <div className="promotion-header">
                                             <div className={`custom-radio ${isSelected ? "checked" : ""}`} />
                                             <span className="promotion-title">{promo.title}</span>
                                        </div>

                                        {/* گرید آیتم‌ها */}
                                        <div className="promotion-grid">
                                             {promo.items.map((item) => (
                                                  <div className="promotion-item" key={item.id}>
                                                       <div className="promotion-item-img">
                                                            {item.photo && <img src={full(item.photo)} alt={item.title} />}

                                                            {/* بج (مثل آیکون + در تصویر) */}
                                                            {item.badge && (
                                                                 <span className="promotion-item-badge">{item.badge}</span>
                                                            )}
                                                       </div>
                                                       <span className="promotion-item-title">{item.title}</span>
                                                  </div>
                                             ))}
                                        </div>
                                   </div>
                              );
                         })}
                    </div>
               </div>

               {/* دکمه شناور پایین صفحه */}
               <div className="promotion-bottom-bar">
                    <button
                         className="auth-btn"
                         onClick={handleBuyClick}
                         disabled={isDisabled}
                    >
                         {submitting ? "در حال ثبت..." : "سفارش دهید"}
                         <MyImage src={ICONS.basket_add_2} className="w__25" alt="truck" />
                    </button>
               </div>

               <OrderCertificateModal
                    isOpen={showCertModal}
                    onClose={() => setShowCertModal(false)}
                    onUpload={() => {
                         setShowCertModal(false);
                         navigate(PROFILE_ROUTES.completion);
                    }}
               />

               {/* مودال ارسال */}
               <OrderCheckoutModal
                    isOpen={showCheckout}
                    onClose={() => setShowCheckout(false)}
                    onConfirm={handleCheckoutConfirm}
                    submitting={submitting}
               />
          </>
     );
}