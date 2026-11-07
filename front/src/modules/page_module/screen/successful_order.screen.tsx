// src/modules/gift_module/screen/successful_order.screen.tsx

import { useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useUser } from "../../user_module/hooks/use-user";
import "../../../shared/styles/gift.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

// هوک‌ها و کامپوننت‌های هدایا
import { useOrderDetail } from "../../gift_module/hooks/use-order-detail";
import GiftSuccessView from "../components/success_order/GiftSuccessView";


// هوک‌ها و کامپوننت‌های پروموشن (اقلام تبلیغاتی)
import { usePromotionOrderDetail } from "../../promotion_module/hooks/use-promotion-order-detail";
import PromotionSuccessView from "../components/success_order/PromotionSuccessView";
import FreeGiftSuccessView from "../components/success_order/FreeGiftSuccessView";

interface Props {
     /** 
      * نوع صفحه: 
      * 'gift' برای هدایا (پیش‌فرض)
      * 'promotion' برای اقلام تبلیغاتی
      */
     type?: "gift" | "promotion";
}

export default function SuccessfulOrderScreen({ type = "gift" }: Props) {
     const { id } = useParams<{ id: string }>();
     const orderId = id ? Number(id) : null;
     const { user } = useUser();

     // ✅ فراخوانی هوک مناسب بر اساس نوع ورودی
     // (اگر نوع هدیه است، هوک هدایا صدا زده می‌شود و برعکس)
     const { order: giftOrder, loading: giftLoading } = useOrderDetail(type === "gift" ? orderId : null);
     const { order: promoOrder, loading: promoLoading } = usePromotionOrderDetail(type === "promotion" ? orderId : null);

     const loading = type === "gift" ? giftLoading : promoLoading;
     const order = type === "gift" ? giftOrder : promoOrder;

     if (loading || !order) {
          return (
               <>
                    <Header showBack showLogo={false} menuBg="f7f8fb" />
                    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", marginTop: 50 }}>
                         <p className="text-muted">در حال دریافت اطلاعات سفارش...</p>
                    </div>
               </>
          );
     }

     const currentBalance = user?.score?.current_balance ?? 0;

     return (
          <>
               <Header showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="success-screen-body p-4">
                    {/* --- بخش آیکون و تیتر (مشترک) --- */}
                    <div className="success-header">
                         <div className="success-icon-wrapper">
                              <MyImage src={ICONS.gift_3} className="" def="/assets/none.png" alt="gift" />
                         </div>
                         <h2 className="success-title">سفارش ثبت شد</h2>
                         <p className="success-subtitle">بعد از تایید، سفارش برایت ارسال می‌شود</p>
                    </div>

                    {/* --- نمایش فاکتور مناسب --- */}
                    {type === "promotion" ? (
                         <PromotionSuccessView order={promoOrder!} currentBalance={currentBalance} />
                    ) : (
                         // کدهای قبلی هدایا
                         giftOrder!.total_azar_value === 0 ? (
                              <FreeGiftSuccessView order={giftOrder!} currentBalance={currentBalance} />
                         ) : (
                              <GiftSuccessView order={giftOrder!} currentBalance={currentBalance} />
                         )
                    )}
               </div>
          </>
     );
}