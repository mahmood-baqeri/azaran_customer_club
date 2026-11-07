/* eslint-disable react-refresh/only-export-components */
// src/modules/project_module/components/FileCard.tsx

import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

export type FileCardStatus = "approved" | "pending" | "rejected";

export interface FileCardProps {
     /** نام فایل */
     name: string;
     /** حجم فایل به بایت */
     sizeInBytes?: number;
     /** callback حذف — فقط وقتی status داده نشده باشد نمایش داده می‌شود */
     onRemove?: () => void;
     /** وضعیت اعتبار — در صورت ارسال، دکمه‌ی حذف مخفی می‌شود */
     status?: FileCardStatus;
     /** حداکثر طول نمایش نام فایل (پیش‌فرض ۱۰۰) */
     maxNameLength?: number;
}

/* -------------------------------------------------------------------------- */
/*                                  Helpers                                   */
/* -------------------------------------------------------------------------- */

/**
 * فرمت خوانا برای حجم فایل
 * 512           → "512 B"
 * 2048          → "2 KB"
 * 1536 * 1024   → "1.5 MB"
 */
export function formatFileSize(bytes: number | undefined | null): string {
     if (bytes === undefined || bytes === null || Number.isNaN(bytes) || bytes < 0) {
          return "—";
     }
     if (bytes === 0) return "0 B";

     const units = ["B", "KB", "MB", "GB", "TB"];
     const k = 1024;
     const i = Math.min(
          Math.floor(Math.log(bytes) / Math.log(k)),
          units.length - 1
     );
     const value = bytes / Math.pow(k, i);
     // برای B و KB گرد می‌کنیم، برای بقیه یک رقم اعشار
     const formatted = i <= 1 ? Math.round(value) : parseFloat(value.toFixed(1));
     return `${formatted} ${units[i]}`;
}

/**
 * کوتاه کردن نام فایل به maxLength کاراکتر با "..." در انتها
 * (طول نهایی = maxLength + ۳ برای سه‌نقطه)
 */
export function truncateFilename(name: string, maxLength: number): string {
     if (!name || name.length <= maxLength) return name;
     return name.slice(0, maxLength) + "...";
}

/* -------------------------------------------------------------------------- */
/*                              Status Badge                                  */
/* -------------------------------------------------------------------------- */

function StatusBadge({ type }: { type: FileCardStatus }) {
     const map: Record<FileCardStatus, { label: string; bg: string; color: string }> = {
          approved: { label: "تایید شده", bg: "#a3eee9", color: "#275a90" },
          pending: { label: "در انتظار بررسی", bg: "#feeea2", color: "#275a90" },
          rejected: { label: "رد شده", bg: "#ff9999", color: "#275a90" },
     };
     const s = map[type];
     return (
          <span
               style={{
                    background: s.bg,
                    color: s.color,
                    padding: "6px 16px",
                    borderRadius: 8,
                    fontSize: 12,
                    fontWeight: 600,
                    whiteSpace: "nowrap",
               }}
          >
               {s.label}
          </span>
     );
}

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export default function FileCard({
     name,
     sizeInBytes,
     onRemove,
     status,
     maxNameLength = 100,
}: FileCardProps) {
     const displayName = truncateFilename(name, maxNameLength);
     const sizeLabel = formatFileSize(sizeInBytes);

     const canRemove = !!onRemove && (!status || status === "pending");

     return (
          <div className="project-file-card" >
               <div style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0, flex: 1 }}>
                    <MyImage src={ICONS.jpg} className="w__20" />
                    <div style={{ display: "flex", flexDirection: "column", minWidth: 0, flex: 1 }}>
                         <span className="--n" dir="ltr" title={name} >
                              {displayName}
                         </span>
                         <span style={{ fontSize: 11, color: "#94a3b8" }}>
                              {sizeLabel}
                         </span>
                    </div>
               </div>

               <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    {status && <StatusBadge type={status} />}

                    {canRemove && (
                         <div className="pointer" onClick={onRemove}>
                              <MyImage src={ICONS.trash} className="w__15" />
                         </div>
                    )}
               </div>
          </div>
     );
}