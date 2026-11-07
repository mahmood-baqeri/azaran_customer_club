// src/modules/gift_module/screen/orders.screen.tsx

import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useOrders } from "../hooks/use-orders";
import { DOMAIN } from "../../../shared/constants/env";
import { convertToJalaliDate } from "../../../shared/utils/date";
import "../../../shared/styles/gift.css";

const STATUS_CLASSES: Record<string, string> = {
     pending: "pending",
     approved: "approved",
     shipped: "shipped",
     delivered: "delivered",
     rejected: "rejected",
     cancelled: "cancelled",
     returned: "rejected",
};

export default function OrdersScreen() {
     const navigate = useNavigate();
     const { orders, loading } = useOrders();

     const full = (p: string | null | undefined) =>
          p ? (p.startsWith("http") ? p : p.startsWith("/") ? `${DOMAIN}${p}` : `${DOMAIN}/media/${p}`) : undefined;

     if (loading) {
          return (
               <>
                    <Header title="سفارش‌های من" showBack showLogo={false} />
                    <p className="text-center text-muted mt-5">در حال بارگذاری…</p>
               </>
          );
     }

     return (
          <>
               <Header title="سفارش‌های من" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="p-4">
                    {orders.length === 0 ? (
                         <p className="text-center text-muted">هنوز سفارشی ثبت نکرده‌اید.</p>
                    ) : (
                         orders.map((order) => (
                              <div
                                   key={order.id}
                                   className="order-list-card"
                                   onClick={() => navigate(`/orders/${order.id}`)}
                              >
                                   <div className="order-card-main">
                                        <div className="order-card-img">
                                             {order.gift.photo && <img src={full(order.gift.photo)} alt={order.gift.title} />}
                                        </div>

                                        <div className="order-card-info">
                                             <h3 className="order-card-title mb-1">{order.gift.title}</h3>
                                             <div className="order-card-meta mb-1">
                                                  <span>تاریخ: {convertToJalaliDate(order.created_at ?? "")}</span>
                                             </div>
                                             <div className="order-card-meta">
                                                  <span>شماره سفارش: {order.id}</span>
                                             </div>
                                        </div>

                                   </div>

                                   <div className="order-card-footer">
                                        <div className="order-card-price">
                                             <img src="/assets/coin_15.png" alt="azar" />
                                             {order.total_azar_value.toLocaleString("fa-IR")}
                                        </div>

                                        <span className={`status-badge fs-11 fw-400 ${STATUS_CLASSES[order.status] || "pending"}`}>
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