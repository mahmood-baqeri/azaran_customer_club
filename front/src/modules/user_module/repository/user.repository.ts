// src/modules/user_module/repository/user.repository.ts
import {
  userApi,
  type UpdateProfileInput,
  type UploadJobCertificateInput,
  type SubmitFavoriteAnswerInput,
} from "../api/user.api";
import type {
  UserMe,
  JobCertificate,
  FavoriteQuestion,
  JobCertificateType,
} from "../interface/user.types";

export const userRepository = {
  // ----- پروفایل -----
  async loadMe(): Promise<UserMe> {
    const res = await userApi.me();
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

  // ----- 🆕 مدارک شغلی -----
  async getJobCertificates(): Promise<JobCertificate[]> {
    const res = await userApi.getJobCertificates();
    return res.data;
  },

  async uploadJobCertificate(input: UploadJobCertificateInput): Promise<JobCertificate> {
    const res = await userApi.uploadJobCertificate(input);
    return res.data;
  },

  async deleteJobCertificate(type: JobCertificateType): Promise<void> {
    await userApi.deleteJobCertificate(type);
  },

  // ----- 🆕 علاقه‌مندی‌ها -----
  async getFavoriteQuestions(): Promise<FavoriteQuestion[]> {
    const res = await userApi.getFavoriteQuestions();
    return res.data;
  },

  async submitFavoriteAnswer(input: SubmitFavoriteAnswerInput): Promise<{
    id: number;
    question_id: number;
    answer: string;
    answer_display: string;
  }> {
    const res = await userApi.submitFavoriteAnswer(input);
    return res.data;
  },
};