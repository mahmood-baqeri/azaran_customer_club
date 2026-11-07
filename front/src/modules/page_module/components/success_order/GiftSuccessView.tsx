// src/modules/gift_module/components/success/GiftSuccessView.tsx

import { useNavigate } from "react-router-dom";
import { GIFT_ROUTES } from "../../../gift_module/routes";
import type { GiftOrder } from "../../../gift_module/interface/gift.types";
import SuccessReceipt from "./SuccessReceipt";

interface Props {
     order: GiftOrder;
     currentBalance: number;
}

export default function GiftSuccessView({ order, currentBalance }: Props) {
     const navigate = useNavigate();

     return (
          <>
               <SuccessReceipt
                    title={order.gift.title}
                    orderId={order.id}
                    images={[order.gift.photo || ""]}
                    quantity={order.quantity}
                    coinsDeducted={order.total_azar_value}
                    isFree={false}
                    currentBalance={currentBalance}
               />

               <div className="success-actions">
                    <button className="auth-btn" onClick={() => navigate(`/orders/${order.id}`)}>
                         پیگیری وضعیت سفارش
                    </button>
                    <button className="auth-btn-link" onClick={() => navigate(GIFT_ROUTES.list)}>
                         بازگشت به هدایا
                    </button>
               </div>
          </>
     );
}