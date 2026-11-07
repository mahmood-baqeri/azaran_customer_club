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

export interface NumberInputProps
     extends Omit<
          React.InputHTMLAttributes<HTMLInputElement>,
          | "type"
          | "inputMode"
          | "value"
          | "defaultValue"   // 👈 این خط اضافه شد
          | "onChange"
          | "min"
          | "max"
          | "step"
     > {
     /** مقدار (controlled) — می‌تواند number، string خالی یا undefined باشد */
     value?: number | string | null;
     /** مقدار اولیه (uncontrolled) */
     defaultValue?: number | string | null;

     /** حداقل مقدار مجاز */
     min?: number;
     /** حداکثر مقدار مجاز */
     max?: number;
     /** گام افزایش/کاهش (پیش‌فرض: 1) */
     step?: number;

     /** فقط اعداد مثبت (پیش‌فرض: true) */
     onlyPositive?: boolean;
     /** اجازه‌ی ورود اعشار (پیش‌فرض: false) */
     allowDecimal?: boolean;
     /** حداکثر تعداد ارقام اعشار (پیش‌فرض: 2) */
     decimalScale?: number;

     /** callback با مقدار عددی (یا null اگر خالی) */
     onChange?: (value: number | null, rawValue: string) => void;
     /** callback موقع blur — اگر مقدار خالی یا نامعتبر بود null می‌گیرید */
     onValueCommit?: (value: number | null) => void;
     /** callback وضعیت اعتبار */
     onValidityChange?: (isValid: boolean, reason?: string) => void;

     /** حالت خطا */
     error?: boolean;
     /** پیام خطا */
     errorMessage?: string;

     /** نمایش دکمه‌های +/- */
     showStepper?: boolean;

     /** 👇 جدید: تراز متن داخل input (پیش‌فرض: "center") */
     textAlign?: "left" | "right" | "center" | "start" | "end";
}

export interface NumberInputRef {
     focus: () => void;
     blur: () => void;
     clear: () => void;
     stepUp: () => void;
     stepDown: () => void;
     getValue: () => number | null;
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

/**
 * پاکسازی ورودی: فقط اعداد (و در صورت اجازه، یک نقطه اعشار) را نگه می‌دارد.
 */
const sanitizeNumeric = (
     input: string,
     allowDecimal: boolean,
     onlyPositive: boolean
): string => {
     let v = toEnglishDigits(input).replace(/,/g, "");

     if (onlyPositive) v = v.replace(/[^\d.]/g, "");
     else v = v.replace(/[^\d.-]/g, "");

     if (allowDecimal) {
          // فقط یک نقطه مجاز است
          const parts = v.split(".");
          if (parts.length > 2) v = `${parts[0]}.${parts.slice(1).join("")}`;
     } else {
          v = v.replace(/\./g, "");
     }

     // منفی فقط در ابتدا و در حالت غیر onlyPositive
     if (!onlyPositive) {
          v = v.replace(/(?!^)-/g, "");
     } else {
          v = v.replace(/-/g, "");
     }

     return v;
};

/**
 * اعتبارسنجی مقدار بر اساس min/max/decimalScale
 */
const validateValue = (
     raw: string,
     {
          min,
          max,
          allowDecimal,
          decimalScale,
          onlyPositive,
     }: {
          min?: number;
          max?: number;
          allowDecimal: boolean;
          decimalScale: number;
          onlyPositive: boolean;
     }
): { valid: boolean; reason?: string } => {
     if (raw === "" || raw === "-" || raw === "." || raw === "-.") {
          return { valid: true }; // خالی معتبر است، اجباری بودن باید بیرون بررسی شود
     }

     const num = Number(raw);

     if (Number.isNaN(num)) return { valid: false, reason: "not-a-number" };
     if (!allowDecimal && !Number.isInteger(num))
          return { valid: false, reason: "integer-required" };
     if (onlyPositive && num < 0) return { valid: false, reason: "positive-only" };
     if (min !== undefined && num < min) return { valid: false, reason: "min" };
     if (max !== undefined && num > max) return { valid: false, reason: "max" };

     if (allowDecimal && decimalScale >= 0) {
          const decPart = raw.split(".")[1];
          if (decPart && decPart.length > decimalScale)
               return { valid: false, reason: "decimal-scale" };
     }

     return { valid: true };
};

const clamp = (n: number, min?: number, max?: number): number => {
     if (min !== undefined && n < min) return min;
     if (max !== undefined && n > max) return max;
     return n;
};

/** محدود کردن تعداد ارقام اعشار به decimalScale */
const applyDecimalScale = (raw: string, scale: number): string => {
     if (!raw.includes(".")) return raw;
     const [int, dec = ""] = raw.split(".");
     return `${int}.${dec.slice(0, scale)}`;
};

/* -------------------------------------------------------------------------- */
/*                                 Component                                  */
/* -------------------------------------------------------------------------- */

export const NumberInput = forwardRef<NumberInputRef, NumberInputProps>(
     (
          {
               value,
               defaultValue = "",
               min,
               max,
               step = 1,
               onlyPositive = true,
               allowDecimal = false,
               decimalScale = 2,
               onChange,
               onValueCommit,
               onValidityChange,
               onBlur,
               onFocus,
               error,
               errorMessage,
               showStepper = false,
               disabled,
               className,
               style,
               dir = "ltr",
               textAlign = "center",
               ...rest
          },
          ref
     ) => {
          const inputRef = useRef<HTMLInputElement>(null);
          const isControlled = value !== undefined;

          const toRaw = (v: number | string | null | undefined): string => {
               if (v === null || v === undefined || v === "") return "";
               return String(v);
          };

          const [internalRaw, setInternalRaw] = useState<string>(() =>
               toRaw(defaultValue)
          );
          const [touched, setTouched] = useState(false);

          const rawValue = isControlled ? toRaw(value) : internalRaw;

          const validation = useMemo(
               () =>
                    validateValue(rawValue, {
                         min,
                         max,
                         allowDecimal,
                         decimalScale,
                         onlyPositive,
                    }),
               [rawValue, min, max, allowDecimal, decimalScale, onlyPositive]
          );

          const numericValue =
               rawValue === "" || rawValue === "-" || rawValue === "."
                    ? null
                    : Number(rawValue);

          const showError =
               (!!error || (touched && !validation.valid)) && !!errorMessage;

          /* --------------------------- Validity sync ---------------------------- */
          useEffect(() => {
               onValidityChange?.(validation.valid, validation.reason);
               // eslint-disable-next-line react-hooks/exhaustive-deps
          }, [validation.valid, validation.reason]);

          /* ----------------------------- Handlers ------------------------------- */
          const commit = useCallback(
               (raw: string) => {
                    if (!isControlled) setInternalRaw(raw);
                    const num =
                         raw === "" || raw === "-" || raw === "." ? null : Number(raw);
                    onChange?.(num, raw);
               },
               [isControlled, onChange]
          );

          const handleChange = useCallback(
               (e: React.ChangeEvent<HTMLInputElement>) => {
                    const el = e.target;
                    const selectionStart = el.selectionStart ?? el.value.length;
                    const digitsBeforeCursor = (
                         el.value.slice(0, selectionStart).match(/[\d.-]/g) || []
                    ).length;

                    let next = sanitizeNumeric(el.value, allowDecimal, onlyPositive);
                    if (allowDecimal) next = applyDecimalScale(next, decimalScale);

                    commit(next);

                    requestAnimationFrame(() => {
                         const input = inputRef.current;
                         if (!input) return;
                         let seen = 0;
                         let pos = 0;
                         for (let i = 0; i < next.length; i++) {
                              if (/[\d.-]/.test(next[i])) {
                                   seen++;
                                   if (seen === digitsBeforeCursor) {
                                        pos = i + 1;
                                        break;
                                   }
                              }
                         }
                         if (pos === 0) pos = Math.min(digitsBeforeCursor, next.length);
                         input.setSelectionRange(pos, pos);
                    });
               },
               [allowDecimal, decimalScale, onlyPositive, commit]
          );

          const handleBlur = useCallback(
               (e: React.FocusEvent<HTMLInputElement>) => {
                    setTouched(true);

                    // اگر مقدار عددی معتبر بود، clamp کن روی min/max
                    if (numericValue !== null && !Number.isNaN(numericValue)) {
                         const clamped = clamp(numericValue, min, max);
                         if (clamped !== numericValue) {
                              const raw = allowDecimal
                                   ? applyDecimalScale(String(clamped), decimalScale)
                                   : String(clamped);
                              commit(raw);
                         }
                         onValueCommit?.(clamped);
                    } else {
                         onValueCommit?.(null);
                    }

                    onBlur?.(e);
               },
               [
                    numericValue,
                    min,
                    max,
                    allowDecimal,
                    decimalScale,
                    commit,
                    onValueCommit,
                    onBlur,
               ]
          );

          const handleKeyDown = useCallback(
               (e: React.KeyboardEvent<HTMLInputElement>) => {
                    const allowedKeys = [
                         "Backspace", "Delete", "ArrowLeft", "ArrowRight", "ArrowUp",
                         "ArrowDown", "Home", "End", "Tab", "Enter", "Escape",
                    ];
                    if (allowedKeys.includes(e.key)) return;
                    if (e.ctrlKey || e.metaKey) return;

                    if (/^\d$/.test(e.key)) return;
                    if (allowDecimal && e.key === ".") {
                         if (e.currentTarget.value.includes(".")) e.preventDefault();
                         return;
                    }
                    if (!onlyPositive && e.key === "-" && !e.currentTarget.value) return;

                    e.preventDefault();
               },
               [allowDecimal, onlyPositive]
          );

          /* ------------------------- Imperative API ----------------------------- */
          const doStep = useCallback(
               (dir: 1 | -1) => {
                    const base = numericValue ?? 0;
                    const next = clamp(base + dir * step, min, max);
                    const raw = allowDecimal
                         ? applyDecimalScale(String(next), decimalScale)
                         : String(next);
                    commit(raw);
                    onValueCommit?.(next);
               },
               [numericValue, step, min, max, allowDecimal, decimalScale, commit, onValueCommit]
          );

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
                    stepUp: () => doStep(1),
                    stepDown: () => doStep(-1),
                    getValue: () => numericValue,
                    isValid: () => validation.valid,
               }),
               [commit, doStep, numericValue, validation.valid, onValueCommit]
          );

          /* ------------------------------- Render ------------------------------- */
          const input = (
               <input
                    {...rest}
                    ref={inputRef}
                    type="text"
                    inputMode={allowDecimal ? "decimal" : "numeric"}
                    autoComplete="off"
                    value={rawValue}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    onBlur={handleBlur}
                    onFocus={onFocus}
                    disabled={disabled}
                    dir={dir}
                    aria-invalid={showError}
                    aria-valuemin={min}
                    aria-valuemax={max}
                    aria-valuenow={numericValue ?? undefined}
                    aria-describedby={showError ? "number-input-error" : undefined}
                    className={className}
                    style={{
                         textAlign,                              // 👈 از پراپ
                         borderColor: showError ? "#dc2626" : undefined,
                         ...style,                               // 👈 style کاربر بالاترین اولویت را دارد
                    }}
               />
          );

          const stepper = (direction: "up" | "down") => (
               <button
                    type="button"
                    tabIndex={-1}
                    disabled={
                         disabled ||
                         (direction === "up" && max !== undefined && (numericValue ?? -Infinity) >= max) ||
                         (direction === "down" && min !== undefined && (numericValue ?? Infinity) <= min)
                    }
                    onClick={() => doStep(direction === "up" ? 1 : -1)}
                    style={{
                         width: 28,
                         height: 20,
                         fontSize: 12,
                         lineHeight: "18px",
                         border: "1px solid #d1d5db",
                         background: "#fff",
                         cursor: "pointer",
                    }}
                    aria-label={direction === "up" ? "افزایش" : "کاهش"}
               >
                    {direction === "up" ? "▲" : "▼"}
               </button>
          );

          return (
               <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    <div style={{ position: "relative", display: "inline-flex" }}>
                         {input}
                         {showStepper && (
                              <div
                                   style={{
                                        position: "absolute",
                                        left: dir === "ltr" ? 6 : "auto",
                                        right: dir === "rtl" ? 6 : "auto",
                                        top: "50%",
                                        transform: "translateY(-50%)",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 2,
                                   }}
                              >
                                   {stepper("up")}
                                   {stepper("down")}
                              </div>
                         )}
                    </div>

                    {showError && (
                         <span
                              id="number-input-error"
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

NumberInput.displayName = "NumberInput";

export default NumberInput;





/*

مقادیر صحیح و اعشاری
حداقل / حداکثر
فقط اعداد مثبت
محدودیت تعداد ارقام اعشار
جلوگیری از کاراکترهای غیرمجاز
کنترل cursor
کاملاً controlled / uncontrolled
پشتیبانی از فارسی و عربی اعداد
a11y کامل


1. ساده — فقط اعداد مثبت صحیح
tsx
const [count, setCount] = useState<number | null>(null);

<NumberInput
  value={count}
  onChange={(v) => setCount(v)}
  placeholder="تعداد"
  errorMessage="لطفاً یک عدد معتبر وارد کنید"
  style={{ marginBottom: 16 }}
/>



2. با حداقل و حداکثر
tsx
<NumberInput
  value={count}
  onChange={setCount}
  min={1}
  max={99}
  errorMessage="مقدار باید بین ۱ و ۹۹ باشد"
  style={{ marginBottom: 16 }}
/>



3. اعشاری (مثلاً قیمت یا وزن)
tsx
<NumberInput
  value={weight}
  onChange={setWeight}
  allowDecimal
  decimalScale={2}
  min={0}
  max={1000}
  placeholder="وزن (kg)"
  errorMessage="وزن باید بین ۰ تا ۱۰۰۰ با حداکثر ۲ رقم اعشار باشد"
/>



4. با Stepper (دکمه‌های +/-)
tsx
<NumberInput
  value={quantity}
  onChange={setQuantity}
  min={0}
  max={10}
  step={1}
  showStepper
/>



5. اجازه‌ی اعداد منفی (مثلاً دمای هوا)
tsx
<NumberInput
  value={temp}
  onChange={setTemp}
  onlyPositive={false}
  allowDecimal
  decimalScale={1}
  min={-50}
  max={50}
/>



6. استفاده با ref
tsx
const numRef = useRef<NumberInputRef>(null);

<NumberInput ref={numRef} />

<button onClick={() => numRef.current?.stepUp()}>+</button>
<button onClick={() => numRef.current?.stepDown()}>-</button>
<button onClick={() => numRef.current?.clear()}>پاک کردن</button>
<button onClick={() => console.log(numRef.current?.getValue())}>دریافت</button>



7. با react-hook-form
tsx
<Controller
  name="quantity"
  control={control}
  rules={{
    required: "تعداد الزامی است",
    validate: (v) =>
      (v === null || v >= 1) || "حداقل تعداد ۱ است",
  }}
  render={({ field, fieldState }) => (
    <NumberInput
      value={field.value}
      onChange={(v) => field.onChange(v)}
      onValueCommit={(v) => field.onChange(v)}
      min={1}
      max={99}
      error={!!fieldState.error}
      errorMessage={fieldState.error?.message}
    />
  )}
/>

*/