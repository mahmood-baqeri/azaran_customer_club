// front/src/modules/auth_module/screens/welcome.screen.tsx

import { useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../../../shared/styles/home-page.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import { useUser } from "../../user_module/hooks/use-user";
import { UserMe } from "../../user_module/interface/user.types";
import { PROFILE_ROUTES } from "../../user_module/routes";

export default function WelcomeScreen() {
     const { user } = useUser();
     const navigate = useNavigate();

     // مدیریت ریدایرکت به شکل صحیح در ری‌اکت
     useEffect(() => {
          if (!user) {
               navigate("/", { replace: true });
          }
     }, [user, navigate]);

     // اگر کاربر وجود نداشت، هیچی رندر نکن تا ریدایرکت انجام شود
     if (!user) return null;

     return (
          <div>
               {/* پاس دادن پراپ به شکل صحیح */}
               <WelcomeSection user={user} />
               <div className="px-2">
                    <GiftPromotion />
                    <BottomTabs />
               </div>
          </div>
     );
}

// ==========================================
// ۱. سکشن بالای صفحه (دایره و آواتارها)
// ==========================================
interface WelcomeSectionProps {
     user: UserMe;
}

const WelcomeSection = ({ user }: WelcomeSectionProps) => {
     return (
          <div className="d-flex flex-column align-items-center mb-4">
               {/* کارت آبی رنگ */}
               <div className="position-relative w-100 rounded-topleft-4 overflow-hidden">
                    <MyImage src={ICONS.welcome} def="/assets/none.png" alt="photo" className="w-100" />

                    {/* امتیاز */}
                    <div className="" style={{
                         position: "absolute", left: "50%",
                         transform: "translateX(-50%)",
                         textAlign: "center",
                         bottom: "15px"
                    }}>
                         <h2 className="text-warning fw-bold mb-1" style={{ fontSize: 28 }}>۱۱,۸۵۳</h2>
                         <p className="text-white fs-12 mb-0 opacity-75">مجری و فروشنده در باشگاه آذر</p>
                    </div>
               </div>

               {/* متن خوش‌آمدگویی */}
               <div className="text-center mt-5 mb-5 w-100 px-2">
                    {/* اینجا از firstname استفاده کردم، اگر در دیتابیس name دارید، همان را بگذارید */}
                    <h5 className="fw-bold color-primary mb-2 fs-16">{user.firstname}، به جمع ما خوش آمدی</h5>
                    <p className="text-muted fs-12 lh-lg">
                         از امروز می‌تونی از تعامل با همکارات در باشگاه لذت ببری
                    </p>
               </div>
          </div>
     );
};

// ==========================================
// ۲. بنر هدیه خوش‌آمدگویی
// ==========================================
const GiftPromotion = () => {
     return (
          <div className="mb-5">
               <div className="rounded-4 p-3 d-flex align-items-center gap-3" style={{ backgroundColor: "#FDF8E8" }}>
                    {/* باکس آیکون */}
                    <div className="d-flex justify-content-center align-items-center rounded-3" style={{ backgroundColor: "#F1D772", width: 50, height: 50, flexShrink: 0 }}>
                         <MyImage src={ICONS.gift} def="/assets/none.png" alt="gift" className="img25_25" />
                    </div>

                    {/* متن */}
                    <div>
                         <h6 className="fw-bold color-primary fs-13 mb-1">هدیه خوش‌آمدگویی منتظر توست</h6>
                         <p className="text-muted fs-11 mb-0 lh-base">
                              پروفایلت ۲ بخش تکمیل نشده داره که با تکمیلش به هدیه نزدیک‌تر میشی
                         </p>
                    </div>
               </div>
          </div>
     );
};

// ==========================================
// ۳. دکمه و تب‌های پایین
// ==========================================
const BottomTabs = () => {
     return (
          <div>
               {/* دکمه آبی */}
               <a href={PROFILE_ROUTES.profile} className="btn w-100 text-white fw-bold fs-13 rounded-4 mb-4" style={{ backgroundColor: "#1E408A", padding: "14px 0" }}>
                    تکمیل پروفایل و دریافت هدیه
               </a>

               {/* تب‌های پایین - با Link برای جلوگیری از رفرش صفحه */}
               <div className="d-flex justify-content-between align-items-center px-2 pb-4">
                    <span className="fs-12 text-muted" style={{ cursor: 'pointer' }}>آشنایی با باشگاه</span>
                    <Link to="/" className="fs-12 fw-bold color-primary text-decoration-none">صفحه اصلی</Link>
               </div>
          </div>
     );
};