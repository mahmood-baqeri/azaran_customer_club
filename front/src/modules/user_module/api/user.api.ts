// src/modules/user_module/api/user.api.ts

import { apiGET, apiPOST } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { UserMe } from "../interface/user.types";

export interface UpdateProfileInput {
  firstname: string;
  lastname: string;
  gender?: string;
  mobile?: string;
  birth_day?: string;
  national_code?: string;
  address?: string;
  post_code?: string;
  job_title?: string;
  company_name?: string;
  province_id?: number | null;
  city_id?: number | null;
  nature?: "executive" | "seller";
  referral_code?: string;
}

export interface ProfileResponse {
  status: "Success" | "Error";
  message: string;
  data: UserMe;
}

export interface SimpleResponse {
  status: "Success" | "Error";
  message: string;
}

export const userApi = {
  // ✅ دریافت دیتای جامع (شامل آمار، فعالیت‌ها و پروفایل)
  me: (): Promise<ProfileResponse> =>
    apiGET(`${BASE_URL}user/me/`, {}, true),

  // ✅ (اختیاری) اگر جایی نیاز به دیتای پایه پروفایل داشتید
  profile: (): Promise<ProfileResponse> =>
    apiGET(`${BASE_URL}user/profile/`, {}, true),

  updateProfile: (input: UpdateProfileInput): Promise<ProfileResponse> =>
    apiPOST(`${BASE_URL}user/profile/update/`, input, true),

  uploadAvatar: (file: File): Promise<ProfileResponse> => {
    const fd = new FormData();
    fd.append("avatar", file);
    return apiPOST(`${BASE_URL}user/profile/uploadavatar/`, fd, true);
  },

  setInitialPassword: (password: string): Promise<SimpleResponse> =>
    apiPOST(`${BASE_URL}user/profile/set-password/`, { password }, true),
};