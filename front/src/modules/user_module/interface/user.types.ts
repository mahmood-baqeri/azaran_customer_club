// src/modules/user_module/interface/user.types.ts

export type UserNatureTypes = "user" | "seller" | "executive" | "manager";

export type LevelName = "kardan" | "ostadkar";


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


export interface UserLevelInfo {
  current_level: LevelName;
  current_level_display: string;
  progress_percentage: number;
  points_needed_for_next: number;
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

  job_certificates: JobCertificate[]; 
  favorite_answers_count: number;
  has_answered_all_favorites: boolean;
  
  stats?: UserStats;
  recent_projects?: RecentProject[];
  recent_factors?: RecentFactor[];
  recent_gift_orders?: RecentGiftOrder[];
  recent_score_logs?: RecentScoreLog[];
  
  level?: UserLevelInfo;
}




// ✅ تایپ‌های جدید برای آمار
export interface UserStats {
  projects: { total: number; pending: number; approved: number; rejected: number };
  factors: { total: number; pending: number; approved: number; rejected: number };
  gift_orders: { total: number; pending: number; shipped: number; delivered: number };
  promotion_orders: { total: number; pending: number; delivered: number };
  supports: { total: number; open: number; in_progress: number; closed: number };
  gallery: { total: number; approved: number; pending: number };
  visits: { total: number; pending: number; approved: number };
  faqs_count: number;
  reviews: { answered_count: number; total_active: number; has_answered_all: boolean };
  invitations: { total_sent: number; successful: number; rewarded: number };
}


// ✅ تایپ‌های آخرین فعالیت‌ها
export interface RecentProject {
  id: number;
  title: string;
  type_display: string;
  status_display: string;
  created_at: string | null;
}

export interface RecentFactor {
  id: number;
  invoice_number: string | null;
  status_display: string;
  amount: number | null;
  created_at: string | null;
}

export interface RecentGiftOrder {
  id: number;
  gift_title: string;
  status_display: string;
  created_at: string | null;
}

export interface RecentScoreLog {
  id: number;
  code_display: string;
  direction: "earned" | "spent";
  amount: number;
  created_at: string | null;
}
