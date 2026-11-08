/* eslint-disable react-refresh/only-export-components */
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

export type LandlineValidationReason =
     | "empty"
     | "missing-leading-zero"
     | "too-short"
     | "too-long"
     | "mobile-prefix"
     | "invalid";

export interface PhoneInputProps
     extends Omit<
          React.InputHTMLAttributes<HTMLInputElement>,
          "value" | "onChange" | "type" | "inputMode" | "maxLength"
     > {
     value?: string;
     defaultValue?: string;
     onChange?: (rawValue: string, formattedValue: string) => void;
     onValidityChange?: (isValid: boolean, reason?: LandlineValidationReason) => void;
     error?: boolean;
     errorMessage?: React.ReactNode;
     validateOnBlur?: boolean;
     /** موقع blur اگر 0 ابتدایی جا افتاده بود، خودکار اضافه می‌شود — پیش‌فرض: true */
     autoPrefixZero?: boolean;
     /** پیام خطای سفارشی برای هر reason */
     errorMessages?: Partial<Record<LandlineValidationReason, string>>;
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

const PERSIAN_ARABIC_DIGITS = /[۰-۹٠-٩]/g;
const PERSIAN_DIGIT_MAP: Record<string, string> = {
     "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
     "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
     "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
     "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
};

export const toEnglishDigits = (input: string): string =>
     input.replace(PERSIAN_ARABIC_DIGITS, (d) => PERSIAN_DIGIT_MAP[d] ?? d);

/** فقط اعداد، حداکثر ۱۱ رقم */
const sanitize = (value: string): string =>
     toEnglishDigits(value).replace(/\D/g, "").slice(0, 11);

/** فرمت: 0XX XXXX XXXX */
export const formatPhone = (value: string): string => {
     const digits = sanitize(value);
     if (!digits) return "";
     if (digits.length <= 3) return digits;
     if (digits.length <= 7) return `${digits.slice(0, 3)} ${digits.slice(3)}`;
     return `${digits.slice(0, 3)} ${digits.slice(3, 7)} ${digits.slice(7, 11)}`;
};

/* -------------------------------------------------------------------------- */
/*                                Validation                                  */
/* -------------------------------------------------------------------------- */

/**
 * ✅ اعتبارسنجی دقیق تلفن ثابت ایران
 * - حتماً با 0 شروع شود
 * - دقیقاً ۱۱ رقم
 * - رقم دوم نباید 0 باشد (پیشوند 00 نامعتبر)
 * - رقم دوم نباید 9 باشد (پیشوند 09 موبایل است، نه ثابت)
 */
export const validateIranLandline = (
     value: string
): { valid: boolean; reason?: LandlineValidationReason } => {
     const digits = sanitize(value);

     if (digits.length === 0) return { valid: false, reason: "empty" };

     if (!digits.startsWith("0"))
          return { valid: false, reason: "missing-leading-zero" };

     if (digits.length < 11) return { valid: false, reason: "too-short" };
     if (digits.length > 11) return { valid: false, reason: "too-long" };

     // رقم دوم 9 → موبایل، رقم دوم 0 → نامعتبر
     if (digits[1] === "9")
          return { valid: false, reason: "mobile-prefix" };
     if (digits[1] === "0")
          return { valid: false, reason: "invalid" };

     // رقم دوم بین 1 تا 8 → کد استان معتبر
     if (!/^0[1-8]\d{9}$/.test(digits))
          return { valid: false, reason: "invalid" };

     return { valid: true };
};

export const isValidIranLandline = (value: string): boolean =>
     validateIranLandline(value).valid;

/* -------------------------------------------------------------------------- */
/*                            Cursor helpers                                  */
/* -------------------------------------------------------------------------- */

const countDigitsBefore = (value: string, cursor: number): number =>
     (toEnglishDigits(value.slice(0, cursor)).match(/\d/g) || []).length;

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

/* -------------------------------------------------------------------------- */
/*                            Default error messages                          */
/* -------------------------------------------------------------------------- */

const DEFAULT_ERROR_MESSAGES: Record<LandlineValidationReason, string> = {
     "empty": "شماره تلفن الزامی است",
     "missing-leading-zero": "شماره تلفن باید با 0 شروع شود (مثال: 02112345678)",
     "too-short": "شماره تلفن باید ۱۱ رقم باشد",
     "too-long": "شماره تلفن نباید بیشتر از ۱۱ رقم باشد",
     "mobile-prefix": "این شماره مربوط به موبایل است، لطفاً شماره تلفن ثابت وارد کنید",
     "invalid": "شماره تلفن ثابت معتبر نیست",
};

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const PhoneInput = forwardRef<
     PhoneInputRef,
     PhoneInputProps
>(
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
               autoPrefixZero = true,
               errorMessages,
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

          const rawValue = isControlled ? sanitize(value!) : internalRaw;
          const formattedValue = formatPhone(rawValue);

          const validation = validateIranLandline(rawValue);
          const valid = validation.valid;

          const resolvedErrorMessage = useMemo(
               () =>
                    errorMessage ??
                    (validation.reason
                         ? (errorMessages?.[validation.reason] ??
                              DEFAULT_ERROR_MESSAGES[validation.reason])
                         : undefined),
               [errorMessage, errorMessages, validation.reason]
          );

          const showError =
               (!!error || (touched && !valid && rawValue.length > 0)) &&
               !!resolvedErrorMessage;

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
                         onValidityChange?.(false, "empty");
                    },
                    isValid: () => valid,
                    getRawValue: () => rawValue,
               }),
               [isControlled, onChange, onValidityChange, valid, rawValue]
          );

          /* --------------------- Validity sync (هر تغییر) ---------------------- */
          useEffect(() => {
               onValidityChange?.(validation.valid, validation.reason);
               // eslint-disable-next-line react-hooks/exhaustive-deps
          }, [validation.valid, validation.reason]);

          /* ------------------------------- Handlers ----------------------------- */
          const handleChange = useCallback(
               (e: React.ChangeEvent<HTMLInputElement>) => {
                    const input = e.target;
                    const selectionStart =
                         input.selectionStart ?? input.value.length;
                    const digitsBeforeCursor = countDigitsBefore(
                         input.value,
                         selectionStart
                    );

                    const nextRaw = sanitize(input.value);

                    if (!isControlled) setInternalRaw(nextRaw);
                    const nextFormatted = formatPhone(nextRaw);
                    onChange?.(nextRaw, nextFormatted);

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

                    // 🎯 اگر 0 ابتدایی جا افتاده بود، خودکار اضافه کن
                    let finalRaw = rawValue;
                    if (
                         autoPrefixZero &&
                         finalRaw.length > 0 &&
                         !finalRaw.startsWith("0")
                    ) {
                         finalRaw = ("0" + finalRaw).slice(0, 11);
                         if (!isControlled) setInternalRaw(finalRaw);
                         onChange?.(finalRaw, formatPhone(finalRaw));
                    }

                    if (validateOnBlur) {
                         const nextValidation = validateIranLandline(finalRaw);
                         onValidityChange?.(nextValidation.valid, nextValidation.reason);
                    }
                    onBlur?.(e);
               },
               [
                    rawValue,
                    autoPrefixZero,
                    isControlled,
                    onChange,
                    onValidityChange,
                    validateOnBlur,
                    onBlur,
               ]
          );

          const handleKeyDown = useCallback(
               (e: React.KeyboardEvent<HTMLInputElement>) => {
                    const allowedKeys = [
                         "Backspace", "Delete", "ArrowLeft", "ArrowRight",
                         "ArrowUp", "ArrowDown", "Home", "End", "Tab",
                         "Enter", "Escape",
                    ];
                    if (allowedKeys.includes(e.key)) return;
                    if (e.ctrlKey || e.metaKey) return;
                    if (/^[0-9۰-۹٠-٩]$/.test(e.key)) return;
                    e.preventDefault();
               },
               []
          );

          /* ------------------------------- Render ------------------------------- */
          return (
               <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    <input
                         {...rest}
                         ref={inputRef}
                         type="tel"
                         inputMode="numeric"
                         autoComplete="tel-national"
                         placeholder="021 1234 5678"
                         value={formattedValue}
                         onChange={handleChange}
                         onKeyDown={handleKeyDown}
                         onBlur={handleBlur}
                         onFocus={onFocus}
                         disabled={disabled}
                         maxLength={13}
                         dir={dir}
                         aria-invalid={showError}
                         aria-describedby={
                              showError ? "landline-input-error" : undefined
                         }
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
                              id="landline-input-error"
                              role="alert"
                              style={{ color: "#dc2626", fontSize: 12 }}
                         >
                              {resolvedErrorMessage}
                         </span>
                    )}
               </div>
          );
     }
);

PhoneInput.displayName = "PhoneInput";
export default PhoneInput;

/*


مثال‌های استفاده
۱. ساده (controlled):

tsx
const [phone, setPhone] = useState<string>("");

<PhoneInput
     value={phone}
     onChange={(raw) => setPhone(raw)}
     placeholder="021 1234 5678"
/>




۲. با اعتبارسنجی و نمایش خطا:

tsx
const [phone, setPhone] = useState("");
const [valid, setValid] = useState(false);

<PhoneInput
     value={phone}
     onChange={(raw) => setPhone(raw)}
     onValidityChange={setValid}
     errorMessage="شماره تلفن ثابت معتبر نیست (مثال: 021 1234 5678)"
/>

<button disabled={!valid}>ادامه</button>





۳. با react-hook-form:

tsx
<Controller
     name="landline"
     control={control}
     rules={{
          required: "شماره تلفن الزامی است",
          validate: (v) =>
               isValidIranLandline(v || "") ||
               "شماره تلفن ثابت معتبر نیست",
     }}
     render={({ field, fieldState }) => (
          <PhoneInput
               value={field.value}
               onChange={(raw) => field.onChange(raw)}
               onBlur={field.onBlur}
               error={!!fieldState.error}
               errorMessage={fieldState.error?.message}
          />
     )}
/>






۴. با ref:

tsx
const landlineRef = useRef<PhoneInputRef>(null);

<PhoneInput ref={landlineRef} />

<button onClick={() => landlineRef.current?.clear()}>پاک کردن</button>
<button onClick={() => console.log(landlineRef.current?.getRawValue())}>
     دریافت مقدار خام
</button>
<button onClick={() => console.log(landlineRef.current?.isValid())}>
     معتبر است؟
</button>







۵. uncontrolled با مقدار اولیه:

tsx
<PhoneInput
     defaultValue="02112345678"
     onChange={(raw, formatted) => {
          console.log("raw:", raw);          // "02112345678"
          console.log("formatted:", formatted); // "021 1234 5678"
     }}




*/