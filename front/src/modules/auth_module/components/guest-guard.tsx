// src/modules/auth_module/components/guest-guard.tsx

import { Navigate, Outlet } from "react-router-dom";
import { getLocalStorage } from "../../../shared/storage/local-storage";
import { Token } from "../../../shared/constants/storage-keys";

export default function GuestGuard() {
     const token = getLocalStorage(Token);
     const isAuthenticated = !!token && token !== "undefined" && token !== "null";

     // ✅ اگر کاربر لاگین است، مستقیماً به صفحه اصلی هدایت می‌شود
     // و صفحات لاگین/ثبت‌نام اصلاً رندر نمی‌شوند.
     if (isAuthenticated) {
          return <Navigate to="/" replace />;
     }

     // اگر لاگین نبود، صفحات را نشان بده
     return <Outlet />;
}