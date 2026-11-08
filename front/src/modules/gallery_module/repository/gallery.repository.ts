// src/modules/gallery_module/repository/gallery.repository.ts

import { galleryApi } from "../api/gallery.api";
import type { Gallery, LikeResponse } from "../interface/gallery.types";

export const galleryRepository = {
  async create(formData: FormData): Promise<Gallery | null> {
    const res = await galleryApi.create(formData);
    if (res.status === "Error") throw new Error(res.message);
    return res.data ?? null;
  },

  async detail(id: number): Promise<Gallery | null> {
    const res = await galleryApi.detail(id);
    if (res.status === "Error") throw new Error(res.message);
    return res.data ?? null;
  },
  
  async list(filterType: string): Promise<Gallery[]> {
    const res = await galleryApi.list(filterType);
    return Array.isArray(res.data) ? res.data : [];
  },

  async delete(id: number): Promise<boolean> {
    const res = await galleryApi.delete(id);
    if (res.status === "Error") throw new Error(res.message);
    return res.status === "Success";
  },

  async toggleLike(id: number): Promise<LikeResponse> {
    const res = await galleryApi.like(id);
    if (res.status === "Error") throw new Error(res.message);
    return res.data;
  },
};