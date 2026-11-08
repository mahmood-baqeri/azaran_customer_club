// src/modules/gallery_module/hooks/use-galleries.ts

import { useCallback, useEffect, useState } from "react";
import { galleryRepository } from "../repository/gallery.repository";
import type { Gallery } from "../interface/gallery.types";

export const useGalleries = (filterType: string = "newest") => {
  const [galleries, setGalleries] = useState<Gallery[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setGalleries(await galleryRepository.list(filterType));
    } finally {
      setLoading(false);
    }
  }, [filterType]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { galleries, loading, refresh, setGalleries };
};