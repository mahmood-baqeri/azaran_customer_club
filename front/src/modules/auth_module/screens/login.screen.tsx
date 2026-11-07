// src/modules/auth_module/screens/login.screen.tsx

import { useMemo, useState } from "react";
// import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/use-auth";
// import { AUTH_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import { MyNotification } from "../../../shared/utils/notification";
import {
     IconSmartphone,
     IconLoader,
     IconArrowLeft,
} from "../../../shared/components/AuthIcons";
import "../../../shared/styles/AuthTemplate.css";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import AuthFootbar from "../components/auth-footbar";

export default function LoginScreen() {
     const { login } = useAuth();
     // const navigate = useNavigate();
     const [mobile, setMobile] = useState("");
     const [loading, setLoading] = useState(false);

     const cleanMobile = useMemo(
          () => convertPersianToEnglish(mobile).trim(),
          [mobile]
     );
     const isMobileValid = /^09\d{9}$/.test(cleanMobile);
     const canSubmit = isMobileValid && !loading;

     const handleSubmit = async (e: React.FormEvent) => {
          e.preventDefault();
          if (!canSubmit) {
               MyNotification("اخطار !", "شماره موبایل معتبر نیست", "error");
               return;
          }
          setLoading(true);
          try {
               await login(cleanMobile);
          } finally {
               setLoading(false);
          }
     };


     const formatPhoneNumber = (value: string) => {
          // فقط اعداد را نگه می‌داریم
          const digits = value.replace(/\D/g, "");

          // اگر خالی بود همان خالی برگردان
          if (!digits) return "";

          // فرمت: 0913 123 4567
          if (digits.length <= 4) return digits;
          if (digits.length <= 7) return `${digits.slice(0, 4)} ${digits.slice(4)}`;
          return `${digits.slice(0, 4)} ${digits.slice(4, 7)} ${digits.slice(7, 11)}`;
     };

     return (
          <div className="auth-root">
               <div className="auth-shell">
                    <div className="auth-hero">
                         <div className="auth-hero-logo">
                              <MyImage src={ICONS.logo} className="img" alt="Azaran" />
                         </div>
                         <h1 className="auth-hero-title">به باشگاه خوش آمدید</h1>
                         <p className="auth-hero-subtitle">ویژه مجریان و فروشندگان تاسیسات</p>
                         <div className="auth-hero-badges">
                              <div className="auth-hero-badge">
                                   <MyImage src={ICONS.folderAdd} height={25} width={25} className="img" alt="photo" />
                                   <span>ثبت پروژه</span>
                              </div>
                              <div className="auth-hero-badge">
                                   <MyImage src={ICONS.gift} height={22} width={22} className="img" alt="photo" />
                                   <span>امتیاز و هدیه</span>
                              </div>
                              <div className="auth-hero-badge">
                                   <MyImage src={ICONS.award} height={22} width={22} className="img" alt="photo" />
                                   <span>چالش روزانه</span>
                              </div>
                         </div>
                    </div>

                    <div className="auth-body">
                         <div className="auth-label">شماره موبایل</div>
                         <form onSubmit={handleSubmit}>
                              <div className="auth-field">
                                   <input
                                        type="tel"
                                        inputMode="numeric"
                                        placeholder="0913 123 4567"
                                        value={formatPhoneNumber(mobile)}
                                        onChange={(e) => {
                                             const rawValue = e.target.value.replace(/\D/g, ""); // حذف فاصله‌ها
                                             setMobile(rawValue.slice(0, 11)); // محدود کردن به ۱۱ رقم
                                        }}

                                        maxLength={13} // ۱۱ رقم + ۲ فاصله = ۱۳ کاراکتر
                                        dir="ltr"
                                        style={{ textAlign: "left", paddingRight: 16, paddingLeft: 46 }}
                                   />
                                   <div className="auth-field-icon">
                                        <IconSmartphone />
                                   </div>
                              </div>
                              <p className="auth-hint">
                                   کد تایید به این شماره پیامک می‌شود. اگر عضو نیستید، با همین
                                   شماره ثبت‌نام می‌شوید.
                              </p>
                              <button type="submit" className="auth-btn" disabled={!canSubmit}>
                                   {loading ? (
                                        <>
                                             <IconLoader size={20} />
                                             <span>در حال ارسال...</span>
                                        </>
                                   ) : (
                                        <>
                                             <span>دریافت کد تایید</span>
                                             <IconArrowLeft size={18} />
                                        </>
                                   )}
                              </button>
                         </form>

                         {/* <button
                              className="auth-btn-link"
                              onClick={() => navigate(AUTH_ROUTES.password)}
                         >
                              ورود با رمز عبور
                         </button> */}

                         <p className="auth-terms">
                              ورود شما به معنی پذیرش{" "}
                              <a className="auth-link" href="#">
                                   قوانین باشگاه
                              </a>{" "}
                              است.
                         </p>
                    </div>

                    <AuthFootbar />

               </div>
          </div>
     );
}