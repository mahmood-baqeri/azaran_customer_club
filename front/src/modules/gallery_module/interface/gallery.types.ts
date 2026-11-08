// src/modules/gallery_module/interface/gallery.types.ts

export type GalleryStatus = "pending" | "approved" | "rejected";

export interface GalleryUser {
  id: number;
  name: string;
  mobile: string;
}

export interface Gallery {
  id: number;
  photo: string | null;
  caption: string | null;
  location: string | null;
  status: GalleryStatus;
  status_display: string;
  created_at: string | null;
  likes_count: number;
  is_liked_by_me: boolean;
  user?: GalleryUser;
}

export interface LikeResponse {
  is_liked: boolean;
  likes_count: number;
}