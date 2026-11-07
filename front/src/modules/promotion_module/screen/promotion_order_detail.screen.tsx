// src/modules/promotion_module/screen/promotion_order_detail.screen.tsx

import { useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { usePromotionOrderDetail } from "../hooks/use-promotion-order-detail";
import { convertToJalaliDate } from "../../../shared/utils/date";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import "../../../shared/styles/gift.css"; // استفاده از تایم‌لاین هدایا

const StepIcon = ({ type }: { type: number }) => {
     switch (type) {
          case 1: return <MyImage src={ICONS.basket_add} className="step-svg-icon" def="/assets/none.png" alt="basket" />;
          case 2: return <MyImage src={ICONS.basket_verify} className="step-svg-icon" def="/assets/none.png" alt="basket" />;
          case 3: return <MyImage src={ICONS.truck_start} className="step-svg-icon" def="/assets/none.png" alt="truck" />;
          case 4: return <MyImage src={ICONS.truck_tick} className="step-svg-icon" def="/assets/none.png" alt="truck" />;
          default: return null;
     }
};

const CheckIcon = () => (
     <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
     </svg>
);

const STATUS_ORDER = ["pending", "approved", "shipped", "delivered"];
const STATUS_LABELS = ["ثبت سفارش", "تایید سفارش", "تحویل به پست", "تحویل به مشتری"];

export default function PromotionOrderDetailScreen() {
     const { id } = useParams<{ id: string }>();
     const orderId = id ? Number(id) : null;
     const { order, loading, cancelling, cancelOrder } = usePromotionOrderDetail(orderId);

     if (loading || !order) {
          return (
               <>
                    <Header title="وضعیت سفارش" showBack showLogo={false} />
                    <p className="text-center text-muted mt-5">در حال دریافت اطلاعات...</p>
               </>
          );
     }

     const currentStatusIndex = STATUS_ORDER.indexOf(order.status);
     const isCancellable = order.status === "pending" || order.status === "approved";

     const getStepDate = (status: string) => {
          const log = order.logs?.find((l) => l.to_status === status);
          return log && log.created_at ? convertToJalaliDate(log.created_at) : "";
     };

     const handleCancel = () => {
          if (window.confirm("آیا از لغو این سفارش مطمئن هستید؟")) {
               cancelOrder("لغو توسط کاربر");
          }
     };

     return (
          <>
               <Header title="وضعیت سفارش" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="p-4">
                    {/* بخش تایم‌لاین */}
                    <div className="timeline-wrapper">
                         {STATUS_ORDER.map((statusKey, index) => {
                              const isActive = index <= currentStatusIndex;
                              const isLast = index === STATUS_ORDER.length - 1;
                              const stepDate = getStepDate(statusKey);

                              return (
                                   <div className="timeline-step" key={statusKey}>
                                        <div className="timeline-content">
                                             <span className={`timeline-title ${isActive ? "" : "inactive"}`}>
                                                  {STATUS_LABELS[index]}
                                                  <StepIcon type={index + 1} />
                                             </span>

                                             {statusKey === "shipped" && isActive && order.tracking_code && (
                                                  <span className="timeline-link" onClick={() => alert(`کد رهگیری: ${order.tracking_code}`)}>
                                                       <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" /></svg>
                                                       وضعیت مرسوله
                                                  </span>
                                             )}
                                        </div>

                                        <div className="timeline-line-container">
                                             <div className={`timeline-icon-circle ${isActive ? "" : "inactive"}`}>
                                                  {isActive && <CheckIcon />}
                                             </div>
                                             {!isLast && (
                                                  <div className={`timeline-line ${isActive && index + 1 <= currentStatusIndex ? "" : "dashed"}`} />
                                             )}
                                        </div>

                                        <div className="timeline-date">{stepDate}</div>
                                   </div>
                              );
                         })}
                    </div>

                    {/* دکمه لغو سفارش */}
                    {isCancellable && (
                         <button
                              className="order-cancel-btn"
                              onClick={handleCancel}
                              disabled={cancelling}
                              style={{ marginTop: 24 }}
                         >
                              {cancelling ? "در حال لغو..." : "لغو سفارش"}
                         </button>
                    )}
               </div>
          </>
     );
}