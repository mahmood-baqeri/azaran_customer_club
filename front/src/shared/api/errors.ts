// src/shared/api/errors.ts

export class ApiError extends Error {
  status: number;
  payload: unknown;
  errorCode?: string;

  constructor(
    message: string,
    status: number,
    payload?: unknown,
    errorCode?: string
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
    this.errorCode = errorCode;
  }
}

/**
 * پیام خطای مناسب برای نمایش به کاربر را استخراج می‌کند.
 * - اگر ApiError بود → message آن
 * - اگر Error معمولی بود → message آن
 * - اگر رشته بود → خودش
 * - در غیر این صورت → fallback
 */
export function getErrorMessage(
  err: unknown,
  fallback = "خطای نامشخص، لطفاً دوباره تلاش کنید"
): string {
  if (err instanceof ApiError) {
    return err.message?.trim() || fallback;
  }
  if (err instanceof Error) {
    return err.message?.trim() || fallback;
  }
  if (typeof err === "string" && err.trim()) {
    return err.trim();
  }
  if (err && typeof err === "object" && "message" in err) {
    const m = (err as { message?: unknown }).message;
    if (typeof m === "string" && m.trim()) return m.trim();
  }
  return fallback;
}