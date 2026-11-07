// src/modules/auth_module/components/auth-guard.tsx

import { Navigate, Outlet } from "react-router-dom";
import { getLocalStorage } from "../../../shared/storage/local-storage";
import { Token } from "../../../shared/constants/storage-keys";
import { AUTH_ROUTES } from "../routes";

export default function AuthGuard() {
     const token = getLocalStorage(Token);
     const isAuthenticated = !!token && token !== "undefined" && token !== "null";

     // ❌ اگر کاربر لاگین نبود، به صفحه لاگین هدایت شود
     if (!isAuthenticated) {
          return <Navigate to={AUTH_ROUTES.login} replace />;
     }

     // ✅ اگر لاگین بود، اجازه ورود به صفحه را بده
     return <Outlet />;
}