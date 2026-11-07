// src/modules/auth_module/screens/password-login.screen.tsx

import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/use-auth";
import { AUTH_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import { MyNotification } from "../../../shared/utils/notification";
import {
     IconLock,
     IconEye,
     IconEyeOff,
     IconLoader,
} from "../../../shared/components/AuthIcons";
import "../../../shared/styles/AuthTemplate.css";
import AuthTopbar from "../components/auth-topbar";
import AuthFootbar from "../components/auth-footbar";

export default function PasswordLoginScreen() {
     const { loginWithPassword } = useAuth();

     const location = useLocation();
     const navigate = useNavigate();

     // ✅ دریافت هر دو مقدار از state با تعریف تایپ صحیح
     const state = location.state as { mobile?: string; existUser?: boolean } | null;
     const mobile = state?.mobile || "";



     const [password, setPassword] = useState("");
     const [showPass, setShowPass] = useState(false);
     const [loading, setLoading] = useState(false);

     const handleSubmit = async (e: React.FormEvent) => {
          e.preventDefault();
          const cleanMobile = convertPersianToEnglish(mobile).trim();
          if (!/^09\d{9}$/.test(cleanMobile)) {
               MyNotification("اخطار ! ", "شماره موبایل معتبر نیست", "error");
               return;
          }
          if (password.length < 4) {
               MyNotification("اخطار ! ", "رمز عبور کوتاه است", "error");
               return;
          }
          setLoading(true);
          try {
               await loginWithPassword({ mobile: cleanMobile, password });
          } finally {
               setLoading(false);
          }
     };

     return (
          <div className="auth-root">
               <div className="auth-shell">

                    <AuthTopbar backTo={AUTH_ROUTES.login} />

                    <div className="auth-body" style={{ paddingTop: 0 }}>
                         <div className="auth-center-icon">
                              <IconLock size={34} />
                         </div>

                         <h1 className="auth-page-title">ورود با رمز عبور</h1>
                         <p className="auth-page-subtitle">
                              ورود با شماره{" "}
                              <strong style={{ color: "#14306b", direction: "ltr", display: "inline-block" }}>
                                   {mobile || "0912***6789"}
                              </strong>{" "}
                              <button
                                   type="button"
                                   className="auth-link"
                                   onClick={() => navigate(AUTH_ROUTES.login)}
                                   style={{ fontSize: 12 }}
                              >
                                   تغییر
                              </button>
                         </p>

                         <form onSubmit={handleSubmit}>

                              <div className="auth-label" style={{ margin: "50px 0 8px" }}>
                                   رمز عبور
                              </div>
                              <div className="auth-field">
                                   <div className="auth-field-icon">
                                        <IconLock />
                                   </div>
                                   <input
                                        type={showPass ? "text" : "password"}
                                        placeholder="رمز عبور خود را وارد کنید"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        style={{ paddingRight: 46, paddingLeft: 46, textAlign: "left" }}
                                   />

                                   <div
                                        className="auth-field-icon clickable"
                                        style={{ left: "auto", right: 14 }}
                                        onClick={() => setShowPass((s) => !s)}
                                   >
                                        {showPass ? <IconEyeOff /> : <IconEye />}
                                   </div>
                              </div>

                              <div style={{ textAlign: "right", margin: "10px 0 80px" }}>
                                   <a className="auth-link" href="#" style={{ fontSize: 12 }}>
                                        رمز عبور را فراموش کرده‌ام
                                   </a>
                              </div>

                              <button type="submit" className="auth-btn" disabled={loading}>
                                   {loading ? (
                                        <>
                                             <IconLoader size={20} />
                                             <span>در حال ورود...</span>
                                        </>
                                   ) : (
                                        <span>ورود</span>
                                   )}
                              </button>
                         </form>

                    </div>

                    <AuthFootbar />
               </div>
          </div>
     );
}