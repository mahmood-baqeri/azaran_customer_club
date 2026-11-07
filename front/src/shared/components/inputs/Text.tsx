import React, {
     forwardRef,
     useCallback,
     useEffect,
     useImperativeHandle,
     useMemo,
     useRef,
     useState,
} from "react";

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

export interface TextInputProps
     extends Omit<
          React.InputHTMLAttributes<HTMLInputElement>,
          | "type"
          | "value"
          | "defaultValue"
          | "onChange"
          | "minLength"
          | "maxLength"
          | "pattern"
     > {
     /** مقدار (controlled) */
     value?: string;
     /** مقدار اولیه (uncontrolled) */
     defaultValue?: string;

     /** حداقل طول مجاز */
     minLength?: number;
     /** حداکثر طول مجاز */
     maxLength?: number;
     /** الگوی اعتبارسنجی (RegExp یا string) */
     pattern?: RegExp | string;
     /** پیام خطای اختصاصی برای عدم تطابق pattern */
     patternMessage?: string;

     /** trim کردن مقدار هنگام blur (پیش‌فرض: true) */
     trimOnBlur?: boolean;
     /** حذف فاصله‌های اضافی (پیش‌فرض: false) */
     collapseSpaces?: boolean;
     /** تبدیل به حروف کوچک / بزرگ (اختیاری) */
     transform?: "none" | "lowercase" | "uppercase";
     /** کاراکترهای مجاز (به‌صورت regex روی هر کاراکتر) — مثال: /[a-zA-Z0-9]/ */
     allowedChars?: RegExp;
     /** کاراکترهای غیرمجاز */
     disallowedChars?: RegExp;

     /** نمایش شمارنده کاراکتر (نیازمند maxLength) */
     showCounter?: boolean;

     /** callback با مقدار جدید */
     onChange?: (value: string) => void;
     /** callback موقع blur — مقدار نهایی (trim شده) */
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

export interface TextInputRef {
     focus: () => void;
     blur: () => void;
     clear: () => void;
     getValue: () => string;
     isValid: () => boolean;
     validate: () => { valid: boolean; reason?: string };
}

/* -------------------------------------------------------------------------- */
/*                                  Helpers                                   */
/* -------------------------------------------------------------------------- */

const validateText = (
     value: string,
     {
          minLength,
          maxLength,
          pattern,
          required,
     }: {
          minLength?: number;
          maxLength?: number;
          pattern?: RegExp | string;
          required?: boolean;
     }
): { valid: boolean; reason?: string } => {
     if (required && value.trim() === "") return { valid: false, reason: "required" };
     if (value === "") return { valid: true }; // خالی معتبر است اگر اجباری نباشد

     if (minLength !== undefined && value.length < minLength)
          return { valid: false, reason: "min-length" };
     if (maxLength !== undefined && value.length > maxLength)
          return { valid: false, reason: "max-length" };

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
          if (allowed && !allowed.test(ch)) continue;
          if (disallowed && disallowed.test(ch)) continue;
          result += ch;
     }
     return result;
};

const applyTransform = (
     value: string,
     transform: "none" | "lowercase" | "uppercase"
): string => {
     if (transform === "lowercase") return value.toLowerCase();
     if (transform === "uppercase") return value.toUpperCase();
     return value;
};

const collapseWhitespace = (value: string): string =>
     value.replace(/\s+/g, " ");

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const TextInput = forwardRef<TextInputRef, TextInputProps>(
     (
          {
               value,
               defaultValue = "",
               minLength,
               maxLength,
               pattern,
               patternMessage,
               trimOnBlur = true,
               collapseSpaces = false,
               transform = "none",
               allowedChars,
               disallowedChars,
               showCounter = false,
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
               ...rest
          },
          ref
     ) => {
          const inputRef = useRef<HTMLInputElement>(null);
          const isControlled = value !== undefined;

          const [internalValue, setInternalValue] = useState<string>(defaultValue);
          const [touched, setTouched] = useState(false);

          const currentValue = isControlled ? value ?? "" : internalValue;

          /* ----------------------------- Validation ---------------------------- */
          const validation = useMemo(
               () =>
                    validateText(currentValue, {
                         minLength,
                         maxLength,
                         pattern,
                         required,
                    }),
               [currentValue, minLength, maxLength, pattern, required]
          );

          const showError =
               (!!error || (touched && !validation.valid)) &&
               (!!errorMessage || (touched && !validation.valid && validation.reason === "pattern" && !!patternMessage));

          const resolvedErrorMessage =
               validation.reason === "pattern" && patternMessage
                    ? patternMessage
                    : errorMessage;

          useEffect(() => {
               onValidityChange?.(validation.valid, validation.reason);
               // eslint-disable-next-line react-hooks/exhaustive-deps
          }, [validation.valid, validation.reason]);

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
                    v = applyTransform(v, transform);
                    if (maxLength !== undefined) v = v.slice(0, maxLength);
                    return v;
               },
               [allowedChars, disallowedChars, collapseSpaces, transform, maxLength]
          );

          /* ----------------------------- Handlers ------------------------------ */
          const handleChange = useCallback(
               (e: React.ChangeEvent<HTMLInputElement>) => {
                    const next = sanitize(e.target.value);
                    commit(next);
               },
               [sanitize, commit]
          );

          const handleBlur = useCallback(
               (e: React.FocusEvent<HTMLInputElement>) => {
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
               inputRef.current?.focus();
          }, [commit, onValueCommit]);

          /* --------------------------- Imperative API --------------------------- */
          useImperativeHandle(
               ref,
               () => ({
                    focus: () => inputRef.current?.focus(),
                    blur: () => inputRef.current?.blur(),
                    clear: () => handleClear(),
                    getValue: () => currentValue,
                    isValid: () => validation.valid,
                    validate: () => validation,
               }),
               [currentValue, validation, handleClear]
          );

          /* ------------------------------- Render ------------------------------- */
          const remaining =
               maxLength !== undefined ? maxLength - currentValue.length : undefined;

          return (
               <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    <div style={{ position: "relative", display: "inline-flex", width: "100%" }}>
                         <input
                              {...rest}
                              ref={inputRef}
                              type="text"
                              value={currentValue}
                              onChange={handleChange}
                              onBlur={handleBlur}
                              onFocus={onFocus}
                              disabled={disabled}
                              required={required}
                              maxLength={maxLength}
                              minLength={minLength}
                              dir={dir}
                              aria-invalid={showError}
                              aria-describedby={
                                   showError ? "text-input-error" : undefined
                              }
                              className={className}
                              style={{
                                   width: "100%",
                                   borderColor: showError ? "#dc2626" : undefined,
                                   paddingLeft: clearable && currentValue ? 40 : undefined,
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
                                        top: "50%",
                                        transform: "translateY(-50%)",
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

                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                         {showError ? (
                              <span
                                   id="text-input-error"
                                   role="alert"
                                   style={{ color: "#dc2626", fontSize: 12 }}
                              >
                                   {resolvedErrorMessage}
                              </span>
                         ) : (
                              <span />
                         )}

                         {showCounter && maxLength !== undefined && (
                              <span
                                   style={{
                                        fontSize: 12,
                                        color:
                                             remaining !== undefined && remaining < 0
                                                  ? "#dc2626"
                                                  : "#6b7280",
                                   }}
                              >
                                   {currentValue.length} / {maxLength}
                              </span>
                         )}
                    </div>
               </div>
          );
     }
);

TextInput.displayName = "TextInput";

export default TextInput;



/*


1. ساده با شمارنده کاراکتر
tsx
const [name, setName] = useState("");

<TextInput
  value={name}
  onChange={setName}
  placeholder="نام"
  maxLength={50}
  showCounter
  errorMessage="نام حداکثر ۵۰ کاراکتر است"
/>



2. حداقل / حداکثر طول
tsx
const [username, setUsername] = useState("");

<TextInput
  value={username}
  onChange={setUsername}
  minLength={3}
  maxLength={20}
  required
  errorMessage="نام کاربری باید بین ۳ تا ۲۰ کاراکتر باشد"
/>



3. فقط حروف انگلیسی (برای نام کاربری)
tsx
<TextInput
  value={username}
  onChange={setUsername}
  allowedChars={/[a-zA-Z0-9_]/}
  minLength={3}
  errorMessage="فقط حروف انگلیسی، عدد و زیرخط مجاز است"
/>



4. الگوی regex (ایمیل)
tsx
<TextInput
  value={email}
  onChange={setEmail}
  pattern={/^[^\s@]+@[^\s@]+\.[^\s@]+$/}
  patternMessage="ایمیل معتبر نیست"
  trimOnBlur
  required
  errorMessage="ایمیل را وارد کنید"
/>



5. کد ملی (فقط رقم، ۱۰ کاراکتر)
tsx
<TextInput
  value={nationalId}
  onChange={setNationalId}
  allowedChars={/\d/}
  maxLength={10}
  minLength={10}
  showCounter
  errorMessage="کد ملی باید ۱۰ رقم باشد"
/>



6. کد پستی با transform به uppercase
tsx
<TextInput
  value={code}
  onChange={setCode}
  allowedChars={/[a-zA-Z0-9]/}
  transform="uppercase"
  maxLength={10}
/>



7. با clearable
tsx
<TextInput
  value={search}
  onChange={setSearch}
  clearable
  placeholder="جستجو..."
/>



8. با ref
tsx
const ref = useRef<TextInputRef>(null);

<TextInput ref={ref} />
<button onClick={() => ref.current?.clear()}>پاک</button>
<button onClick={() => console.log(ref.current?.validate())}>
  بررسی اعتبار
</button>



9. با react-hook-form
tsx
<Controller
  name="username"
  control={control}
  rules={{
    required: "نام کاربری الزامی است",
    minLength: { value: 3, message: "حداقل ۳ کاراکتر" },
    pattern: { value: /^[a-zA-Z0-9_]+$/, message: "فقط حروف و عدد" },
  }}
  render={({ field, fieldState }) => (
    <TextInput
      value={field.value ?? ""}
      onChange={field.onChange}
      onValueCommit={field.onChange}
      error={!!fieldState.error}
      errorMessage={fieldState.error?.message}
      minLength={3}
      maxLength={20}
      showCounter
    />
  )}
/>


*/
