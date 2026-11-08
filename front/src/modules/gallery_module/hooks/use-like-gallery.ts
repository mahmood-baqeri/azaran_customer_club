
// src/modules/gallery_module/hooks/use-like-gallery.ts

import { useState } from "react";
import { galleryRepository } from "../repository/gallery.repository";
import { MyNotification } from "../../../shared/utils/notification";
import type { LikeResponse } from "../interface/gallery.types";

export const useLikeGallery = () => {
  const [loadingId, setLoadingId] = useState<number | null>(null);

  const toggleLike = async (id: number): Promise<LikeResponse | null> => {
    if (loadingId === id) return null;
    setLoadingId(id);
    try {
      return await galleryRepository.toggleLike(id);
    } catch (err: unknown) {
      let msg = "خطا در ثبت لایک";
      if (err instanceof Error) msg = err.message;
      MyNotification("خطا", msg, "error");
      return null;
    } finally {
      setLoadingId(null);
    }
  };

  return { toggleLike, loadingId };
};