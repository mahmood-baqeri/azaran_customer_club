// src/modules/auth_module/interface/auth.types.ts

import type { UserMe } from "../../user_module/interface/user.types";


export interface LoginInput {
  mobile: string;
}

export interface VerifyInput {
  mobile: string;
  code: string;
}

export interface PasswordLoginInput {
  mobile: string;
  password: string;
}

export interface RegisterInput {
  first_name: string;
  last_name: string;
  nature: "executive" | "seller";
  password?: string;
  referral_code?: string;
  province_id: number | null;
  city_id: number | null;
  address: string;
  postal_code: string;
}


export interface AuthResponse {
  access_token: string;
  user?: UserMe;
}

export interface VerifyResponse {
  status: "Success" | "Error";
  message: string;
  data: {
    access_token: string;
    refresh_token: string;
    user?: UserMe;
  };
}

export interface SendLoginCodeResponse {
  status: "Success" | "Error";
  message: string;
  data: { existUser: boolean };
}