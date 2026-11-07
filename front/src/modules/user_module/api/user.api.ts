// src/modules/user_module/api/user.api.ts
import { apiGET, apiPOST, apiDELETE } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type {
  UserMe,
  JobCertificate,
  FavoriteQuestion,
  FavoriteAnswerValue,
  JobCertificateType,
} from "../interface/user.types";

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

export interface JobCertificatesResponse {
  status: "Success" | "Error";
  message: string;
  data: JobCertificate[];
}

export interface JobCertificateResponse {
  status: "Success" | "Error";
  message: string;
  data: JobCertificate;
}

export interface FavoriteQuestionsResponse {
  status: "Success" | "Error";
  message: string;
  data: FavoriteQuestion[];
}

export interface FavoriteAnswerResponse {
  status: "Success" | "Error";
  message: string;
  data: {
    id: number;
    question_id: number;
    answer: FavoriteAnswerValue;
    answer_display: string;
  };
}

export interface UploadJobCertificateInput {
  type: JobCertificateType;
  file: File;
}

export interface SubmitFavoriteAnswerInput {
  question_id: number;
  answer: FavoriteAnswerValue;
}

export const userApi = {
  // ----- پروفایل -----
  me: (): Promise<ProfileResponse> =>
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

  // ----- 🆕 مدارک شغلی -----
  getJobCertificates: (): Promise<JobCertificatesResponse> =>
    apiGET(`${BASE_URL}user/profile/job-certificates/`, {}, true),

  uploadJobCertificate: (input: UploadJobCertificateInput): Promise<JobCertificateResponse> => {
    const fd = new FormData();
    fd.append("type", input.type);
    fd.append("file", input.file);
    return apiPOST(`${BASE_URL}user/profile/job-certificate/upload/`, fd, true);
  },

  deleteJobCertificate: (type: JobCertificateType): Promise<SimpleResponse> =>
    apiDELETE(`${BASE_URL}user/profile/job-certificate/${type}/`, true),

  // ----- 🆕 علاقه‌مندی‌ها -----
  getFavoriteQuestions: (): Promise<FavoriteQuestionsResponse> =>
    apiGET(`${BASE_URL}user/favorite-questions/`, {}, true),

  submitFavoriteAnswer: (input: SubmitFavoriteAnswerInput): Promise<FavoriteAnswerResponse> =>
    apiPOST(`${BASE_URL}user/favorite-questions/answer/`, input, true),
};