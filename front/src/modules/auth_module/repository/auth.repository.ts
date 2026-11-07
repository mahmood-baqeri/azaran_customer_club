// src/modules/auth_module/repository/auth.repository.ts
import { authApi } from "../api/auth.api";
import { Token } from "../../../shared/constants/storage-keys";
import { getLocalStorage, setLocalStorage, clearLocalStorage } from "../../../shared/storage/local-storage";
import type { AuthResponse, PasswordLoginInput, SendLoginCodeResponse, VerifyResponse } from "../interface/auth.types";

export const authRepository = {
  login: (mobile: string): Promise<SendLoginCodeResponse> => authApi.sendLoginCode(mobile),

  async verify(mobile: string, code: string, purpose: string): Promise<AuthResponse> {
    const res = await authApi.verifyLoginCode(mobile, code, purpose);
    if (res.access_token) setLocalStorage(Token, res.access_token);
    return res;
  },

  async loginWithPassword(input: PasswordLoginInput): Promise<VerifyResponse> {
    const res = await authApi.loginWithPassword(input);
    if (res.data?.access_token) setLocalStorage(Token, res.data.access_token);
    return res;
  },

  hasAccessToken(): boolean {
    const t = getLocalStorage(Token);
    return !!t && t !== "undefined" && t !== "null";
  },

  async logout(): Promise<void> {
    try {
      await authApi.logout();
    } catch (e) {
      console.warn("[auth] logout api failed:", e);
    } finally {
      clearLocalStorage();
    }
  },
};