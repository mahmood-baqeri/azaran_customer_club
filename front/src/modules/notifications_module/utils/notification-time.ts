// front/src/modules/notifications_module/utils/notification-time.ts

/** زمان نسبی برای نمایش در کارت (۱ ساعت پیش، ۳ روز پیش، ...) */
export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return "";
  const t = new Date(iso).getTime();
  if (isNaN(t)) return "";
  const diff = Math.floor((Date.now() - t) / 1000);
  if (diff < 60) return "همین حالا";
  if (diff < 3600) return `${Math.floor(diff / 60)} دقیقه پیش`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} ساعت پیش`;
  if (diff < 7 * 86400) return `${Math.floor(diff / 86400)} روز پیش`;
  return new Date(iso).toLocaleDateString("fa-IR");
}

/** تاریخ و ساعت کامل (شمسی) برای مودال جزئیات */
export function formatFullDateTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  return d.toLocaleString("fa-IR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}