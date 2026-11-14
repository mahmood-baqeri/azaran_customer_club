// front/src/modules/notifications_module/hooks/use-notifications.ts

import { useCallback, useEffect, useState } from "react";
import { notificationsRepository } from "../repository/notifications.repository";
import { UserNotifications } from "../../../shared/constants/storage-keys";
import { getLocalStorage, setLocalStorage } from "../../../shared/storage/local-storage";
import type { NotificationItemData } from "../interface/notification.types";

// ═══════════════════════════════════════════════════════════
// badge count (هدر)
// ═══════════════════════════════════════════════════════════
export const useNotifications = (refreshKey?: string | number) => {
  const [count, setCount] = useState<number>(
    Number(getLocalStorage(UserNotifications) ?? 0)
  );

  const refresh = useCallback(async () => {
    try {
      const c = await notificationsRepository.unreadCount();
      setLocalStorage(UserNotifications, c);
      setCount(c);
    } catch (e) {
      console.warn("[notifications] refresh failed:", e);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh, refreshKey]);

  return { count, refresh };
};

// ═══════════════════════════════════════════════════════════
// list + pagination
// ═══════════════════════════════════════════════════════════
export const useNotificationList = (pageSize = 20) => {
  const [items, setItems] = useState<NotificationItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchPage = useCallback(
    async (p: number, append = false) => {
      // ✅ if/else به‌جای ternary به‌عنوان statement
      if (p === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      setError(null);

      try {
        const res = await notificationsRepository.list({
          page: p,
          page_size: pageSize,
        });
        setItems((prev) => (append ? [...prev, ...res.items] : res.items));
        setTotalPages(res.total_pages);
        setPage(p);
      } catch (e) {
        console.error("[notifications] list failed:", e);
        setError("خطا در دریافت اعلان‌ها");
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [pageSize]
  );

  useEffect(() => {
    fetchPage(1);
  }, [fetchPage]);

  const loadMore = useCallback(() => {
    if (page < totalPages && !loadingMore) fetchPage(page + 1, true);
  }, [page, totalPages, loadingMore, fetchPage]);

  const reload = useCallback(() => fetchPage(1), [fetchPage]);

  const markItemRead = useCallback((id: number) => {
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, is_read: true } : it))
    );
  }, []);

  const markAllLocalRead = useCallback(() => {
    setItems((prev) =>
      prev.map((it) => (it.is_read ? it : { ...it, is_read: true }))
    );
  }, []);

  const removeItem = useCallback((id: number) => {
    setItems((prev) => prev.filter((it) => it.id !== id));
  }, []);

  return {
    items,
    loading,
    loadingMore,
    error,
    page,
    totalPages,
    loadMore,
    reload,
    markItemRead,
    markAllLocalRead,
    removeItem,
  };
};