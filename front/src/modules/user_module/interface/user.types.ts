// src/modules/user_module/interface/user.types.ts

export type UserNatureTypes = "user" | "seller" | "executive" | "manager";

export interface UserInviter {
  uuid: string;
  name: string;
  mobile: string;
  referral_code: string;
}

export interface LocationItem {
  id: number | null;
  name: string | null;
}

export interface UserProfile {
 national_code: string | null;
  birth_date: string | null;
  gender: "male" | "female" | null;
  gender_display: string | null;
  address: string | null;
  post_code: string | null;
  province: LocationItem | null;
  city: LocationItem | null;
  job_title: string | null;
  company_name: string | null;
}

export interface UserScore {
  current_balance: number;
  total_earned: number;
  total_spent: number;
}



// ==========================================
// 🆕 مدرک شغلی
// ==========================================
export type JobCertificateType =
  | "valid_business_license"
  | "technical_professional_certificate"
  | "letter_of_introduction";

export interface JobCertificate {
  id: number;
  type: JobCertificateType;
  type_display: string;
  file: string | null;
  file_size: number;
  file_type: string;
  is_verified: boolean;
  verified_at: string | null;
  can_edit: boolean;
}

// ==========================================
// 🆕 علاقه‌مندی‌ها
// ==========================================
export type FavoriteAnswerValue =
  | "very_little"
  | "little"
  | "average"
  | "a_lot"
  | "very_much";

export interface FavoriteAnswerOption {
  value: FavoriteAnswerValue;
  label: string;
}

export interface FavoriteUserAnswer {
  id: number;
  answer: FavoriteAnswerValue;
  answer_display: string;
  updated_at: string | null;
}

export interface FavoriteQuestion {
  id: number;
  question: string;
  answer_options: FavoriteAnswerOption[];
  user_answer: FavoriteUserAnswer | null;
}


// ==========================================
// کاربر کامل
// ==========================================
export interface UserMe {
  uuid: string;
  name: string;
  firstname: string;
  lastname: string;
  short_name: string;
  avatar: string | null;

  mobile: string;
  is_mobile_verified: boolean;
  date_joined: string | null;
  last_active_at: string | null;

  referral_code: string;
  nature: UserNatureTypes;
  nature_display: string;

  invited_by: UserInviter | null;
  profile: UserProfile | null;
  score: UserScore | null;

  // 🆕
  job_certificates: JobCertificate[]; 
  favorite_answers_count: number;
  has_answered_all_favorites: boolean;
}