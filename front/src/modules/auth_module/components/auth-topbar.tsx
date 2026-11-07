// src/modules/auth_module/screens/AuthTopbar.tsx (یا هر جایی که این فایل قرار دارد)

import { useNavigate } from "react-router-dom";
import { AUTH_ROUTES } from "../routes"; // مطمئن شوید مسیر درست است
import "../../../shared/styles/AuthTemplate.css";

// ✅ تعریف پراپس‌ها
interface AuthTopbarProps {
     backTo?: string; // مسیر بازگشت (اختیاری)
     title?: string; // مسیر بازگشت (اختیاری)
}

export default function AuthTopbar({ backTo = AUTH_ROUTES.login, title }: AuthTopbarProps) {
     const navigate = useNavigate();

     return (
          <div className="auth-topbar">
               <button
                    className="auth-back-btn"
                    onClick={() => navigate(backTo)}
                    aria-label="back"
               >
                    <i className="icon-arrow-right-3 fw-800"></i>
               </button>

               <h1 className="auth-page-title">{title}</h1>
          </div>
     );
}