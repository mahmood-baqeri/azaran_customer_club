// src/modules/user_module/repository/user.repository.ts

import { userApi, type UpdateProfileInput } from "../api/user.api";
import type { UserMe } from "../interface/user.types";

export const userRepository = {
  // ✅ دریافت دیتای جامع (آمار، فعالیت‌ها، پروفایل)
  async loadFullInformation(): Promise<UserMe> {
    const res = await userApi.full_information();
    return res.data;
  },

  // ✅ (اختیاری) اگر فقط دیتای پایه پروفایل را خواستید
  async loadProfile(): Promise<UserMe> {
    const res = await userApi.profile();
    return res.data;
  },

  async updateProfile(input: UpdateProfileInput): Promise<UserMe> {
    const res = await userApi.updateProfile(input);
    return res.data;
  },

  async uploadAvatar(file: File): Promise<UserMe> {
    const res = await userApi.uploadAvatar(file);
    return res.data;
  },

  async setInitialPassword(password: string): Promise<void> {
    await userApi.setInitialPassword(password);
  },
};