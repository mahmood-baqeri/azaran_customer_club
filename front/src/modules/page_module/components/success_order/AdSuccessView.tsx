// src/modules/gift_module/components/success/AdSuccessView.tsx

import { useNavigate } from "react-router-dom";
import type { GiftOrder } from "../../../gift_module/interface/gift.types";
import SuccessReceipt from "./SuccessReceipt";

interface Props {
     order: GiftOrder;
     currentBalance: number;
}

export default function AdSuccessView({ order, currentBalance }: Props) {
     const navigate = useNavigate();

     // در اینجا فرض بر این است که ممکن است چند عکس در گالری هدیه باشد
     // اگر عکس اصلی هم وجود داشت، به آرایه اضافه می‌کنیم
     const images = [
          order.gift.photo || "",
          ...([])
     ].filter(Boolean);

     return (
          <>
               <SuccessReceipt
                    title={order.gift.title}
                    orderId={order.id}
                    images={images}
                    quantity={order.quantity}
                    coinsDeducted={order.total_azar_value}
                    isFree={order.total_azar_value === 0}
                    currentBalance={currentBalance}
               />

               <div className="success-actions">
                    <button className="auth-btn" onClick={() => navigate("/ads")}>
                         بازگشت به اقلام تبلیغاتی
                    </button>
               </div>
          </>
     );
}