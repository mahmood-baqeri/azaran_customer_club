// src/modules/auth_module/hooks/use-auth.ts
import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { authRepository } from "../repository/auth.repository";
import { AUTH_ROUTES } from "../routes";
import { MyNotification } from "../../../shared/utils/notification";
import { useUser } from "../../user_module/hooks/use-user";
import { useSettings } from "../../settings_module/hooks/use-settings";
import { userRepository } from "../../user_module/repository/user.repository";
import type { PasswordLoginInput, RegisterInput } from "../interface/auth.types";
import { getErrorMessage } from "../../../shared/api/errors";

export const useAuth = () => {
  const navigate = useNavigate();
  const { setUser } = useUser();
  const { refreshSettings } = useSettings();

  const login = useCallback(async (mobile: string): Promise<void> => {
    try {
      const response = await authRepository.login(mobile);
      const existUser = response.data?.existUser === true;
      navigate(AUTH_ROUTES.otp, { state: { mobile, existUser } });
    } catch (err) {      
      MyNotification("اخطار ! ", getErrorMessage(err, "خطا در ارسال کد"), "error");
      
      throw err;
    }
  }, [navigate]);

  const verify = useCallback(async (mobile: string, code: string, existUser: boolean): Promise<void> => {
    try {
      // ⚠️ کدی که در login ساخته می‌شود purpose="login" دارد.
      const res = await authRepository.verify(mobile, code, "login");
      
      if (res.user) setUser(res.user);

      if (existUser) {
        await refreshSettings();
        navigate("/", { replace: true });
      } else {
        // کاربر جدید: توکن را دارد، پس باید اطلاعات تکمیلی را پر کند
        navigate(AUTH_ROUTES.register, { state: { mobile } });
      }
    } catch (err) {    
      MyNotification("اخطار ! ", getErrorMessage(err, "کد وارد شده معتبر نیست."), "error");
      throw err;
    }
  }, [navigate, setUser, refreshSettings]);

  const resend = useCallback(async (identifier: string) => {
    try {
      await authRepository.login(identifier);
      MyNotification("", "کد تایید دوباره ارسال شد.", "success");
    } catch {
      MyNotification("", "ارسال مجدد ناموفق بود.", "error");
    }
  }, []);

  const loginWithPassword = useCallback(async (input: PasswordLoginInput) => {
    try {
      const res = await authRepository.loginWithPassword(input);
      if (res.data?.user) setUser(res.data.user);
      await refreshSettings();
      navigate("/", { replace: true });
    } catch (err) {
      console.error("[auth] password login failed:", err);
      MyNotification("اخطار ! ", getErrorMessage(err, "شماره موبایل یا رمز عبور اشتباه است."), "error");
      throw err;
    }
  }, [navigate, setUser, refreshSettings]);

  const register = useCallback(
    async (input: RegisterInput) => {
      try {
        // ۱) ذخیره اطلاعات پروفایل
        const updatedUser = await userRepository.updateProfile({
          firstname: input.first_name,
          lastname: input.last_name,
          nature: input.nature,
          referral_code: input.referral_code,
          province_id: input.province_id,
          city_id: input.city_id,
          address: input.address,
          post_code: input.postal_code,
        });

        // ۲) اگر رمز تعیین شده بود، ذخیره کن
        if (input.password && input.password.length >= 6) {
          try {
            await userRepository.setInitialPassword(input.password);
          } catch (pwErr) {
            console.warn("[auth] set password failed:", pwErr);
          }
        }

        setUser(updatedUser);
        await refreshSettings();
        MyNotification("", "ثبت‌نام با موفقیت تکمیل شد.", "success");
        navigate("/", { replace: true });
      } catch (err) {
        console.error("[auth] register failed:", err);
        MyNotification("اخطار ! ", getErrorMessage(err, "خطا در ثبت‌نام"), "error");
        throw err;
      }
    },
    [navigate, setUser, refreshSettings]
  );

  const logout = useCallback(async () => {
    await authRepository.logout();
    setUser(null);
    navigate(AUTH_ROUTES.login, { replace: true });
  }, [navigate, setUser]);

  return { login, verify, resend, loginWithPassword, register, logout };
};