/* eslint-disable react-refresh/only-export-components */
import React, {
     forwardRef,
     useCallback,
     useImperativeHandle,
     useMemo,
     useRef,
     useState,
} from "react";

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

export interface CurrencyInputProps
     extends Omit<
          React.InputHTMLAttributes<HTMLInputElement>,
          | "type"
          | "inputMode"
          | "value"
          | "defaultValue"
          | "onChange"
          | "min"
          | "max"
          | "step"
     > {
     /** مقدار (controlled) — می‌تواند number، رشته‌ی ارقام خالص یا null باشد */
     value?: number | string | null;
     /** مقدار اولیه (uncontrolled) */
     defaultValue?: number | string | null;

     /** حداقل مقدار مجاز */
     min?: number;
     /** حداکثر مقدار مجاز */
     max?: number;

     /** برچسب واحد پول — پیش‌فرض: "ریال" */
     currencyLabel?: React.ReactNode;
     /** پنهان کردن واحد پول */
     hideCurrency?: boolean;
     /** فاصله‌ی متن از واحد (px) — پیش‌فرض 56 */
     currencyGutter?: number;

     /** callback با مقدار عددی (یا null اگر خالی) + رشته‌ی ارقام خالص */
     onChange?: (value: number | null, digits: string) => void;
     /** callback موقع blur */
     onValueCommit?: (value: number | null) => void;
     /** callback اعتبار */
     onValidityChange?: (isValid: boolean, reason?: string) => void;

     /** حالت خطا */
     error?: boolean;
     /** پیام خطا */
     errorMessage?: string;

     /** تراز متن (پیش‌فرض "left") */
     textAlign?: "left" | "right" | "center" | "start" | "end";

     /** کلاس کانتینر بیرونی */
     containerClassName?: string;
}

export interface CurrencyInputRef {
     focus: () => void;
     blur: () => void;
     clear: () => void;
     getValue: () => number | null;
     setValue: (value: number | string | null) => void;
     isValid: () => boolean;
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

/** تبدیل ارقام فارسی/عربی به لاتین */
export const toEnglishDigits = (input: string): string =>
     input.replace(PERSIAN_ARABIC_DIGITS, (d) => PERSIAN_DIGIT_MAP[d] ?? d);

/** فقط ارقام — بدون جداکننده، بدون صفر ابتدایی اضافه */
const toDigits = (raw: string): string => {
     const en = toEnglishDigits(raw).replace(/[^\d]/g, "");
     return en.replace(/^0+(?=\d)/, "");
};

/** درج جداکننده‌ی هزارگان */
const formatThousands = (digits: string): string =>
     digits ? digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : "";

/** تعداد ارقام در یک رشته */
const countDigits = (s: string): number => s.replace(/\D/g, "").length;

/** ایندکس بعد از n-امین رقم */
const positionAfterNthDigit = (s: string, n: number): number => {
     if (n <= 0) return 0;
     let count = 0;
     for (let i = 0; i < s.length; i++) {
          if (/\d/.test(s[i])) {
               count++;
               if (count === n) return i + 1;
          }
     }
     return s.length;
};

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const CurrencyInput = forwardRef<CurrencyInputRef, CurrencyInputProps>(
     (
          {
               value,
               defaultValue = "",
               min,
               max,
               currencyLabel = "ریال",
               hideCurrency = false,
               currencyGutter,
               onChange,
               onValueCommit,
               onValidityChange,
               onBlur,
               onFocus,
               error,
               errorMessage,
               textAlign = "left",
               containerClassName,
               className,
               style,
               disabled,
               placeholder = "0",
               ...rest
          },
          ref
     ) => {
          const inputRef = useRef<HTMLInputElement>(null);
          const isControlled = value !== undefined;

          const toDigitsFromValue = (v: number | string | null | undefined): string => {
               if (v === null || v === undefined || v === "") return "";
               return toDigits(String(v));
          };

          const [internalDigits, setInternalDigits] = useState<string>(() =>
               toDigitsFromValue(defaultValue)
          );
          const [touched, setTouched] = useState(false);

          const digits = isControlled ? toDigitsFromValue(value) : internalDigits;
          const formatted = formatThousands(digits);
          const numericValue = digits === "" ? null : Number(digits);

          /* ---------------------------- validation ---------------------------- */
          const validation = useMemo(() => {
               if (digits === "") return { valid: true as const };
               const num = Number(digits);
               if (Number.isNaN(num)) return { valid: false as const, reason: "not-a-number" };
               if (min !== undefined && num < min) return { valid: false as const, reason: "min" };
               if (max !== undefined && num > max) return { valid: false as const, reason: "max" };
               return { valid: true as const };
          }, [digits, min, max]);

          const showError = (!!error || (touched && !validation.valid)) && !!errorMessage;

          /* -------------------------- validity sync --------------------------- */
          React.useEffect(() => {
               onValidityChange?.(validation.valid, validation.reason);
               // eslint-disable-next-line react-hooks/exhaustive-deps
          }, [validation.valid, validation.reason]);

          /* ------------------------------ commit ------------------------------ */
          const commit = useCallback(
               (nextDigits: string) => {
                    if (!isControlled) setInternalDigits(nextDigits);
                    const num = nextDigits === "" ? null : Number(nextDigits);
                    onChange?.(num, nextDigits);
               },
               [isControlled, onChange]
          );

          /* ------------------------- cursor restoration ----------------------- */
          const restoreCursor = useCallback((digitsBeforeCursor: number) => {
               requestAnimationFrame(() => {
                    const input = inputRef.current;
                    if (!input) return;
                    const pos = positionAfterNthDigit(input.value, digitsBeforeCursor);
                    input.setSelectionRange(pos, pos);
               });
          }, []);

          /* ----------------------------- handlers ----------------------------- */
          const handleChange = useCallback(
               (e: React.ChangeEvent<HTMLInputElement>) => {
                    const el = e.target;
                    const cursorPos = el.selectionStart ?? el.value.length;
                    const beforeCursor = el.value.slice(0, cursorPos);

                    const rawDigitsBefore = countDigits(toEnglishDigits(beforeCursor));
                    const cleaned = toDigits(el.value);
                    const rawAll = toEnglishDigits(el.value).replace(/[^\d]/g, "");
                    const stripped = rawAll.length - cleaned.length;
                    const adjustedBefore = Math.max(0, rawDigitsBefore - stripped);

                    commit(cleaned);
                    restoreCursor(adjustedBefore);
               },
               [commit, restoreCursor]
          );

          const handleBlur = useCallback(
               (e: React.FocusEvent<HTMLInputElement>) => {
                    setTouched(true);
                    let finalValue = numericValue;
                    if (finalValue !== null) {
                         let clamped = finalValue;
                         if (min !== undefined && clamped < min) clamped = min;
                         if (max !== undefined && clamped > max) clamped = max;
                         if (clamped !== finalValue) {
                              commit(String(clamped));
                              finalValue = clamped;
                         }
                    }
                    onValueCommit?.(finalValue);
                    onBlur?.(e);
               },
               [numericValue, min, max, commit, onValueCommit, onBlur]
          );

          const handleKeyDown = useCallback(
               (e: React.KeyboardEvent<HTMLInputElement>) => {
                    const el = e.currentTarget;

                    // ✅ اگر cursor بلافاصله بعد از "," بود، رقم قبل از جداکننده را حذف کن
                    if (e.key === "Backspace") {
                         const start = el.selectionStart ?? 0;
                         const end = el.selectionEnd ?? 0;
                         if (start === end && start > 0 && el.value[start - 1] === ",") {
                              e.preventDefault();
                              const newValue =
                                   el.value.slice(0, start - 2) + el.value.slice(start);
                              const digitsBefore = countDigits(el.value.slice(0, start - 2));
                              commit(toDigits(newValue));
                              restoreCursor(digitsBefore);
                              return;
                         }
                    }

                    const allowed = [
                         "Backspace", "Delete", "ArrowLeft", "ArrowRight",
                         "Home", "End", "Tab", "Enter", "Escape",
                    ];
                    if (allowed.includes(e.key)) return;
                    if (e.ctrlKey || e.metaKey) return;
                    if (/^[0-9۰-۹٠-٩]$/.test(e.key)) return; // اعداد لاتین و فارسی/عربی
                    e.preventDefault();
               },
               [commit, restoreCursor]
          );

          /* --------------------------- imperative API -------------------------- */
          useImperativeHandle(
               ref,
               () => ({
                    focus: () => inputRef.current?.focus(),
                    blur: () => inputRef.current?.blur(),
                    clear: () => {
                         setTouched(false);
                         commit("");
                         onValueCommit?.(null);
                    },
                    getValue: () => numericValue,
                    setValue: (v) => commit(toDigitsFromValue(v)),
                    isValid: () => validation.valid,
               }),
               [commit, numericValue, validation.valid, onValueCommit]
          );

          /* ------------------------------- render ------------------------------ */
          const gutter = currencyGutter ?? (hideCurrency ? 14 : 56);

          return (
               <div
                    style={{ display: "flex", flexDirection: "column", gap: 6 }}
                    className={containerClassName}
               >
                    <div style={{ position: "relative", display: "block" }}>
                         <input
                              {...rest}
                              ref={inputRef}
                              type="text"
                              inputMode="numeric"
                              autoComplete="off"
                              value={formatted}
                              onChange={handleChange}
                              onKeyDown={handleKeyDown}
                              onBlur={handleBlur}
                              onFocus={onFocus}
                              disabled={disabled}
                              dir="ltr"
                              placeholder={placeholder}
                              aria-invalid={showError}
                              aria-describedby={showError ? "currency-input-error" : undefined}
                              className={className}
                              style={{
                                   textAlign,
                                   paddingLeft: gutter,
                                   borderColor: showError ? "#dc2626" : undefined,
                                   ...style,
                              }}
                         />
                         {!hideCurrency && (
                              <span
                                   aria-hidden="true"
                                   style={{
                                        position: "absolute",
                                        left: 12,
                                        top: "50%",
                                        transform: "translateY(-50%)",
                                        color: "#a0aec0",
                                        fontSize: 12,
                                        pointerEvents: "none",
                                        userSelect: "none",
                                   }}
                              >
                                   {currencyLabel}
                              </span>
                         )}
                    </div>

                    {showError && (
                         <span
                              id="currency-input-error"
                              role="alert"
                              style={{ color: "#dc2626", fontSize: 12 }}
                         >
                              {errorMessage}
                         </span>
                    )}
               </div>
          );
     }
);

CurrencyInput.displayName = "CurrencyInput";
export default CurrencyInput;





/*


با:

tsx
const [amount, setAmount] = useState<string>("");

<CurrencyInput
     value={amount}
     onChange={(_, digits) => setAmount(digits)}
     className="proj-input"
     placeholder="0"
     currencyLabel="ریال"
/>
چند مثال کاربردی
۱. ساده — فقط مبلغ:

tsx
const [amount, setAmount] = useState<number | null>(null);

<CurrencyInput
     value={amount}
     onChange={(v) => setAmount(v)}
     min={0}
     errorMessage="مبلغ معتبر وارد کنید"
/>






۲. تومان با گاتر بلندتر:

tsx
<CurrencyInput
     value={price}
     onChange={(v) => setPrice(v)}
     currencyLabel="تومان"
     currencyGutter={68}
     style={{ height: 44 }}
/>





۳. با react-hook-form:

tsx
<Controller
     name="amount"
     control={control}
     rules={{ required: "مبلغ الزامی است", min: { value: 1000, message: "حداقل ۱٬۰۰۰ ریال" } }}
     render={({ field, fieldState }) => (
          <CurrencyInput
               value={field.value}
               onChange={(v) => field.onChange(v)}
               onValueCommit={(v) => field.onChange(v)}
               min={1000}
               error={!!fieldState.error}
               errorMessage={fieldState.error?.message}
          />
     )}
/>






۴. با ref:

tsx
const amountRef = useRef<CurrencyInputRef>(null);

<CurrencyInput ref={amountRef} />

<button onClick={() => amountRef.current?.setValue(5000000)}>۵ میلیون</button>
<button onClick={() => console.log(amountRef.current?.getValue())}>دریافت</button>


*/