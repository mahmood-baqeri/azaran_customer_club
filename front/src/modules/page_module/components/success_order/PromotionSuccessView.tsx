// src/modules/promotion_module/components/success/PromotionSuccessView.tsx

import { useNavigate } from "react-router-dom";
import type { PromotionOrder } from "../../../promotion_module/interface/promotion.types";
// ⚠️ از همان کامپوننت فاکتور مشترک استفاده می‌کنیم
import SuccessReceipt from "./SuccessReceipt";

interface Props {
     order: PromotionOrder;
     currentBalance: number;
}

export default function PromotionSuccessView({ order, currentBalance }: Props) {
     const navigate = useNavigate();

     // استخراج عکس تمام آیتم‌های داخل این پک
     const images = order.promotion.items
          .map((item) => item.photo || "")
          .filter(Boolean);

     return (
          <>
               <SuccessReceipt
                    title={order.promotion.title}
                    orderId={order.id}
                    images={images}
                    quantity={1} // پک‌های تبلیغاتی معمولاً ۱ عدد هستند
                    coinsDeducted={0}
                    isFree={true} // چون پروموشن‌ها کاملاً رایگان هستند
                    currentBalance={currentBalance}
               />

               <div className="success-actions">
                    <button className="auth-btn" onClick={() => navigate(`/promotions/orders/${order.id}`)}>
                         پیگیری وضعیت سفارش
                    </button>
                    <button className="auth-btn-link" onClick={() => navigate("/promotions")}>
                         بازگشت به اقلام تبلیغاتی
                    </button>
               </div>
          </>
     );
}