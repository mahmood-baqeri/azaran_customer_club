import React, {
     forwardRef,
     useCallback,
     useEffect,
     useImperativeHandle,
     useLayoutEffect,
     useMemo,
     useRef,
     useState,
} from "react";

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

export interface TextareaProps
     extends Omit<
          React.TextareaHTMLAttributes<HTMLTextAreaElement>,
          | "value"
          | "defaultValue"
          | "onChange"
          | "minLength"
          | "maxLength"
          | "cols"
     > {
     /** مقدار (controlled) */
     value?: string;
     /** مقدار اولیه (uncontrolled) */
     defaultValue?: string;

     /** حداقل طول مجاز */
     minLength?: number;
     /** حداکثر طول مجاز */
     maxLength?: number;

     /** حداقل تعداد خطوط (ارتفاع حداقلی) */
     minRows?: number;
     /** حداکثر تعداد خطوط — اگر ست نشود، نامحدود */
     maxRows?: number;

     /** رشد خودکار ارتفاع با تایپ (پیش‌فرض: true) */
     autoResize?: boolean;

     /** الگوی اعتبارسنجی */
     pattern?: RegExp | string;
     /** پیام خطای اختصاصی pattern */
     patternMessage?: string;

     /** trim هنگام blur (پیش‌فرض: true) */
     trimOnBlur?: boolean;
     /** تبدیل فاصله‌های تکراری به یک فاصله */
     collapseSpaces?: boolean;
     /** کاراکترهای مجاز */
     allowedChars?: RegExp;
     /** کاراکترهای غیرمجاز */
     disallowedChars?: RegExp;

     /** نمایش شمارنده کاراکتر (نیازمند maxLength) */
     showCounter?: boolean;
     /** نمایش شمارنده خطوط */
     showLineCounter?: boolean;

     /** callback با مقدار جدید */
     onChange?: (value: string) => void;
     /** callback هنگام blur با مقدار نهایی */
     onValueCommit?: (value: string) => void;
     /** callback وضعیت اعتبار */
     onValidityChange?: (isValid: boolean, reason?: string) => void;

     /** حالت خطا */
     error?: boolean;
     /** پیام خطا */
     errorMessage?: string;

     /** نمایش دکمه‌ی پاک کردن */
     clearable?: boolean;
}

export interface TextareaRef {
     focus: () => void;
     blur: () => void;
     clear: () => void;
     getValue: () => string;
     isValid: () => boolean;
     validate: () => { valid: boolean; reason?: string };
     /** محاسبه‌ی دستی ارتفاع — مفید برای وقتی مقدار برنامه‌نویسی تغییر می‌کند */
     resize: () => void;
}

/* -------------------------------------------------------------------------- */
/*                                  Helpers                                   */
/* -------------------------------------------------------------------------- */

const validateTextarea = (
     value: string,
     {
          minLength,
          maxLength,
          maxRows,
          pattern,
          required,
     }: {
          minLength?: number;
          maxLength?: number;
          maxRows?: number;
          pattern?: RegExp | string;
          required?: boolean;
     }
): { valid: boolean; reason?: string } => {
     if (required && value.trim() === "")
          return { valid: false, reason: "required" };
     if (value === "") return { valid: true };

     if (minLength !== undefined && value.length < minLength)
          return { valid: false, reason: "min-length" };
     if (maxLength !== undefined && value.length > maxLength)
          return { valid: false, reason: "max-length" };

     if (maxRows !== undefined) {
          const lines = value.split("\n").length;
          if (lines > maxRows) return { valid: false, reason: "max-rows" };
     }

     if (pattern) {
          const regex = pattern instanceof RegExp ? pattern : new RegExp(pattern);
          if (!regex.test(value)) return { valid: false, reason: "pattern" };
     }

     return { valid: true };
};

const applyAllowedChars = (
     value: string,
     allowed?: RegExp,
     disallowed?: RegExp
): string => {
     if (!allowed && !disallowed) return value;
     let result = "";
     for (const ch of value) {
          if (allowed && ch !== "\n" && !allowed.test(ch)) continue;
          if (disallowed && disallowed.test(ch)) continue;
          result += ch;
     }
     return result;
};

const collapseWhitespace = (value: string): string =>
     value.replace(/[^\S\n]+/g, " ").replace(/\n{2,}/g, "\n");

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const Textarea = forwardRef<TextareaRef, TextareaProps>(
     (
          {
               value,
               defaultValue = "",
               minLength,
               maxLength,
               minRows = 3,
               maxRows,
               autoResize = true,
               pattern,
               patternMessage,
               trimOnBlur = true,
               collapseSpaces = false,
               allowedChars,
               disallowedChars,
               showCounter = false,
               showLineCounter = false,
               clearable = false,
               onChange,
               onValueCommit,
               onValidityChange,
               onBlur,
               onFocus,
               error,
               errorMessage,
               disabled,
               className,
               style,
               dir = "rtl",
               required,
               rows, // ممکن است کاربر rows بدهد (از Omit حذف کردیم تا کنترل کامل داشته باشیم)
               ...rest
          },
          ref
     ) => {
          const textareaRef = useRef<HTMLTextAreaElement>(null);
          const isControlled = value !== undefined;

          const [internalValue, setInternalValue] = useState<string>(defaultValue);
          const [touched, setTouched] = useState(false);

          const currentValue = isControlled ? value ?? "" : internalValue;
          const lineCount = currentValue === "" ? 0 : currentValue.split("\n").length;

          /* ----------------------------- Validation ---------------------------- */
          const validation = useMemo(
               () =>
                    validateTextarea(currentValue, {
                         minLength,
                         maxLength,
                         maxRows,
                         pattern,
                         required,
                    }),
               [currentValue, minLength, maxLength, maxRows, pattern, required]
          );

          const resolvedErrorMessage =
               validation.reason === "pattern" && patternMessage
                    ? patternMessage
                    : errorMessage;

          const showError = !!error || (touched && !validation.valid);

          useEffect(() => {
               onValidityChange?.(validation.valid, validation.reason);
               // eslint-disable-next-line react-hooks/exhaustive-deps
          }, [validation.valid, validation.reason]);

          /* --------------------------- Auto-resize ----------------------------- */
          const resize = useCallback(() => {
               if (!autoResize) return;
               const el = textareaRef.current;
               if (!el) return;

               el.style.height = "auto";

               const cs = window.getComputedStyle(el);
               const lineHeight = parseFloat(cs.lineHeight) || 20;
               const paddingTop = parseFloat(cs.paddingTop) || 0;
               const paddingBottom = parseFloat(cs.paddingBottom) || 0;
               const borderTop = parseFloat(cs.borderTopWidth) || 0;
               const borderBottom = parseFloat(cs.borderBottomWidth) || 0;

               const minHeight = minRows * lineHeight + paddingTop + paddingBottom + borderTop + borderBottom;

               let nextHeight = Math.max(el.scrollHeight, minHeight);

               if (maxRows !== undefined) {
                    const maxHeight = maxRows * lineHeight + paddingTop + paddingBottom + borderTop + borderBottom;
                    nextHeight = Math.min(nextHeight, maxHeight);
                    el.style.overflowY = el.scrollHeight > maxHeight ? "auto" : "hidden";
               } else {
                    el.style.overflowY = "hidden";
               }

               el.style.height = `${nextHeight}px`;
          }, [autoResize, minRows, maxRows]);

          useLayoutEffect(() => {
               resize();
          }, [currentValue, resize]);

          // اگر اندازه‌ی container تغییر کرد
          useEffect(() => {
               if (!autoResize) return;
               const el = textareaRef.current;
               if (!el || typeof ResizeObserver === "undefined") return;
               const ro = new ResizeObserver(() => resize());
               ro.observe(el);
               return () => ro.disconnect();
          }, [autoResize, resize]);

          /* ------------------------------ Helpers ------------------------------ */
          const commit = useCallback(
               (next: string) => {
                    if (!isControlled) setInternalValue(next);
                    onChange?.(next);
               },
               [isControlled, onChange]
          );

          const sanitize = useCallback(
               (raw: string): string => {
                    let v = raw;
                    if (allowedChars || disallowedChars) {
                         v = applyAllowedChars(v, allowedChars, disallowedChars);
                    }
                    if (collapseSpaces) v = collapseWhitespace(v);
                    if (maxLength !== undefined) v = v.slice(0, maxLength);
                    if (maxRows !== undefined) {
                         const lines = v.split("\n");
                         if (lines.length > maxRows) v = lines.slice(0, maxRows).join("\n");
                    }
                    return v;
               },
               [allowedChars, disallowedChars, collapseSpaces, maxLength, maxRows]
          );

          /* ----------------------------- Handlers ------------------------------ */
          const handleChange = useCallback(
               (e: React.ChangeEvent<HTMLTextAreaElement>) => {
                    const next = sanitize(e.target.value);
                    commit(next);
               },
               [sanitize, commit]
          );

          const handleBlur = useCallback(
               (e: React.FocusEvent<HTMLTextAreaElement>) => {
                    setTouched(true);

                    let finalValue = currentValue;
                    if (trimOnBlur) finalValue = finalValue.trim();
                    if (collapseSpaces) finalValue = collapseWhitespace(finalValue);

                    if (finalValue !== currentValue) {
                         commit(finalValue);
                    }

                    onValueCommit?.(finalValue);
                    onBlur?.(e);
               },
               [currentValue, trimOnBlur, collapseSpaces, commit, onValueCommit, onBlur]
          );

          const handleClear = useCallback(() => {
               setTouched(false);
               commit("");
               onValueCommit?.("");
               textareaRef.current?.focus();
          }, [commit, onValueCommit]);

          /* --------------------------- Imperative API --------------------------- */
          useImperativeHandle(
               ref,
               () => ({
                    focus: () => textareaRef.current?.focus(),
                    blur: () => textareaRef.current?.blur(),
                    clear: () => handleClear(),
                    getValue: () => currentValue,
                    isValid: () => validation.valid,
                    validate: () => validation,
                    resize,
               }),
               [currentValue, validation, handleClear, resize]
          );

          /* ------------------------------- Render ------------------------------- */
          const remaining =
               maxLength !== undefined ? maxLength - currentValue.length : undefined;

          return (
               <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    <div style={{ position: "relative", display: "inline-flex", width: "100%" }}>
                         <textarea
                              {...rest}
                              ref={textareaRef}
                              value={currentValue}
                              onChange={handleChange}
                              onBlur={handleBlur}
                              onFocus={onFocus}
                              disabled={disabled}
                              required={required}
                              maxLength={maxLength}
                              minLength={minLength}
                              rows={autoResize ? minRows : rows ?? minRows}
                              dir={dir}
                              aria-invalid={showError}
                              aria-describedby={showError ? "textarea-error" : undefined}
                              className={className}
                              style={{
                                   width: "100%",
                                   resize: autoResize ? "none" : "vertical",
                                   overflowY: autoResize ? "hidden" : "auto",
                                   boxSizing: "border-box",
                                   borderColor: showError ? "#dc2626" : undefined,
                                   paddingLeft: clearable && currentValue ? 32 : undefined,
                                   ...style,
                              }}
                         />

                         {clearable && currentValue && !disabled && (
                              <button
                                   type="button"
                                   onClick={handleClear}
                                   aria-label="پاک کردن"
                                   tabIndex={-1}
                                   style={{
                                        position: "absolute",
                                        left: 8,
                                        top: 8,
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        fontSize: 16,
                                        color: "#6b7280",
                                        lineHeight: 1,
                                        padding: 4,
                                   }}
                              >
                                   ×
                              </button>
                         )}
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                         {showError ? (
                              <span
                                   id="textarea-error"
                                   role="alert"
                                   style={{ color: "#dc2626", fontSize: 12 }}
                              >
                                   {resolvedErrorMessage}
                              </span>
                         ) : (
                              <span />
                         )}

                         <div style={{ display: "flex", gap: 12, fontSize: 12, color: "#6b7280" }}>
                              {showLineCounter && (
                                   <span style={{ color: maxRows !== undefined && lineCount > maxRows ? "#dc2626" : undefined }}>
                                        {lineCount}
                                        {maxRows !== undefined ? ` / ${maxRows} خط` : " خط"}
                                   </span>
                              )}

                              {showCounter && maxLength !== undefined && (
                                   <span style={{ color: remaining !== undefined && remaining < 0 ? "#dc2626" : undefined }}>
                                        {currentValue.length} / {maxLength}
                                   </span>
                              )}
                         </div>
                    </div>
               </div>
          );
     }
);

Textarea.displayName = "Textarea";

export default Textarea;




/*


1. ساده با auto-resize
tsx
const [bio, setBio] = useState("");

<Textarea
  value={bio}
  onChange={setBio}
  placeholder="درباره من..."
  minRows={3}
  maxRows={6}
  maxLength={500}
  showCounter
/>




2. با حداکثر خطوط
tsx
const [description, setDescription] = useState("");

<Textarea
  value={description}
  onChange={setDescription}
  minRows={4}
  maxRows={8}
  showLineCounter
  errorMessage="حداکثر ۸ خط مجاز است"
/>




3. با اعتبارسنجی طول
tsx
const [comment, setComment] = useState("");

<Textarea
  value={comment}
  onChange={setComment}
  minLength={10}
  maxLength={1000}
  required
  showCounter
  errorMessage="نظر باید بین ۱۰ تا ۱۰۰۰ کاراکتر باشد"
/>




4. توضیحات HTML-free (regex)
tsx
<Textarea
  value={description}
  onChange={setDescription}
  pattern={/^[^<>]*$/}
  patternMessage="استفاده از تگ‌های HTML مجاز نیست"
  trimOnBlur
  collapseSpaces
/>




5. با clearable
tsx
<Textarea
  value={notes}
  onChange={setNotes}
  clearable
  placeholder="یادداشت..."
  minRows={2}
  maxRows={10}
/>




6. با ref برای resize دستی
tsx
const taRef = useRef<TextareaRef>(null);

<Textarea ref={taRef} autoResize />

<button onClick={() => taRef.current?.resize()}>دوباره‌سازی ارتفاع</button>
<button onClick={() => taRef.current?.clear()}>پاک کردن</button>
<button onClick={() => console.log(taRef.current?.validate())}>
  بررسی اعتبار
</button>




7. با react-hook-form
tsx
<Controller
  name="description"
  control={control}
  rules={{
    required: "توضیحات الزامی است",
    minLength: { value: 10, message: "حداقل ۱۰ کاراکتر" },
    maxLength: { value: 500, message: "حداکثر ۵۰۰ کاراکتر" },
  }}
  render={({ field, fieldState }) => (
    <Textarea
      value={field.value ?? ""}
      onChange={field.onChange}
      onValueCommit={field.onChange}
      error={!!fieldState.error}
      errorMessage={fieldState.error?.message}
      minLength={10}
      maxLength={500}
      minRows={3}
      maxRows={8}
      showCounter
      showLineCounter
    />
  )}
/>



*/