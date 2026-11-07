/* eslint-disable react-hooks/exhaustive-deps */
import React, {
     forwardRef,
     useCallback,
     useEffect,
     useId,
     useImperativeHandle,
     useMemo,
     useRef,
     useState,
} from "react";

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

export type FileRejectionReason =
     | "too-large"
     | "too-small"
     | "invalid-type"
     | "max-files"
     | "duplicate"
     | "read-error";

export interface FileValidationError {
     file: File;
     reason: FileRejectionReason;
     message: string;
}

export interface FileWithMeta {
     file: File;
     /** URL پیش‌نمایش (برای تصاویر) — خودتان revoke نکنید، کامپوننت مدیریت می‌کند */
     previewUrl?: string;
     /** درصد پیشرفت آپلود (0-100) — اگر آپلود دستی مدیریت شود */
     progress?: number;
     /** وضعیت آپلود */
     status?: "idle" | "uploading" | "success" | "error";
     /** پیام خطای سرور (اختیاری) */
     errorMessage?: string;
}

export interface FileInputProps
     extends Omit<
          React.InputHTMLAttributes<HTMLInputElement>,
          | "type"
          | "value"
          | "defaultValue"
          | "onChange"
          | "multiple"
          | "accept"
          | "capture"
     > {
     /** فایل‌های فعلی (controlled) */
     value?: FileWithMeta[];
     /** فایل‌های اولیه (uncontrolled) */
     defaultValue?: FileWithMeta[];

     /** اجازه‌ی انتخاب چند فایل (پیش‌فرض: false) */
     multiple?: boolean;
     /** حداکثر تعداد فایل مجاز */
     maxFiles?: number;

     /** انواع مجاز — پسوند (`.png`) یا MIME (`image/*`, `application/pdf`) */
     accept?: string | string[];

     /** حداکثر حجم هر فایل (بایت) */
     maxSize?: number;
     /** حداقل حجم هر فایل (بایت) */
     minSize?: number;

     /** ساخت پیش‌نمایش تصویر (پیش‌فرض: true برای image/*) */
     preview?: boolean;

     /** callback با فایل‌های پذیرفته‌شده و رد‌شده */
     onChange?: (accepted: FileWithMeta[], rejected: FileValidationError[]) => void;
     /** callback برای هر فایل به‌صورت جداگانه (ساده‌تر) */
     onFilesChange?: (files: File[]) => void;

     /** حالت خطا */
     error?: boolean;
     /** پیام خطا */
     errorMessage?: string;

     /** متن/راهنمای dropzone */
     placeholder?: string;
     /** متن ثانویه */
     hint?: string;

     /** نمایش پیش‌نمایش تصویر */
     showThumbnails?: boolean;
     /** نمایش دکمه‌ی حذف روی هر فایل */
     clearable?: boolean;
     /** نمایش دکمه‌ی «همه را پاک کن» */
     clearAll?: boolean;
     /** امکان کلیک روی dropzone برای باز کردن file dialog */
     clickable?: boolean;

     /** کلاس dropzone */
     dropzoneClassName?: string;
     /** استایل dropzone */
     dropzoneStyle?: React.CSSProperties;

     /** نام حالت drag فعال (برای استایل‌دهی سفارشی) */
     onDragStateChange?: (isDragging: boolean) => void;
}

export interface FileInputRef {
     /** باز کردن پنجره‌ی انتخاب فایل */
     open: () => void;
     /** پاک کردن همه‌ی فایل‌ها */
     clear: () => void;
     /** حذف یک فایل */
     remove: (index: number) => void;
     /** دریافت فایل‌های فعلی */
     getFiles: () => File[];
     /** اعتبارسنجی فایل‌های فعلی */
     validate: () => { valid: boolean; errors: FileValidationError[] };
     /** افزودن برنامه‌نویسی فایل‌ها */
     addFiles: (files: File[] | FileList) => void;
}

/* -------------------------------------------------------------------------- */
/*                                  Helpers                                   */
/* -------------------------------------------------------------------------- */

const DEFAULT_MAX_SIZE = 10 * 1024 * 1024; // 10MB
const DANGEROUS_EXTENSIONS = [
     ".exe", ".bat", ".cmd", ".sh", ".scr", ".msi", ".com", ".pif",
     ".vbs", ".js", ".jar", ".app", ".dmg",
];

const isImage = (file: File): boolean => file.type.startsWith("image/");

const formatBytes = (bytes: number): string => {
     if (bytes === 0) return "0 B";
     const k = 1024;
     const sizes = ["B", "KB", "MB", "GB"];
     const i = Math.floor(Math.log(bytes) / Math.log(k));
     return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

/**
 * بررسی تطابق فایل با accept (هم پسوند، هم MIME).
 */
const matchAccept = (file: File, accept: string[]): boolean => {
     if (accept.length === 0) return true;
     const fileExt = "." + (file.name.split(".").pop() || "").toLowerCase();
     const mime = file.type.toLowerCase();

     return accept.some((pattern) => {
          const p = pattern.trim().toLowerCase();
          if (!p) return false;

          // پسوند
          if (p.startsWith(".")) return fileExt === p;

          // MIME wildcard
          if (p.endsWith("/*")) {
               const prefix = p.slice(0, -1); // "image/"
               return mime.startsWith(prefix);
          }

          // MIME دقیق
          return mime === p;
     });
};

/**
 * ساخت URL پیش‌نمایش برای تصاویر
 */
const createPreviewUrl = (file: File): string | undefined => {
     if (!isImage(file)) return undefined;
     try {
          return URL.createObjectURL(file);
     } catch {
          return undefined;
     }
};

/**
 * اعتبارسنجی یک فایل
 */
const validateFile = (
     file: File,
     {
          accept,
          maxSize,
          minSize,
          currentFiles,
     }: {
          accept: string[];
          maxSize?: number;
          minSize?: number;
          currentFiles: FileWithMeta[];
     }
): FileValidationError | null => {
     const fileExt = "." + (file.name.split(".").pop() || "").toLowerCase();

     // امنیت
     if (DANGEROUS_EXTENSIONS.includes(fileExt)) {
          return {
               file,
               reason: "invalid-type",
               message: `فرمت ${fileExt} به دلایل امنیتی مجاز نیست`,
          };
     }

     // نوع
     if (!matchAccept(file, accept)) {
          return {
               file,
               reason: "invalid-type",
               message: `فرمت فایل مجاز نیست (مجاز: ${accept.join(", ")})`,
          };
     }

     // حجم
     if (maxSize !== undefined && file.size > maxSize) {
          return {
               file,
               reason: "too-large",
               message: `حجم فایل بیشتر از ${formatBytes(maxSize)} است`,
          };
     }
     if (minSize !== undefined && file.size < minSize) {
          return {
               file,
               reason: "too-small",
               message: `حجم فایل کمتر از ${formatBytes(minSize)} است`,
          };
     }

     // تکراری
     const exists = currentFiles.some(
          (f) =>
               f.file.name === file.name &&
               f.file.size === file.size &&
               f.file.lastModified === file.lastModified
     );
     if (exists) {
          return {
               file,
               reason: "duplicate",
               message: "این فایل قبلاً اضافه شده است",
          };
     }

     return null;
};

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const FileInput = forwardRef<FileInputRef, FileInputProps>(
     (
          {
               value,
               defaultValue = [],
               multiple = false,
               maxFiles,
               accept,
               maxSize = DEFAULT_MAX_SIZE,
               minSize,
               preview = true,
               onChange,
               onFilesChange,
               error,
               errorMessage,
               placeholder = "فایل را اینجا رها کنید یا کلیک کنید",
               hint,
               showThumbnails = true,
               clearable = true,
               clearAll = true,
               clickable = true,
               dropzoneClassName,
               dropzoneStyle,
               onDragStateChange,
               disabled,
               className,
               style,
               dir = "rtl",
               required,
               ...rest
          },
          ref
     ) => {
          const inputRef = useRef<HTMLInputElement>(null);
          const inputId = useId();
          const isControlled = value !== undefined;

          const acceptList = useMemo<string[]>(() => {
               if (!accept) return [];
               return Array.isArray(accept) ? accept : accept.split(",").map((s) => s.trim()).filter(Boolean);
          }, [accept]);

          const [internalFiles, setInternalFiles] = useState<FileWithMeta[]>(defaultValue);
          const [isDragging, setIsDragging] = useState(false);
          const [errors, setErrors] = useState<FileValidationError[]>([]);
          const [touched, setTouched] = useState(false);

          const currentFiles = isControlled ? value ?? [] : internalFiles;

          /* --------------------------- Preview cleanup -------------------------- */
          // پاک‌کردن previewUrl فایل‌هایی که حذف شده‌اند
          const previousUrls = useRef<Set<string>>(new Set());

          useEffect(() => {
               const currentUrls = new Set(
                    currentFiles.map((f) => f.previewUrl).filter(Boolean) as string[]
               );
               // URLهای قدیمی که در currentUrls نیستند → revoke
               previousUrls.current.forEach((url) => {
                    if (!currentUrls.has(url)) {
                         try { URL.revokeObjectURL(url); } catch { /* noop */ }
                    }
               });
               previousUrls.current = currentUrls;
          }, [currentFiles]);

          // پاک‌سازی نهایی در unmount
          useEffect(() => {
               return () => {
                    previousUrls.current.forEach((url) => {
                         try { URL.revokeObjectURL(url); } catch { /* noop */ }
                    });
               };
          }, []);


          /* --------------------------- Process files ---------------------------- */
          const processFiles = useCallback(
               (files: FileList | File[]) => {
                    const incoming = Array.from(files);
                    const accepted: FileWithMeta[] = [];
                    const rejected: FileValidationError[] = [];
                    const allRejected: FileValidationError[] = [];

                    let working = [...currentFiles];

                    for (const file of incoming) {
                         // بررسی maxFiles
                         if (maxFiles !== undefined && working.length >= maxFiles) {
                              allRejected.push({
                                   file,
                                   reason: "max-files",
                                   message: `حداکثر ${maxFiles} فایل مجاز است`,
                              });
                              continue;
                         }

                         const err = validateFile(file, {
                              accept: acceptList,
                              maxSize,
                              minSize,
                              currentFiles: working,
                         });

                         if (err) {
                              rejected.push(err);
                              allRejected.push(err);
                              continue;
                         }

                         const item: FileWithMeta = {
                              file,
                              previewUrl: preview ? createPreviewUrl(file) : undefined,
                              status: "idle",
                         };
                         accepted.push(item);
                         working = multiple ? [...working, item] : [item];

                         if (!multiple) break; // فقط یک فایل
                    }

                    // state نهایی
                    let next: FileWithMeta[];
                    if (multiple) {
                         next = [...currentFiles, ...accepted];
                    } else {
                         next = accepted.length > 0 ? accepted : currentFiles;
                    }

                    if (!isControlled) setInternalFiles(next);

                    // free URLs فایل‌های رد شده
                    for (const a of accepted) {
                         if (a.previewUrl && !next.includes(a)) {
                              try { URL.revokeObjectURL(a.previewUrl); } catch { /* noop */ }
                         }
                    }
                    // فایل‌های قبلی که به‌خاطر single mode حذف شدند
                    currentFiles.forEach((old) => {
                         if (!next.includes(old) && old.previewUrl) {
                              try { URL.revokeObjectURL(old.previewUrl); } catch { /* noop */ }
                         }
                    });

                    setErrors(allRejected);
                    setTouched(true);

                    onChange?.(next, allRejected);
                    onFilesChange?.(next.map((f) => f.file));
               },
               [acceptList, currentFiles, isControlled, maxFiles, maxSize, minSize, multiple, onChange, onFilesChange, preview]
          );

          /* ----------------------------- Handlers ------------------------------- */
          const handleInputChange = useCallback(
               (e: React.ChangeEvent<HTMLInputElement>) => {
                    const files = e.target.files;
                    if (files && files.length > 0) processFiles(files);
                    // reset تا انتخاب مجدد همان فایل هم trigger شود
                    e.target.value = "";
               },
               [processFiles]
          );

          const handleClick = useCallback(() => {
               if (disabled || !clickable) return;
               inputRef.current?.click();
          }, [clickable, disabled]);

          const handleDragOver = useCallback(
               (e: React.DragEvent<HTMLDivElement>) => {
                    if (disabled) return;
                    e.preventDefault();
                    e.stopPropagation();
                    if (!isDragging) {
                         setIsDragging(true);
                         onDragStateChange?.(true);
                    }
               },
               [disabled, isDragging, onDragStateChange]
          );

          const handleDragLeave = useCallback(
               (e: React.DragEvent<HTMLDivElement>) => {
                    if (disabled) return;
                    e.preventDefault();
                    e.stopPropagation();
                    setIsDragging(false);
                    onDragStateChange?.(false);
               },
               [disabled, onDragStateChange]
          );

          const handleDrop = useCallback(
               (e: React.DragEvent<HTMLDivElement>) => {
                    if (disabled) return;
                    e.preventDefault();
                    e.stopPropagation();
                    setIsDragging(false);
                    onDragStateChange?.(false);

                    const items = e.dataTransfer?.files;
                    if (items && items.length > 0) processFiles(items);
               },
               [disabled, onDragStateChange, processFiles]
          );

          const handleRemove = useCallback(
               (index: number) => {
                    if (disabled) return;
                    const target = currentFiles[index];
                    if (!target) return;

                    if (target.previewUrl) {
                         try { URL.revokeObjectURL(target.previewUrl); } catch { /* noop */ }
                    }

                    const next = currentFiles.filter((_, i) => i !== index);
                    if (!isControlled) setInternalFiles(next);
                    onChange?.(next, []);
                    onFilesChange?.(next.map((f) => f.file));
               },
               [currentFiles, disabled, isControlled, onChange, onFilesChange]
          );

          const handleClear = useCallback(() => {
               if (disabled) return;
               currentFiles.forEach((f) => {
                    if (f.previewUrl) {
                         try { URL.revokeObjectURL(f.previewUrl); } catch { /* noop */ }
                    }
               });
               if (!isControlled) setInternalFiles([]);
               setErrors([]);
               setTouched(false);
               onChange?.([], []);
               onFilesChange?.([]);
          }, [currentFiles, disabled, isControlled, onChange, onFilesChange]);

          /* --------------------------- Imperative API --------------------------- */
          useImperativeHandle(
               ref,
               () => ({
                    open: () => inputRef.current?.click(),
                    clear: handleClear,
                    remove: handleRemove,
                    getFiles: () => currentFiles.map((f) => f.file),
                    validate: () => {
                         const errs: FileValidationError[] = [];
                         currentFiles.forEach((f) => {
                              const err = validateFile(f.file, {
                                   accept: acceptList,
                                   maxSize,
                                   minSize,
                                   currentFiles,
                              });
                              if (err) errs.push(err);
                         });
                         return { valid: errs.length === 0, errors: errs };
                    },
                    addFiles: (files) => processFiles(files),
               }),
               [currentFiles, handleClear, handleRemove, processFiles, acceptList, maxSize, minSize]
          );

          /* ------------------------------- Render ------------------------------- */
          const showError = !!error || (touched && errors.length > 0);
          const hasFiles = currentFiles.length > 0;

          return (
               <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {/* input مخفی */}
                    <input
                         {...rest}
                         ref={inputRef}
                         id={inputId}
                         type="file"
                         accept={acceptList.join(",") || undefined}
                         multiple={multiple}
                         disabled={disabled}
                         required={required && !hasFiles}
                         onChange={handleInputChange}
                         style={{ display: "none" }}
                         aria-hidden="true"
                         tabIndex={-1}
                    />

                    {/* Dropzone */}
                    <div
                         role="button"
                         tabIndex={disabled ? -1 : 0}
                         onClick={handleClick}
                         onKeyDown={(e) => {
                              if (e.key === "Enter" || e.key === " ") {
                                   e.preventDefault();
                                   handleClick();
                              }
                         }}
                         onDragOver={handleDragOver}
                         onDragEnter={handleDragOver}
                         onDragLeave={handleDragLeave}
                         onDrop={handleDrop}
                         className={[className, dropzoneClassName].filter(Boolean).join(" ") || undefined}
                         aria-disabled={disabled}
                         aria-invalid={showError}
                         aria-label={placeholder}
                         aria-describedby={showError ? `${inputId}-error` : undefined}
                         style={{
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              justifyContent: "center",
                              gap: 8,
                              padding: 24,
                              border: `2px dashed ${showError ? "#dc2626" : isDragging ? "#2563eb" : "#d1d5db"}`,
                              borderRadius: 12,
                              background: isDragging ? "rgba(37,99,235,0.05)" : "#fafafa",
                              cursor: disabled ? "not-allowed" : clickable ? "pointer" : "default",
                              textAlign: "center",
                              transition: "all 120ms ease",
                              opacity: disabled ? 0.6 : 1,
                              outline: "none",
                              ...dropzoneStyle,
                              ...style,
                         }}
                    >
                         <svg
                              width="32"
                              height="32"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              style={{ color: isDragging ? "#2563eb" : "#6b7280" }}
                         >
                              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                              <polyline points="17 8 12 3 7 8" />
                              <line x1="12" y1="3" x2="12" y2="15" />
                         </svg>

                         <span style={{ fontSize: 14, color: "#374151", fontWeight: 500 }}>
                              {placeholder}
                         </span>

                         {hint && (
                              <span style={{ fontSize: 12, color: "#6b7280" }}>{hint}</span>
                         )}

                         <span style={{ fontSize: 11, color: "#9ca3af" }}>
                              حداکثر {formatBytes(maxSize)}
                              {acceptList.length > 0 && ` • ${acceptList.join("، ")}`}
                              {multiple && ` • تا ${maxFiles ?? "نامحدود"} فایل`}
                         </span>
                    </div>

                    {/* File list */}
                    {hasFiles && (
                         <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                   <span style={{ fontSize: 12, color: "#6b7280" }}>
                                        {currentFiles.length} فایل
                                        {maxFiles !== undefined && ` از ${maxFiles}`}
                                   </span>
                                   {clearAll && !disabled && (
                                        <button
                                             type="button"
                                             onClick={handleClear}
                                             style={{
                                                  fontSize: 12,
                                                  color: "#dc2626",
                                                  background: "transparent",
                                                  border: "none",
                                                  cursor: "pointer",
                                                  padding: 4,
                                             }}
                                        >
                                             پاک کردن همه
                                        </button>
                                   )}
                              </div>

                              <ul
                                   dir={dir}
                                   style={{
                                        listStyle: "none",
                                        margin: 0,
                                        padding: 0,
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 4,
                                   }}
                              >
                                   {currentFiles.map((item, idx) => (
                                        <li
                                             key={`${item.file.name}-${item.file.lastModified}-${idx}`}
                                             style={{
                                                  display: "flex",
                                                  alignItems: "center",
                                                  gap: 8,
                                                  padding: 8,
                                                  border: "1px solid #e5e7eb",
                                                  borderRadius: 8,
                                                  background: "#fff",
                                             }}
                                        >
                                             {showThumbnails && item.previewUrl ? (
                                                  <img
                                                       src={item.previewUrl}
                                                       alt={item.file.name}
                                                       style={{
                                                            width: 40,
                                                            height: 40,
                                                            objectFit: "cover",
                                                            borderRadius: 6,
                                                            border: "1px solid #e5e7eb",
                                                            flexShrink: 0,
                                                       }}
                                                  />
                                             ) : (
                                                  <div
                                                       style={{
                                                            width: 40,
                                                            height: 40,
                                                            display: "flex",
                                                            alignItems: "center",
                                                            justifyContent: "center",
                                                            borderRadius: 6,
                                                            border: "1px solid #e5e7eb",
                                                            background: "#f9fafb",
                                                            fontSize: 10,
                                                            color: "#6b7280",
                                                            flexShrink: 0,
                                                            textTransform: "uppercase",
                                                       }}
                                                  >
                                                       {(item.file.name.split(".").pop() || "FILE").slice(0, 4)}
                                                  </div>
                                             )}

                                             <div style={{ flex: 1, minWidth: 0 }}>
                                                  <div
                                                       style={{
                                                            fontSize: 13,
                                                            color: "#111827",
                                                            whiteSpace: "nowrap",
                                                            overflow: "hidden",
                                                            textOverflow: "ellipsis",
                                                       }}
                                                       title={item.file.name}
                                                  >
                                                       {item.file.name}
                                                  </div>
                                                  <div style={{ fontSize: 11, color: "#6b7280" }}>
                                                       {formatBytes(item.file.size)}
                                                       {item.status === "uploading" && ` • در حال آپلود ${item.progress ?? 0}%`}
                                                       {item.status === "success" && " • آپلود شد"}
                                                       {item.status === "error" && (
                                                            <span style={{ color: "#dc2626" }}> • {item.errorMessage ?? "خطا"}</span>
                                                       )}
                                                  </div>
                                                  {item.status === "uploading" && (
                                                       <div
                                                            style={{
                                                                 marginTop: 4,
                                                                 height: 4,
                                                                 background: "#e5e7eb",
                                                                 borderRadius: 2,
                                                                 overflow: "hidden",
                                                            }}
                                                       >
                                                            <div
                                                                 style={{
                                                                      height: "100%",
                                                                      width: `${item.progress ?? 0}%`,
                                                                      background: "#2563eb",
                                                                      transition: "width 200ms ease",
                                                                 }}
                                                            />
                                                       </div>
                                                  )}
                                             </div>

                                             {clearable && !disabled && (
                                                  <button
                                                       type="button"
                                                       onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleRemove(idx);
                                                       }}
                                                       aria-label={`حذف ${item.file.name}`}
                                                       style={{
                                                            border: "none",
                                                            background: "transparent",
                                                            cursor: "pointer",
                                                            color: "#6b7280",
                                                            fontSize: 18,
                                                            lineHeight: 1,
                                                            padding: 4,
                                                            borderRadius: 4,
                                                       }}
                                                  >
                                                       ×
                                                  </button>
                                             )}
                                        </li>
                                   ))}
                              </ul>
                         </div>
                    )}

                    {/* Errors */}
                    {showError && (
                         <div
                              id={`${inputId}-error`}
                              role="alert"
                              style={{
                                   padding: 8,
                                   background: "#fef2f2",
                                   border: "1px solid #fecaca",
                                   borderRadius: 6,
                                   fontSize: 12,
                                   color: "#dc2626",
                                   display: "flex",
                                   flexDirection: "column",
                                   gap: 2,
                              }}
                         >
                              {errorMessage && <span style={{ fontWeight: 600 }}>{errorMessage}</span>}
                              {errors.map((err, i) => (
                                   <span key={i}>
                                        <strong>{err.file.name}:</strong> {err.message}
                                   </span>
                              ))}
                         </div>
                    )}
               </div>
          );
     }
);

FileInput.displayName = "FileInput";

export default FileInput;





/*


1. ساده — یک فایل تصویری
tsx
const [avatar, setAvatar] = useState<FileWithMeta[]>([]);

<FileInput
  value={avatar}
  onChange={(accepted) => setAvatar(accepted)}
  accept="image/*"
  maxSize={2 * 1024 * 1024} // 2MB
  placeholder="عکس پروفایل را انتخاب کنید"
  hint="JPG یا PNG، حداکثر ۲ مگابایت"
/>








2. چند فایلی با محدودیت تعداد
tsx
const [docs, setDocs] = useState<FileWithMeta[]>([]);

<FileInput
  multiple
  maxFiles={5}
  value={docs}
  onChange={(accepted, rejected) => {
    setDocs(accepted);
    if (rejected.length > 0) console.warn(rejected);
  }}
  accept={["application/pdf", ".docx", ".xlsx"]}
  maxSize={5 * 1024 * 1024}
  clearAll
/>








3. با آپلود دستی و نمایش progress
tsx
const [files, setFiles] = useState<FileWithMeta[]>([]);

const handleUpload = async (index: number) => {
  const item = files[index];
  const formData = new FormData();
  formData.append("file", item.file);

  // آپدیت state
  setFiles((prev) =>
    prev.map((f, i) => (i === index ? { ...f, status: "uploading", progress: 0 } : f))
  );

  try {
    // با XHR تا progress داشته باشیم
    await new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/upload");
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 100);
          setFiles((prev) =>
            prev.map((f, i) => (i === index ? { ...f, progress: pct } : f))
          );
        }
      };
      xhr.onload = () => (xhr.status < 400 ? resolve() : reject());
      xhr.onerror = reject;
      xhr.send(formData);
    });

    setFiles((prev) =>
      prev.map((f, i) =>
        i === index ? { ...f, status: "success", progress: 100 } : f
      )
    );
  } catch {
    setFiles((prev) =>
      prev.map((f, i) =>
        i === index ? { ...f, status: "error", errorMessage: "آپلود ناموفق" } : f
      )
    );
  }
};

<FileInput value={files} onChange={setFiles} multiple accept="image/*" />







4. فقط از طریق دکمه (بدون click روی dropzone)
tsx
<FileInput
  clickable={false}
  accept=".pdf"
  placeholder="فایل را رها کنید"
/>








5. با ref
tsx
const ref = useRef<FileInputRef>(null);

<FileInput ref={ref} accept="image/*" multiple />

<button onClick={() => ref.current?.open()}>انتخاب فایل</button>
<button onClick={() => ref.current?.clear()}>پاک کردن</button>
<button onClick={() => console.log(ref.current?.getFiles())}>دریافت</button>
<button onClick={() => console.log(ref.current?.validate())}>
  بررسی اعتبار
</button>










6. با react-hook-form
tsx
<Controller
  name="attachments"
  control={control}
  rules={{
    validate: (v) => (v && v.length > 0) || "حداقل یک فایل الزامی است",
  }}
  render={({ field, fieldState }) => (
    <FileInput
      value={field.value ?? []}
      onChange={(accepted) => field.onChange(accepted)}
      multiple
      maxFiles={3}
      accept="image/*,application/pdf"
      maxSize={5 * 1024 * 1024}
      error={!!fieldState.error}
      errorMessage={fieldState.error?.message}
      clearAll
    />
  )}
/>



*/