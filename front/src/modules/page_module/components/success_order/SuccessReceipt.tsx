// src/modules/gift_module/components/success/SuccessReceipt.tsx

import { DOMAIN } from "../../../../shared/constants/env";

interface Props {
     title: string;
     orderId: number;
     images: string[];
     quantity: number;
     coinsDeducted: number;
     isFree: boolean;
     currentBalance: number;
}

export default function SuccessReceipt({
     title,
     orderId,
     images,
     quantity,
     coinsDeducted,
     isFree,
     currentBalance,
}: Props) {
     const full = (p: string | null | undefined) =>
          p ? (p.startsWith("http") ? p : p.startsWith("/") ? `${DOMAIN}${p}` : `${DOMAIN}/media/${p}`) : undefined;

     return (
          <div className="order-receipt-card">
               {/* هدر کارت: عنوان و عکس‌ها */}
               <div className="receipt-header">
                    <div className="receipt-title-box">
                         <h3>{title}</h3>
                         <span>شماره سفارش: {orderId}</span>
                    </div>

                    {/* مدیریت نمایش یک یا چند عکس */}
                    <div className={`receipt-images ${images.length > 1 ? "multi" : "single"}`}>
                         {images.map((img, i) => (
                              <div className="receipt-image" key={i}>
                                   <img src={full(img)} alt={title} />
                              </div>
                         ))}
                    </div>
               </div>

               <div className="receipt-divider" />

               {/* ردیف‌های اطلاعات */}
               <div className="receipt-row">
                    <span className="receipt-label">تعداد</span>
                    <strong className="receipt-value">{quantity} عدد</strong>
               </div>

               <div className="receipt-row">
                    <span className="receipt-label">سکه‌ی کسر شده</span>
                    {isFree ? (
                         <span className="free-badge">رایگان، چون عضو باشگاه شدی</span>
                    ) : (
                         <strong className="receipt-value coin-value">
                              <img src="/assets/coin_15.png" alt="azar" />
                              {coinsDeducted.toLocaleString("fa-IR")}
                         </strong>
                    )}
               </div>

               <div className="receipt-row">
                    <span className="receipt-label">موجودی فعلی تو</span>
                    <strong className="receipt-value coin-value">
                         <img src="/assets/coin_15.png" alt="azar" />
                         {currentBalance.toLocaleString("fa-IR")}
                    </strong>
               </div>
          </div>
     );
}