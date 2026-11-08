/* eslint-disable react-refresh/only-export-components */
import React, {
     forwardRef,
     useCallback,
     useEffect,
     useImperativeHandle,
     useRef,
     useState,
} from "react";

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

export interface ImageUploadProps {
     /** فایل انتخاب‌شده (controlled) */
     value?: File | null;
     /** فایل اولیه (uncontrolled) */
     defaultValue?: File | null;
     /** آدرس تصویر خارجی (مثلاً از سرور در حالت ویرایش) — وقتی فایلی انتخاب نشده نمایش داده می‌شود */
     externalPreviewUrl?: string | null;
     /** callback با فایل انتخاب‌شده یا null هنگام حذف */
     onChange?: (file: File | null, previewUrl: string | null) => void;
     /** callback خطا */
     onError?: (error: string, reason: ImageUploadErrorReason) => void;

     /** accept پیش‌فرض: image/* */
     accept?: string;
     /** حداکثر حجم به بایت — پیش‌فرض ۵ مگابایت */
     maxSize?: number;
     /** پیام‌های خطای سفارشی */
     errorMessages?: Partial<Record<ImageUploadErrorReason, string>>;

     /** عنوان اصلی — پیش‌فرض "گرفتن عکس فاکتور" */
     label?: React.ReactNode;
     /** توضیح زیر عنوان */
     hint?: React.ReactNode;
     /** ارتفاع کادر — پیش‌فرض 120 */
     height?: number;
     /** گوشه‌ها — پیش‌فرض 12 */
     borderRadius?: number;
     /** رنگ متن */
     textColor?: string;

     /** رنگ اصلی — پیش‌فرض #A2A2A2 */
     accentColor?: string;
     /** پس‌زمینه حالت خالی — پیش‌فرض #f4f6fa */
     emptyBackground?: string;

     /** فعال‌کردن انتخاب از دوربین — پیش‌فرض true */
     enableCamera?: boolean;
     /** فعال‌کردن گالری — پیش‌فرض true */
     enableGallery?: boolean;
     /** فعال‌کردن Drag & Drop — پیش‌فرض true */
     enableDrop?: boolean;

     disabled?: boolean;
     className?: string;
     style?: React.CSSProperties;

     /** حالت خطای دستی */
     error?: string;
}

export type ImageUploadErrorReason =
     | "size"
     | "type"
     | "empty"
     | "read-error";

export interface ImageUploadRef {
     open: () => void;
     openCamera: () => void;
     clear: () => void;
     getFile: () => File | null;
     getPreviewUrl: () => string | null;
}

/* -------------------------------------------------------------------------- */
/*                             Default messages                               */
/* -------------------------------------------------------------------------- */

const DEFAULT_ERROR_MESSAGES: Record<ImageUploadErrorReason, string> = {
     size: "حجم تصویر بیش از حد مجاز است",
     type: "فرمت فایل پشتیبانی نمی‌شود",
     empty: "فایلی انتخاب نشده است",
     "read-error": "خطا در خواندن فایل",
};

const formatBytes = (bytes: number): string => {
     if (bytes < 1024) return `${bytes} B`;
     if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
     return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
};

/* -------------------------------------------------------------------------- */
/*                                 Icons                                      */
/* -------------------------------------------------------------------------- */

const CameraIcon = ({ size = 26 }: { size?: number }) => (
     <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
          <circle cx="12" cy="13" r="4" />
     </svg>
);

const GalleryIcon = ({ size = 22 }: { size?: number }) => (
     <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <path d="M21 15l-5-5L5 21" />
     </svg>
);

const CloseIcon = ({ size = 18 }: { size?: number }) => (
     <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
     </svg>
);

const RefreshIcon = ({ size = 16 }: { size?: number }) => (
     <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="23 4 23 10 17 10" />
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
     </svg>
);

/* -------------------------------------------------------------------------- */
/*                              Inline styles                                 */
/* -------------------------------------------------------------------------- */

const iconBtnStyle = (bg: string, color: string): React.CSSProperties => ({
     width: 28,
     height: 28,
     borderRadius: "50%",
     border: "none",
     background: bg,
     color,
     display: "inline-flex",
     alignItems: "center",
     justifyContent: "center",
     cursor: "pointer",
     padding: 0,
     boxShadow: "0 1px 4px rgba(0,0,0,.2)",
});

const pillBtnStyle = (color: string): React.CSSProperties => ({
     display: "inline-flex",
     alignItems: "center",
     gap: 4,
     padding: "4px 10px",
     borderRadius: 999,
     border: `1px solid ${color}`,
     background: "#fff",
     color,
     fontSize: 11,
     fontWeight: 600,
     cursor: "pointer",
});

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const ImageUpload = forwardRef<ImageUploadRef, ImageUploadProps>(
     (
          {
               value,
               defaultValue = null,
               externalPreviewUrl = null,
               onChange,
               onError,
               accept = "image/*",
               maxSize = 5 * 1024 * 1024,
               errorMessages,
               label = "گرفتن عکس فاکتور",
               hint,
               height = 120,
               borderRadius = 12,
               accentColor = "#A2A2A2",
               textColor = "#14306b",
               emptyBackground = "#f4f6fa",
               enableCamera = true,
               enableGallery = true,
               enableDrop = true,
               disabled = false,
               className,
               style,
               error,
          },
          ref
     ) => {
          const isControlled = value !== undefined;

          const [internalFile, setInternalFile] = useState<File | null>(
               defaultValue
          );
          const [objectUrl, setObjectUrl] = useState<string | null>(null);
          const [internalError, setInternalError] = useState<string | null>(null);
          const [isDragging, setIsDragging] = useState(false);

          const file = isControlled ? value : internalFile;

          const fileInputRef = useRef<HTMLInputElement>(null);
          const cameraInputRef = useRef<HTMLInputElement>(null);
          const dragCounter = useRef(0);

          const getErrorMessage = useCallback(
               (reason: ImageUploadErrorReason): string =>
                    errorMessages?.[reason] ??
                    DEFAULT_ERROR_MESSAGES[reason],
               [errorMessages]
          );

          const emitError = useCallback(
               (reason: ImageUploadErrorReason, custom?: string) => {
                    const msg = custom ?? getErrorMessage(reason);
                    setInternalError(msg);
                    onError?.(msg, reason);
               },
               [getErrorMessage, onError]
          );

          /* --------------------- preview URL management ----------------------- */
          useEffect(() => {
               if (!file) {
                    setObjectUrl(null);
                    return;
               }
               const url = URL.createObjectURL(file);
               setObjectUrl(url);
               return () => URL.revokeObjectURL(url);
          }, [file]);

          // ✅ اولویت: فایل جدید → تصویر خارجی (سرور) → null
          const previewUrl = objectUrl ?? externalPreviewUrl ?? null;

          /* ------------------------ file validation --------------------------- */
          const validateFile = useCallback(
               (f: File): ImageUploadErrorReason | null => {
                    if (!f) return "empty";

                    if (accept && accept !== "image/*") {
                         const acceptList = accept
                              .split(",")
                              .map((s) => s.trim().toLowerCase());
                         const fileType = f.type.toLowerCase();
                         const fileName = f.name.toLowerCase();
                         const ok = acceptList.some((a) => {
                              if (a.startsWith(".")) return fileName.endsWith(a);
                              if (a.endsWith("/*"))
                                   return fileType.startsWith(a.replace("/*", "/"));
                              return fileType === a;
                         });
                         if (!ok) return "type";
                    } else if (!f.type.startsWith("image/")) {
                         return "type";
                    }

                    if (f.size > maxSize) return "size";
                    return null;
               },
               [accept, maxSize]
          );

          const handleFile = useCallback(
               (f: File | null) => {
                    if (disabled) return;

                    if (!f) {
                         setInternalError(null);
                         if (!isControlled) setInternalFile(null);
                         onChange?.(null, null);
                         return;
                    }

                    const reason = validateFile(f);
                    if (reason) {
                         emitError(
                              reason,
                              reason === "size"
                                   ? `حجم فایل بیش از ${formatBytes(maxSize)} است`
                                   : undefined
                         );
                         return;
                    }

                    setInternalError(null);
                    if (!isControlled) setInternalFile(f);
                    onChange?.(f, URL.createObjectURL(f));
               },
               [
                    disabled,
                    isControlled,
                    onChange,
                    validateFile,
                    emitError,
                    maxSize,
               ]
          );

          /* ---------------------------- handlers ----------------------------- */
          const handleInputChange = useCallback(
               (e: React.ChangeEvent<HTMLInputElement>) => {
                    const f = e.target.files?.[0] ?? null;
                    handleFile(f);
                    // reset تا انتخاب دوباره‌ی همون فایل هم trigger بشه
                    e.target.value = "";
               },
               [handleFile]
          );

          const handleClear = useCallback(
               (e: React.MouseEvent) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setInternalError(null);
                    if (!isControlled) setInternalFile(null);
                    onChange?.(null, null);
               },
               [isControlled, onChange]
          );

          const handleReplace = useCallback((e: React.MouseEvent) => {
               e.preventDefault();
               e.stopPropagation();
               fileInputRef.current?.click();
          }, []);

          const handleCameraClick = useCallback((e: React.MouseEvent) => {
               e.preventDefault();
               e.stopPropagation();
               cameraInputRef.current?.click();
          }, []);

          const handleGalleryClick = useCallback((e: React.MouseEvent) => {
               e.preventDefault();
               e.stopPropagation();
               fileInputRef.current?.click();
          }, []);

          /* ------------------------- drag & drop ----------------------------- */
          const handleDragEnter = useCallback(
               (e: React.DragEvent) => {
                    if (!enableDrop || disabled) return;
                    e.preventDefault();
                    dragCounter.current++;
                    setIsDragging(true);
               },
               [enableDrop, disabled]
          );

          const handleDragLeave = useCallback(
               (e: React.DragEvent) => {
                    if (!enableDrop || disabled) return;
                    e.preventDefault();
                    dragCounter.current--;
                    if (dragCounter.current === 0) setIsDragging(false);
               },
               [enableDrop, disabled]
          );

          const handleDragOver = useCallback(
               (e: React.DragEvent) => {
                    if (!enableDrop || disabled) return;
                    e.preventDefault();
               },
               [enableDrop, disabled]
          );

          const handleDrop = useCallback(
               (e: React.DragEvent) => {
                    if (!enableDrop || disabled) return;
                    e.preventDefault();
                    dragCounter.current = 0;
                    setIsDragging(false);
                    const f = e.dataTransfer.files?.[0] ?? null;
                    handleFile(f);
               },
               [enableDrop, disabled, handleFile]
          );

          /* --------------------------- imperative ---------------------------- */
          useImperativeHandle(
               ref,
               () => ({
                    open: () => fileInputRef.current?.click(),
                    openCamera: () => cameraInputRef.current?.click(),
                    clear: () => {
                         setInternalError(null);
                         if (!isControlled) setInternalFile(null);
                         onChange?.(null, null);
                    },
                    getFile: () => file ?? null,
                    getPreviewUrl: () => previewUrl,
               }),
               [file, previewUrl, isControlled, onChange]
          );

          /* ------------------------------ derived ---------------------------- */
          const borderColor =
               error || internalError
                    ? "#dc2626"
                    : isDragging
                         ? "#2563eb"
                         : accentColor;

          const hasFile = !!previewUrl;
          const showError = !!(internalError || error);

          return (
               <div
                    className={className}
                    style={{
                         display: "flex",
                         flexDirection: "column",
                         gap: 6,
                         ...style,
                    }}
               >
                    <div
                         role="button"
                         tabIndex={disabled ? -1 : 0}
                         aria-disabled={disabled}
                         aria-label={typeof label === "string" ? label : "آپلود تصویر"}
                         onClick={() => {
                              if (disabled || hasFile) return;
                              fileInputRef.current?.click();
                         }}
                         onKeyDown={(e) => {
                              if (disabled || hasFile) return;
                              if (e.key === "Enter" || e.key === " ") {
                                   e.preventDefault();
                                   fileInputRef.current?.click();
                              }
                         }}
                         onDragEnter={handleDragEnter}
                         onDragOver={handleDragOver}
                         onDragLeave={handleDragLeave}
                         onDrop={handleDrop}
                         style={{
                              position: "relative",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              flexDirection: "column",
                              gap: 8,
                              height,
                              borderRadius,
                              border: `2px dashed ${borderColor}`,
                              color: textColor,
                              fontWeight: 700,
                              fontSize: 14,
                              cursor: disabled ? "not-allowed" : "pointer",
                              background: hasFile ? "#000" : emptyBackground,
                              overflow: "hidden",
                              opacity: disabled ? 0.6 : 1,
                              transition: "border-color .15s, background .15s",
                              outline: "none",
                         }}
                    >
                         {/* ---------- حالت با تصویر ---------- */}
                         {hasFile ? (
                              <>
                                   {/* تصویر */}
                                   <img
                                        src={previewUrl!}
                                        alt="پیش‌نمایش فاکتور"
                                        style={{
                                             position: "absolute",
                                             inset: 0,
                                             width: "100%",
                                             height: "100%",
                                             objectFit: "cover",
                                             pointerEvents: "none",
                                        }}
                                   />

                                   {/* gradient پایین — غیرکلیک‌پذیر */}
                                   <div
                                        aria-hidden="true"
                                        style={{
                                             position: "absolute",
                                             inset: 0,
                                             background:
                                                  "linear-gradient(to top, rgba(0,0,0,.55), rgba(0,0,0,0) 55%)",
                                             pointerEvents: "none",
                                        }}
                                   />

                                   {/* بج نام و حجم فایل */}
                                   {file && (
                                        <div
                                             style={{
                                                  position: "absolute",
                                                  top: 6,
                                                  right: 8,
                                                  fontSize: 10,
                                                  color: "#fff",
                                                  background: "rgba(0,0,0,.55)",
                                                  padding: "2px 8px",
                                                  borderRadius: 999,
                                                  direction: "rtl",
                                                  maxWidth: "calc(100% - 16px)",
                                                  overflow: "hidden",
                                                  textOverflow: "ellipsis",
                                                  whiteSpace: "nowrap",
                                                  pointerEvents: "none",
                                             }}
                                             title={file.name}
                                        >
                                             {file.name} · {formatBytes(file.size)}
                                        </div>
                                   )}

                                   {/* دکمه‌های سمت چپ */}
                                   <div
                                        style={{
                                             position: "absolute",
                                             left: 8,
                                             bottom: 8,
                                             display: "flex",
                                             gap: 6,
                                        }}
                                   >
                                        <button
                                             type="button"
                                             onClick={handleReplace}
                                             disabled={disabled}
                                             aria-label="تعویض تصویر"
                                             title="تعویض تصویر"
                                             style={iconBtnStyle("rgba(255,255,255,.92)", "#14306b")}
                                        >
                                             <RefreshIcon />
                                        </button>
                                        {enableCamera && (
                                             <button
                                                  type="button"
                                                  onClick={handleCameraClick}
                                                  disabled={disabled}
                                                  aria-label="گرفتن عکس جدید"
                                                  title="گرفتن عکس جدید"
                                                  style={iconBtnStyle("rgba(255,255,255,.92)", "#14306b")}
                                             >
                                                  <CameraIcon size={16} />
                                             </button>
                                        )}
                                   </div>

                                   {/* دکمه‌ی حذف سمت راست */}
                                   <button
                                        type="button"
                                        onClick={handleClear}
                                        disabled={disabled}
                                        aria-label="حذف تصویر"
                                        title="حذف تصویر"
                                        style={{
                                             ...iconBtnStyle("rgba(220,38,38,.95)", "#fff"),
                                             position: "absolute",
                                             right: 8,
                                             bottom: 8,
                                        }}
                                   >
                                        <CloseIcon />
                                   </button>
                              </>
                         ) : (
                              /* ---------- حالت خالی ---------- */
                              <>
                                   <CameraIcon />
                                   <span>{isDragging ? "رها کنید تا آپلود شود" : label}</span>
                                   {hint && (
                                        <span
                                             style={{
                                                  fontSize: 11,
                                                  fontWeight: 400,
                                                  opacity: 0.75,
                                             }}
                                        >
                                             {hint}
                                        </span>
                                   )}

                                   {(enableCamera || enableGallery) && (
                                        <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                                             {enableCamera && (
                                                  <button
                                                       type="button"
                                                       onClick={handleCameraClick}
                                                       disabled={disabled}
                                                       style={pillBtnStyle(accentColor)}
                                                  >
                                                       <CameraIcon size={14} />
                                                       دوربین
                                                  </button>
                                             )}
                                             {enableGallery && (
                                                  <button
                                                       type="button"
                                                       onClick={handleGalleryClick}
                                                       disabled={disabled}
                                                       style={pillBtnStyle(accentColor)}
                                                  >
                                                       <GalleryIcon size={14} />
                                                       گالری
                                                  </button>
                                             )}
                                        </div>
                                   )}
                              </>
                         )}

                         {/* input مخفی — گالری */}
                         <input
                              ref={fileInputRef}
                              type="file"
                              accept={accept}
                              onChange={handleInputChange}
                              disabled={disabled}
                              style={{ display: "none" }}
                         />

                         {/* input مخفی — دوربین */}
                         <input
                              ref={cameraInputRef}
                              type="file"
                              accept={accept}
                              capture="environment"
                              onChange={handleInputChange}
                              disabled={disabled}
                              style={{ display: "none" }}
                         />
                    </div>

                    {showError && (
                         <span
                              role="alert"
                              style={{ color: "#dc2626", fontSize: 12 }}
                         >
                              {internalError ?? error}
                         </span>
                    )}
               </div>
          );
     }
);

ImageUpload.displayName = "ImageUpload";
export default ImageUpload;

/*



استفاده



۱. ساده — جایگزین کد فعلی شما:

tsx
const [photo, setPhoto] = useState<File | null>(null);

<ImageUpload
     value={photo}
     onChange={(file) => setPhoto(file)}
     label="گرفتن عکس فاکتور"
/>




۲. با پیام خطای سفارشی و محدودیت ۲ مگابایت:

tsx
<ImageUpload
     value={photo}
     onChange={setPhoto}
     maxSize={2 * 1024 * 1024}
     errorMessages={{
          size: "حداکثر حجم مجاز ۲ مگابایت است",
          type: "فقط فایل‌های JPG و PNG پذیرفته می‌شوند",
     }}
     hint="فرمت JPG یا PNG — حداکثر ۲ مگابایت"
/>




۳. فقط دوربین (بدون گالری):

tsx
<ImageUpload
     enableGallery={false}
     enableCamera
     label="گرفتن عکس فاکتور"
/>





۴. با react-hook-form:

tsx
<Controller
     name="invoicePhoto"
     control={control}
     rules={{
          required: "عکس فاکتور الزامی است",
          validate: (f) => f instanceof File || "لطفاً یک تصویر انتخاب کنید",
     }}
     render={({ field, fieldState }) => (
          <ImageUpload
               value={field.value ?? null}
               onChange={(f) => field.onChange(f)}
               error={fieldState.error?.message}
          />
     )}
/>





۵. با ref:

tsx
const photoRef = useRef<ImageUploadRef>(null);

<ImageUpload ref={photoRef} />

<button onClick={() => photoRef.current?.openCamera()}>دوربین</button>
<button onClick={() => photoRef.current?.open()}>گالری</button>
<button onClick={() => photoRef.current?.clear()}>حذف</button>
<button onClick={() => console.log(photoRef.current?.getFile())}>دریافت فایل</button>


*/