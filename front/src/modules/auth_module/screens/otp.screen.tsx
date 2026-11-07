// src/modules/auth_module/screens/otp.screen.tsx

import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/use-auth";
import { AUTH_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import {

     IconLoader,
     IconArrowLeft,
} from "../../../shared/components/AuthIcons";
import "../../../shared/styles/AuthTemplate.css";
import AuthTopbar from "../components/auth-topbar";
import AuthFootbar from "../components/auth-footbar";

const OTP_LEN = 4;
const RESEND_SECONDS = 120;

export default function OtpScreen() {
     const location = useLocation();
     const navigate = useNavigate();
     const { verify, resend } = useAuth();

     // ✅ دریافت هر دو مقدار از state با تعریف تایپ صحیح
     const state = location.state as { mobile?: string; existUser?: boolean } | null;
     const mobile = state?.mobile || "";
     const existUser = state?.existUser || false;

     const [digits, setDigits] = useState<string[]>(Array(OTP_LEN).fill(""));
     const [loading, setLoading] = useState(false);
     const [secondsLeft, setSecondsLeft] = useState(RESEND_SECONDS);
     const refs = useRef<Array<HTMLInputElement | null>>([]);

     useEffect(() => {
          if (!mobile) navigate(AUTH_ROUTES.login, { replace: true });
     }, [mobile, navigate]);

     useEffect(() => {
          if (secondsLeft <= 0) return;
          const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
          return () => clearTimeout(t);
     }, [secondsLeft]);

     const maskedMobile = useMemo(() => {
          if (mobile.length < 11) return mobile;
          return `${mobile.slice(0, 4)}***${mobile.slice(-4)}`;
     }, [mobile]);

     const timeLabel = useMemo(() => {
          const m = Math.floor(secondsLeft / 60);
          const s = String(secondsLeft % 60).padStart(2, "0");
          return `${m}:${s}`;
     }, [secondsLeft]);

     const fullCode = digits.join("");
     const canSubmit = fullCode.length === OTP_LEN && !loading;

     const setDigit = (index: number, value: string) => {
          const cleaned = convertPersianToEnglish(value).replace(/\D/g, "");
          if (!cleaned) {
               const next = [...digits];
               next[index] = "";
               setDigits(next);
               return;
          }
          const chars = cleaned.split("");
          const next = [...digits];
          let cursor = index;
          for (const ch of chars) {
               if (cursor >= OTP_LEN) break;
               next[cursor] = ch;
               cursor += 1;
          }
          setDigits(next);
          const focusIdx = Math.min(cursor, OTP_LEN - 1);
          refs.current[focusIdx]?.focus();
     };

     const handleKeyDown = (
          index: number,
          e: React.KeyboardEvent<HTMLInputElement>
     ) => {
          if (e.key === "Backspace") {
               e.preventDefault();
               const next = [...digits];
               if (next[index]) {
                    next[index] = "";
                    setDigits(next);
               } else if (index > 0) {
                    next[index - 1] = "";
                    setDigits(next);
                    refs.current[index - 1]?.focus();
               }
          }
          if (e.key === "ArrowLeft" && index < OTP_LEN - 1) {
               refs.current[index + 1]?.focus();
          }
          if (e.key === "ArrowRight" && index > 0) {
               refs.current[index - 1]?.focus();
          }
     };

     const handleSubmit = async (e: React.FormEvent) => {
          e.preventDefault();
          if (!canSubmit) return;
          setLoading(true);
          try {
               await verify(mobile, fullCode, existUser);
          } finally {
               setLoading(false);
          }
     };

     const handleResend = async () => {
          if (secondsLeft > 0) return;
          await resend(mobile);
          setSecondsLeft(RESEND_SECONDS);
          setDigits(Array(OTP_LEN).fill(""));
          refs.current[0]?.focus();
     };

     return (
          <div className="auth-root">
               <div className="auth-shell">

                    <AuthTopbar backTo={AUTH_ROUTES.login} />

                    <div className="auth-body" style={{ paddingTop: 0 }}>
                         <div className="auth-center-icon">
                              <i className="icon-sms fs-40 fw-100"></i>
                         </div>

                         <h1 className="auth-page-title">کد تایید را وارد کنید</h1>
                         <p className="auth-page-subtitle">
                              کد {OTP_LEN} رقمی به شماره{" "}
                              <strong style={{ color: "#14306b", direction: "ltr", display: "inline-block" }}>
                                   {maskedMobile}
                              </strong>{" "}
                              پیامک شد
                         </p>

                         <div style={{ textAlign: "center", marginBottom: 50 }} className="fs-12">
                              <button
                                   type="button"
                                   className="auth-link fw-300"
                                   onClick={() => navigate(AUTH_ROUTES.login)}
                              >
                                   ویرایش شماره
                              </button>
                         </div>

                         <form onSubmit={handleSubmit}>
                              <div className="auth-otp-row">
                                   {digits.map((d, i) => (
                                        <input
                                             key={i}
                                             ref={(el) => {
                                                  refs.current[i] = el;
                                             }}
                                             className={`auth-otp-box ${d ? "filled" : ""}`}
                                             type="text"
                                             inputMode="numeric"
                                             maxLength={1}
                                             value={d}
                                             onChange={(e) => setDigit(i, e.target.value)}
                                             onKeyDown={(e) => handleKeyDown(i, e)}
                                             onFocus={(e) => e.currentTarget.select()}
                                        />
                                   ))}
                              </div>


                              <div className="auth-otp-resend">
                                   <i className="icon-clock"></i>
                                   <span>ارسال دوباره کد تا</span>
                                   <button type="button" disabled={secondsLeft > 0} onClick={handleResend}>
                                        {secondsLeft > 0 ? timeLabel : "ارسال مجدد"}
                                   </button>
                              </div>


                              <button type="submit" className="auth-btn" disabled={!canSubmit}>
                                   {loading ? (
                                        <>
                                             <IconLoader size={20} />
                                             <span>در حال بررسی...</span>
                                        </>
                                   ) : (
                                        <>
                                             <span> {existUser ? "ورود به باشگاه" : "تکمیل ثبت‌نام"} </span>
                                             <IconArrowLeft size={18} />
                                        </>
                                   )}
                              </button>
                         </form>

                         {existUser &&
                              <button
                                   className="auth-btn-link"
                                   onClick={() => navigate(AUTH_ROUTES.password, { state: { mobile } })}
                              >
                                   <i className="icon-lock fa-16"></i>

                                   <span> ورود با رمز عبور</span>
                              </button>
                         }
                    </div>

                    <AuthFootbar />
               </div>
          </div>
     );
}