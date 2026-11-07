// src/modules/promotion_module/screen/promotion_orders.screen.tsx

import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { usePromotionOrders } from "../hooks/use-promotion-orders";
import { convertToJalaliDate } from "../../../shared/utils/date";
import { PROMOTION_ROUTES } from "../routes";
import "../../../shared/styles/promotion.css";
import "../../../shared/styles/gift.css"; // استفاده از استایل‌های مشترک کارت سفارش

const STATUS_CLASSES: Record<string, string> = {
     pending: "pending",
     approved: "approved",
     shipped: "shipped",
     delivered: "delivered",
     rejected: "rejected",
     cancelled: "cancelled",
     returned: "rejected",
};

export default function PromotionOrdersScreen() {
     const navigate = useNavigate();
     const { orders, loading } = usePromotionOrders();

     if (loading) {
          return (
               <>
                    <Header title="سفارش‌های اقلام تبلیغاتی" showBack showLogo={false} />
                    <p className="text-center text-muted mt-5">در حال بارگذاری…</p>
               </>
          );
     }

     return (
          <>
               <Header title="سفارش‌های اقلام تبلیغاتی" showBack showLogo={false} menuBg="f7f8fb" />

               <div className="p-4">
                    {orders.length === 0 ? (
                         <p className="text-center text-muted">هنوز سفارشی از اقلام تبلیغاتی ثبت نکرده‌اید.</p>
                    ) : (
                         orders.map((order) => (
                              <div
                                   key={order.id}
                                   className="order-list-card"
                                   onClick={() => navigate(PROMOTION_ROUTES.orderDetail(order.id))}
                              >
                                   <div className="order-card-main">
                                        {/* اگر پک تک‌عکسی بود، عکس اول را نشان می‌دهیم */}
                                        <div className="order-card-img">
                                             {order.promotion.items[0]?.photo && (
                                                  <img src={`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/manager'}${order.promotion.items[0].photo}`} alt={order.promotion.title} />
                                             )}
                                        </div>

                                        <div className="order-card-info">
                                             <h3 className="order-card-title">{order.promotion.title}</h3>
                                             <div className="order-card-meta">
                                                  <span>تاریخ: {convertToJalaliDate(order.created_at ?? "")}</span>
                                             </div>
                                             <div className="order-card-meta">
                                                  <span>شماره سفارش: {order.id}</span>
                                             </div>
                                        </div>

                                        <div className="order-card-price" style={{ color: "#4caf50" }}>
                                             رایگان
                                        </div>
                                   </div>

                                   <div className="order-card-footer">
                                        <span className={`status-badge ${STATUS_CLASSES[order.status] || "pending"}`}>
                                             {order.status_display}
                                        </span>
                                   </div>
                              </div>
                         ))
                    )}
               </div>
          </>
     );
}