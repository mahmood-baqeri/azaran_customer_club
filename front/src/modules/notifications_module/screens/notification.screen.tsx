// front/src/modules/notifications_module/screen/notification.screen.tsx

import { useMemo, useState } from "react";
import Header from "../../../app/layouts/header";
import "../../../shared/styles/notification-page.css";
import { NotificationGroupData, NotificationItemData } from "../interface/notification.types";
import { NotificationItem } from "../components/notifications.item";
import { NotificationDetailModal } from "../components/notification-detail-modal";
import { useNotificationList, useNotifications } from "../hooks/use-notifications";
import { notificationsRepository } from "../repository/notifications.repository";
import { MyNotification } from "../../../shared/utils/notification";
import { getErrorMessage } from "../../../shared/api/errors";

// ─── گروه‌بندی بر اساس تاریخ ───
function startOfDay(d: Date): number {
     const x = new Date(d);
     x.setHours(0, 0, 0, 0);
     return x.getTime();
}

function groupByDate(items: NotificationItemData[]): NotificationGroupData[] {
     const now = new Date();
     const todayStart = startOfDay(now);
     const yesterdayStart = todayStart - 86_400_000;
     const weekStart = todayStart - 6 * 86_400_000;

     const buckets: Record<"today" | "yesterday" | "week" | "older", NotificationItemData[]> = {
          today: [],
          yesterday: [],
          week: [],
          older: [],
     };

     for (const it of items) {
          const iso = it.sent_at ?? it.created_at;
          const t = iso ? new Date(iso).getTime() : 0;
          if (t >= todayStart) buckets.today.push(it);
          else if (t >= yesterdayStart) buckets.yesterday.push(it);
          else if (t >= weekStart) buckets.week.push(it);
          else buckets.older.push(it);
     }

     const labels = {
          today: "امروز",
          yesterday: "دیروز",
          week: "این هفته",
          older: "قبل‌تر",
     } as const;

     return (Object.keys(buckets) as (keyof typeof buckets)[])
          .filter((k) => buckets[k].length > 0)
          .map((k) => ({ id: k, group: labels[k], items: buckets[k] }));
}

// ─── صفحه ───
export default function NotificationScreen() {
     const {
          items,
          loading,
          loadingMore,
          error,
          page,
          totalPages,
          loadMore,
          reload,
          markItemRead,
          // markAllLocalRead,
          removeItem,
     } = useNotificationList();

     const { refresh: refreshCount } = useNotifications();

     const [selected, setSelected] = useState<NotificationItemData | null>(null);
     // const [markingAll, setMarkingAll] = useState(false);

     const groups = useMemo(() => groupByDate(items), [items]);
     // const hasUnread = items.some((it) => !it.is_read);

     const handleOpen = (item: NotificationItemData) => {
          setSelected(item);
          if (!item.is_read) {
               markItemRead(item.id); // به‌روزرسانی خوش‌بینانه
               refreshCount();
               notificationsRepository.markRead(item.id).catch((e) => {
                    console.warn("[notifications] markRead failed:", e);
               });
          }
     };

     const handleDismiss = async (item: NotificationItemData) => {
          try {
               await notificationsRepository.dismiss(item.id);
               removeItem(item.id);
               setSelected(null);
               refreshCount();
          } catch (e) {
               MyNotification("", getErrorMessage(e, "حذف اعلان ناموفق بود"), "error");
          }
     };

     // const handleMarkAllRead = async () => {
     //      if (markingAll) return;
     //      setMarkingAll(true);
     //      try {
     //           await notificationsRepository.markAllRead();
     //           markAllLocalRead();
     //           refreshCount();
     //      } catch (e) {
     //           MyNotification("", getErrorMessage(e, "خطا در خواندن همه"), "error");
     //      } finally {
     //           setMarkingAll(false);
     //      }
     // };

     // ─── Loading ───
     if (loading) {
          return (
               <>
                    <Header title="اعلان‌ها" showLogo={false} showBack={true} menuBg="f7f8fb" buttonBg="white" />
                    <div className="d-flex justify-content-center py-5">
                         <div className="spinner-border" style={{ color: "#0d3b66" }} role="status">
                              <span className="visually-hidden">در حال بارگذاری...</span>
                         </div>
                    </div>
               </>
          );
     }

     return (
          <>
               <Header
                    title="اعلان‌ها"
                    showLogo={false}
                    showBack={true}
                    menuBg="f7f8fb"
                    buttonBg="white"
               // action={
               //      hasUnread ? (
               //           <button
               //                type="button"
               //                className="header-action-btn"
               //                onClick={handleMarkAllRead}
               //                disabled={markingAll}
               //           >
               //                <span className="color-primary fw-400 me-1 fs-12">
               //                     {markingAll ? "..." : "خواندن همه"}
               //                </span>
               //           </button>
               //      ) : null
               // }
               />

               <div className="px-3 py-3">
                    {/* خطا */}
                    {error && (
                         <div className="text-center py-5">
                              <p className="text-muted fs-13">{error}</p>
                              <button className="btn bg-primary text-white rounded-3 fs-13" onClick={reload}>
                                   تلاش مجدد
                              </button>
                         </div>
                    )}

                    {/* خالی */}
                    {!error && items.length === 0 && (
                         <div className="text-center py-5">
                              <p className="text-muted fs-13">هنوز اعلانی ندارید</p>
                         </div>
                    )}

                    {/* گروه‌ها */}
                    {!error &&
                         groups.map((group) => (
                              <div key={group.id} className="mb-4">
                                   <div className="text-end mb-2 pe-1">
                                        <span className="color-primary fs-13">{group.group}</span>
                                   </div>
                                   <div className="d-flex flex-column gap-2">
                                        {group.items.map((item) => (
                                             <NotificationItem key={item.id} item={item} onOpen={handleOpen} />
                                        ))}
                                   </div>
                              </div>
                         ))}

                    {/* Load more */}
                    {!error && page < totalPages && (
                         <div className="d-flex justify-content-center py-3">
                              <button
                                   className="btn btn-light rounded-3 fs-13"
                                   onClick={loadMore}
                                   disabled={loadingMore}
                              >
                                   {loadingMore ? "در حال بارگذاری..." : "بارگذاری بیشتر"}
                              </button>
                         </div>
                    )}
               </div>

               {/* مودال جزئیات */}
               {selected && (
                    <NotificationDetailModal
                         item={selected}
                         onClose={() => setSelected(null)}
                         onDismiss={() => handleDismiss(selected)}
                    />
               )}
          </>
     );
}