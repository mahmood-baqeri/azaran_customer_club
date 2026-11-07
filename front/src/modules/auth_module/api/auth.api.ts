// src/modules/auth_module/api/auth.api.ts
import { apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type {
  AuthResponse,
  PasswordLoginInput,
  RegisterInput,
  SendLoginCodeResponse,
  VerifyResponse,
} from "../interface/auth.types";

export const authApi = {
  sendLoginCode: (mobile: string): Promise<SendLoginCodeResponse> =>   apiPOST(`${BASE_URL}auth/login/`, { mobile }, false),

  verifyLoginCode: async (mobile: string, code: string, purpose: string): Promise<AuthResponse> => {
    const res = await apiPOST<VerifyResponse>(
      `${BASE_URL}auth/verify/`,
      { mobile, code, purpose }, // 👈 purpose ارسال می‌شود
      false
    );
    return { access_token: res.data.access_token, user: res.data.user };
  },

  loginWithPassword: (input: PasswordLoginInput): Promise<VerifyResponse> => apiPOST(`${BASE_URL}auth/login-password/`, input, false),

  register: (input: RegisterInput): Promise<unknown> => apiPOST(`${BASE_URL}auth/register/`, input, false),

  logout: (): Promise<unknown> =>  apiPOST(`${BASE_URL}auth/logout/`, {}, true),
};