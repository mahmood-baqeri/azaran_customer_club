// src/modules/gift_module/screen/gifts.screen.tsx

import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useGifts } from "../hooks/use-gifts";
import { DOMAIN } from "../../../shared/constants/env";
import { GIFT_ROUTES } from "../routes";
import "../../../shared/styles/gift.css";
import { useUser } from "../../user_module/hooks/use-user";

export default function GiftsScreen() {
     const { user } = useUser();
     const navigate = useNavigate();
     const { gifts, loading } = useGifts();

     const currentScore = user?.score?.current_balance ?? 0;

     const title = `ویترین هدایا ${user?.nature === "seller" ? "فروشندگان" : "مجریان"}`;

     return (
          <>
               <Header title={title} showBack showLogo={false} menuBg="f7f8fb" buttonBg="white" />

               <div className="auth-body mb-3              pt-0" style={{ paddingTop: 16 }}>
                    {loading && gifts.length === 0 && (
                         <p className="text-center text-muted">در حال بارگذاری…</p>
                    )}

                    <div className="gifts-grid">
                         {gifts.map((g) => {
                              // محاسبه درصد پیشرفت (اگر قیمت صفر بود، تقسیم بر صفر نشود)
                              const percent = g.azar_value > 0 ? Math.min((currentScore / g.azar_value) * 100, 100) : 0;

                              // (اختیاری) اگر کاربر پول کافی داشت رنگ بار را کمی تغییر می‌دهیم
                              const isAffordable = currentScore >= g.azar_value;

                              return (
                                   <button key={g.id} type="button" className="gift-card" onClick={() => navigate(GIFT_ROUTES.detail(g.id))} >

                                        {/* نوار پیشرفت بالای کارت */}
                                        <div className="gift-card-topbar mt-2">
                                             <div
                                                  className={`gift-card-topbar-fill ${isAffordable ? "affordable" : ""}`}
                                                  style={{ width: `${percent}%` }}
                                             />
                                        </div>

                                        <div className="gift-card-price">
                                             <img src="/assets/coin_15.png" alt="azar" />
                                             <span>{g.azar_value.toLocaleString("fa-IR")}</span>
                                        </div>

                                        <div className="gift-card-image">
                                             {g.photo && (
                                                  <img
                                                       src={g.photo.startsWith("http") ? g.photo : `${DOMAIN}/media/${g.photo}`}
                                                       alt={g.title}
                                                  />
                                             )}
                                        </div>

                                        <h3 className="gift-card-title">{g.title}</h3>
                                   </button>
                              );
                         })}
                    </div>
               </div>
          </>
     );
}