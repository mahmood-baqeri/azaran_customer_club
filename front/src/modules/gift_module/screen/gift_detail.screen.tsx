// src/modules/gift_module/screen/gift_detail.screen.tsx

import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useGiftDetail } from "../hooks/use-gift-detail";
import { useBuyGift } from "../hooks/use-buy-gift";
import { useUser } from "../../user_module/hooks/use-user";
import { DOMAIN } from "../../../shared/constants/env";
import { GIFT_ROUTES } from "../routes";
import OrderCertificateModal from "../../../shared/components/modal/order/certificate-modal";
import OrderCheckoutModal from "../../../shared/components/modal/order/checkout-modal";
import "../../../shared/styles/gift.css";
import "../../../shared/styles/gift-detail.css";
import { PROFILE_ROUTES } from "../../user_module/routes";

export default function GiftDetailScreen() {
     const { id } = useParams<{ id: string }>();
     const giftId = id ? Number(id) : null;
     const navigate = useNavigate();
     const { user } = useUser();

     const { gift, loading } = useGiftDetail(giftId);
     const { buy, submitting } = useBuyGift();

     const [qty, setQty] = useState(1);
     const [activeImage, setActiveImage] = useState<string | null>(null);

     // مودال‌ها
     const [showCertModal, setShowCertModal] = useState(false);
     const [showCheckout, setShowCheckout] = useState(false); // ✅ استیت مودال ارسال

     const full = (p: string | null | undefined) =>
          p ? (p.startsWith("http") ? p : `${DOMAIN + "/media/"}${p}`) : undefined;

     const allThumbs = useMemo(() => {
          if (!gift) return [];
          const items: { key: string; url: string | null; isMain: boolean }[] = [];
          if (gift.photo) items.push({ key: "main", url: gift.photo, isMain: true });
          gift.gallery.forEach((url, i) => {
               if (url) items.push({ key: `g${i}`, url, isMain: false });
          });
          return items;
     }, [gift]);

     if (loading && !gift) {
          return (
               <div className="auth-root">
                    <div className="auth-shell">
                         <Header title="جزئیات هدیه" showBack />
                         <div className="auth-body"><p className="text-center text-muted">در حال بارگذاری…</p></div>
                    </div>
               </div>
          );
     }

     if (!gift) return null;

     const hero = activeImage ? full(activeImage) : full(gift.photo);

     const userBalance = user?.score?.current_balance ?? 0;
     const totalPrice = gift.azar_value * qty;

     const isAffordable = userBalance >= totalPrice;
     const isOutOfStock = gift.stock < 1;
     const canBuy = isAffordable && !isOutOfStock && !submitting;

     const handleBuyClick = () => {
          if (!canBuy) return;

          const hasJobInfo = !!(user?.job_certificates && user.job_certificates.length === 3);

          if (!hasJobInfo) {
               setShowCertModal(true);
               return;
          }

          // ✅ باز کردن مودال ارسال به جای خرید مستقیم
          setShowCheckout(true);
     };

     const handleCheckoutConfirm = async (data: {
          receiver_name: string;
          receiver_phone: string;
          address: string;
          postal_code: string;
     }) => {
          if (!gift) return;

          const order = await buy({
               gift_id: gift.id,
               quantity: qty,
               ...data,
          });

          if (order) {
               setShowCheckout(false);
               navigate(GIFT_ROUTES.success(order.id));
          }
     };

     return (
          <>
               <Header showLogo={false} showBack menuBg="e8eefc" buttonBg="white" />

               <div className="gift-detail-section" style={{ background: "#e8eefc" }}>
                    <div className="gift-body" style={{ paddingTop: 0, paddingBottom: 0 }}>
                         <div className="gift-hero">
                              {hero && <img src={hero} alt={gift.title} />}
                         </div>

                         {allThumbs.length > 1 && (
                              <div className="gift-thumbnails">
                                   {allThumbs.map((t) => (
                                        <button
                                             key={t.key}
                                             type="button"
                                             className={`thumb-btn ${activeImage === t.url || (t.isMain && !activeImage) ? "active" : ""}`}
                                             onClick={() => setActiveImage(t.isMain ? null : t.url)}
                                        >
                                             <img src={full(t.url)} alt="thumb" />
                                        </button>
                                   ))}
                              </div>
                         )}

                         <div className="gift-detail-sheet">
                              <h1 className="gift-detail-title">{gift.title}</h1>
                              <p className="gift-detail-desc">{gift.description}</p>

                              <div className="gift-price-row">
                                   <div className="gift-price">
                                        <img src="/assets/coin_15.png" alt="azar" />
                                        <span>{totalPrice.toLocaleString("fa-IR")}</span>
                                   </div>

                                   <div className="qty-selector">
                                        <button
                                             onClick={() => setQty(q => Math.min(q + 1, gift.stock))}
                                             disabled={qty >= gift.stock || isOutOfStock}
                                        >
                                             +
                                        </button>
                                        <span>{qty}</span>
                                        <button
                                             onClick={() => setQty(q => Math.max(1, q - 1))}
                                             disabled={qty <= 1}
                                        >
                                             -
                                        </button>
                                   </div>
                              </div>

                              <button
                                   className="gift-buy-btn"
                                   onClick={handleBuyClick}
                                   disabled={!canBuy}
                              >
                                   <i className="icon-bag-2" style={{ marginLeft: 8 }}></i>
                                   {submitting
                                        ? "در حال ثبت..."
                                        : isOutOfStock
                                             ? "ناموجود"
                                             : !isAffordable
                                                  ? "امتیاز کافی نیست"
                                                  : "خرید با امتیاز"}
                              </button>
                         </div>
                    </div>
               </div>

               <OrderCertificateModal
                    isOpen={showCertModal}
                    onClose={() => setShowCertModal(false)}
                    onUpload={() => {
                         setShowCertModal(false);
                         navigate(PROFILE_ROUTES.completion);
                    }}
               />

               {/* ✅ مودال ثبت اطلاعات ارسال */}
               <OrderCheckoutModal
                    isOpen={showCheckout}
                    onClose={() => setShowCheckout(false)}
                    onConfirm={handleCheckoutConfirm}
                    submitting={submitting}
               />
          </>
     );
}