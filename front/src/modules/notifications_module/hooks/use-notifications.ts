import { useCallback, useEffect, useState } from "react";
import { notificationsApi } from "../api/notifications.api";
import { UserNotifications } from "../../../shared/constants/storage-keys";
import { setLocalStorage } from "../../../shared/storage/local-storage";

export const useNotifications = (refreshKey?: string | number) => {
  const [count, setCount] = useState<number>(
    Number(localStorage.getItem(UserNotifications) || 0)
  );

  const refresh = useCallback(async () => {
    try {
      const res = await notificationsApi.unreadCount();
      setLocalStorage(UserNotifications, res.count);
      setCount(res.count);
    } catch (e) {
      console.warn("[notifications] refresh failed:", e);
    }
  }, []);

  // ✅ فقط یک بار mount و هر بار refreshKey عوض شود
  useEffect(() => {
    refresh();
  }, [refresh, refreshKey]);

  return { count, refresh };
};