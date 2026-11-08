/* eslint-disable @typescript-eslint/no-unused-vars */
// src/modules/gallery_module/hooks/use-gallery-detail.ts

import { useCallback, useEffect, useState } from "react";
import { galleryRepository } from "../repository/gallery.repository";
import type { Gallery } from "../interface/gallery.types";

export const useGalleryDetail = (id: number | null) => {
  const [gallery, setGallery] = useState<Gallery | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setGallery(await galleryRepository.detail(id));
    } catch (err) {
      setGallery(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { gallery, loading, setGallery, refresh };
};