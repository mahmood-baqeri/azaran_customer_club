// src/modules/invitation_module/interface/invitation.types.ts

export interface InvitedUser {
  uuid: string;
  name: string;
  avatar: string | null;
  joined_at: string | null;
}

export interface Invitation {
  id: number;
  invited_mobile: string;
  is_registered: boolean;
  is_rewarded: boolean;
  invited_at: string | null;
  rewarded_at: string | null;
  user: InvitedUser | null;
}

export interface ApiResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T;
}