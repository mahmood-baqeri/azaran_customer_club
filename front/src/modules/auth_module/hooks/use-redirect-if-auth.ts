// src/modules/auth_module/hooks/use-redirect-if-auth.ts

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getLocalStorage } from "../../../shared/storage/local-storage";
import { Token } from "../../../shared/constants/storage-keys";

/**
 * اگر کاربر قبلاً لاگین کرده باشد (توکن داشته باشد)، او را به صفحه اصلی هدایت می‌کند.
 * این هوک برای صفحاتی مثل لاگین، ثبت‌نام و OTP استفاده می‌شود تا کاربر لاگین شده دوباره این صفحات را نبیند.
 */
export const useRedirectIfAuthenticated = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = getLocalStorage(Token);
    if (token && token !== "undefined" && token !== "null") {
      // کاربر لاگین است -> هدایت به صفحه اصلی
      navigate("/", { replace: true });
    }
  }, [navigate]);
};