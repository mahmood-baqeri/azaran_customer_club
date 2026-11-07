// src/modules/gift_module/components/success/FreeGiftSuccessView.tsx

import { useNavigate } from "react-router-dom";
import type { GiftOrder } from "../../interface/gift.types";
import SuccessReceipt from "./SuccessReceipt";

interface Props {
     order: GiftOrder;
     currentBalance: number;
}

export default function FreeGiftSuccessView({ order, currentBalance }: Props) {
     const navigate = useNavigate();

     return (
          <>
               <SuccessReceipt
                    title={order.gift.title}
                    orderId={order.id}
                    images={[order.gift.photo || ""]}
                    quantity={order.quantity}
                    coinsDeducted={order.total_azar_value}
                    isFree={true}
                    currentBalance={currentBalance}
               />

               <div className="success-actions">
                    <button className="auth-btn" onClick={() => navigate("/")}>
                         بازگشت به منو اصلی
                    </button>
               </div>
          </>
     );
}