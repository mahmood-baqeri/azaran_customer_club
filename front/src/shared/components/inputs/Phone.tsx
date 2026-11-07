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

export interface PhoneInputProps
     extends Omit<
          React.InputHTMLAttributes<HTMLInputElement>,
          "value" | "onChange" | "type" | "inputMode" | "maxLength"
     > {
     /** مقدار خام شماره (فقط اعداد) — controlled */
     value?: string;
     /** مقدار اولیه برای uncontrolled */
     defaultValue?: string;
     /** callback با مقدار خام (فقط اعداد) و مقدار فرمت‌شده */
     onChange?: (rawValue: string, formattedValue: string) => void;
     /** callback موقع blur — همراه با وضعیت اعتبار */
     onValidityChange?: (isValid: boolean) => void;
     /** حالت uncontrolled یا controlled را مشخص می‌کند */
     error?: boolean;
     /** نمایش پیام خطا زیر input */
     errorMessage?: string;
     /** پیش‌فرض: true — اعتبارسنجی شماره موبایل ایران */
     validateOnBlur?: boolean;
}

export interface PhoneInputRef {
     focus: () => void;
     blur: () => void;
     clear: () => void;
     isValid: () => boolean;
     getRawValue: () => string;
}

/* -------------------------------------------------------------------------- */
/*                                  Helpers                                   */
/* -------------------------------------------------------------------------- */

const IRAN_MOBILE_REGEX = /^09\d{9}$/;

/**
 * فقط اعداد را نگه می‌دارد و به ۱۱ رقم محدود می‌کند.
 */
const sanitize = (value: string): string =>
     value.replace(/\D/g, "").slice(0, 11);

/**
 * فرمت شماره به صورت `0913 123 4567`
 */
export const formatPhoneNumber = (value: string): string => {
     const digits = sanitize(value);
     if (!digits) return "";

     if (digits.length <= 4) return digits;
     if (digits.length <= 7) return `${digits.slice(0, 4)} ${digits.slice(4)}`;
     return `${digits.slice(0, 4)} ${digits.slice(4, 7)} ${digits.slice(7, 11)}`;
};

/**
 * اعتبارسنجی شماره موبایل ایران: `09XXXXXXXXX`
 */
export const isValidIranMobile = (value: string): boolean =>
     IRAN_MOBILE_REGEX.test(sanitize(value));

/**
 * موقعیت cursor را با توجه به تعداد اعداد قبل از آن محاسبه می‌کند.
 * این تابع باعث می‌شود هنگام تایپ/حذف، cursor در جای درست بماند.
 */
const getCursorFromDigitIndex = (
     formattedValue: string,
     digitIndex: number
): number => {
     if (digitIndex <= 0) return 0;

     let seen = 0;
     for (let i = 0; i < formattedValue.length; i++) {
          if (/\d/.test(formattedValue[i])) {
               seen++;
               if (seen === digitIndex) return i + 1;
          }
     }
     return formattedValue.length;
};

/**
 * تعداد اعداد قبل از موقعیت cursor در رشته را برمی‌گرداند.
 */
const countDigitsBefore = (value: string, cursor: number): number =>
     (value.slice(0, cursor).match(/\d/g) || []).length;

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const PhoneInput = forwardRef<PhoneInputRef, PhoneInputProps>(
     (
          {
               value,
               defaultValue = "",
               onChange,
               onValidityChange,
               onBlur,
               onFocus,
               error,
               errorMessage,
               validateOnBlur = true,
               dir = "ltr",
               style,
               className,
               disabled,
               ...rest
          },
          ref
     ) => {
          const inputRef = useRef<HTMLInputElement>(null);
          const isControlled = value !== undefined;

          const [internalRaw, setInternalRaw] = useState<string>(() =>
               sanitize(defaultValue)
          );
          const [touched, setTouched] = useState(false);

          // مقدار خام فعلی
          const rawValue = isControlled ? sanitize(value!) : internalRaw;
          const formattedValue = formatPhoneNumber(rawValue);

          const valid = isValidIranMobile(rawValue);
          const showError = (!!error || (touched && validateOnBlur && !valid && rawValue.length > 0)) && !!errorMessage;

          /* --------------------------- Imperative API --------------------------- */
          useImperativeHandle(
               ref,
               () => ({
                    focus: () => inputRef.current?.focus(),
                    blur: () => inputRef.current?.blur(),
                    clear: () => {
                         if (!isControlled) setInternalRaw("");
                         onChange?.("", "");
                         setTouched(false);
                         onValidityChange?.(false);
                    },
                    isValid: () => valid,
                    getRawValue: () => rawValue,
               }),
               [isControlled, onChange, onValidityChange, valid, rawValue]
          );

          /* -------------------------- Controlled sync --------------------------- */
          useEffect(() => {
               if (isControlled) {
                    onValidityChange?.(valid);
               }
               // eslint-disable-next-line react-hooks/exhaustive-deps
          }, [valid]);

          /* ------------------------------- Handlers ----------------------------- */

          const handleChange = useCallback(
               (e: React.ChangeEvent<HTMLInputElement>) => {
                    const input = e.target;
                    const selectionStart = input.selectionStart ?? input.value.length;

                    // تعداد اعداد قبل از cursor در مقدار جدید (فرمت‌شده)
                    const digitsBeforeCursor = countDigitsBefore(
                         input.value,
                         selectionStart
                    );

                    const nextRaw = sanitize(input.value);

                    // state را به‌روزرسانی کن
                    if (!isControlled) setInternalRaw(nextRaw);
                    const nextFormatted = formatPhoneNumber(nextRaw);
                    onChange?.(nextRaw, nextFormatted);

                    // بعد از re-render، cursor را در جای درست قرار بده
                    requestAnimationFrame(() => {
                         const el = inputRef.current;
                         if (!el) return;
                         const newPos = getCursorFromDigitIndex(
                              nextFormatted,
                              Math.min(digitsBeforeCursor, nextRaw.length)
                         );
                         el.setSelectionRange(newPos, newPos);
                    });
               },
               [isControlled, onChange]
          );

          const handleBlur = useCallback(
               (e: React.FocusEvent<HTMLInputElement>) => {
                    setTouched(true);
                    if (validateOnBlur) onValidityChange?.(valid);
                    onBlur?.(e);
               },
               [onBlur, onValidityChange, validateOnBlur, valid]
          );

          const handleFocus = useCallback(
               (e: React.FocusEvent<HTMLInputElement>) => {
                    onFocus?.(e);
               },
               [onFocus]
          );

          const handleKeyDown = useCallback(
               (e: React.KeyboardEvent<HTMLInputElement>) => {
                    // اجازه تایپ فقط اعداد و کلیدهای کنترلی
                    const allowedKeys = [
                         "Backspace",
                         "Delete",
                         "ArrowLeft",
                         "ArrowRight",
                         "ArrowUp",
                         "ArrowDown",
                         "Home",
                         "End",
                         "Tab",
                         "Enter",
                         "Escape",
                    ];

                    if (allowedKeys.includes(e.key)) return;
                    if (e.ctrlKey || e.metaKey) return; // copy/paste/...
                    if (!/^\d$/.test(e.key)) e.preventDefault();
               },
               []
          );

          /* ------------------------------- Render ------------------------------- */

          return (
               <div style={{ display: "flex", flexDirection: "column", gap: 6, position: "relative" }}>
                    <input
                         {...rest}
                         ref={inputRef}
                         type="tel"
                         inputMode="numeric"
                         autoComplete="tel-national"
                         placeholder="0913 123 4567"
                         value={formattedValue}
                         onChange={handleChange}
                         onKeyDown={handleKeyDown}
                         onBlur={handleBlur}
                         onFocus={handleFocus}
                         disabled={disabled}
                         maxLength={13}
                         dir={dir}
                         aria-invalid={showError}
                         aria-describedby={showError ? "phone-input-error" : undefined}
                         className={className}
                         style={{
                              textAlign: "left",
                              paddingRight: 15,
                              paddingLeft: 15,
                              borderColor: showError ? "#dc2626" : undefined,
                              ...style,
                         }}
                    />

                    {showError && (
                         <span
                              id="phone-input-error"
                              role="alert"
                              style={{ color: "#dc2626", fontSize: 12, position: "absolute", right: 6, bottom: -6, backgroundColor: "#fff", padding: "0 5px" }}
                         >
                              {errorMessage}
                         </span>
                    )}
               </div>
          );
     }
);

PhoneInput.displayName = "PhoneInput";

export default PhoneInput;