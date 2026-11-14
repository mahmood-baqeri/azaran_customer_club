// src/shared/api/http.ts

import axios from "axios";
import { BASE_URL, RunInServer } from "../constants/env";
import { Token } from "../constants/storage-keys";
import { redirectTo } from "../auth/navigation";
import { isTokenExpired } from "../auth/token";
import {
     clearLocalStorage,
     getCookie,
     getLocalStorage,
     setLocalStorage,
} from "../storage/local-storage";
import { ApiError } from "./errors";

// ==================================================================
// تنظیمات
// ==================================================================

const REQUEST_TIMEOUT_MS = 30_000;
const LOGIN_PATH = "/login";
const REDIRECT_LOCK_MS = 1_000;

// ==================================================================
// helpers
// ==================================================================

let isRedirecting = false;

function safeRedirect(path: string): void {
     if (isRedirecting) return;
     if (typeof window !== "undefined" && window.location.pathname === path) {
          return; // همین الان روی صفحه لاگین هستیم
     }
     isRedirecting = true;
     try {
          redirectTo(path);
     } finally {
          window.setTimeout(() => {
               isRedirecting = false;
          }, REDIRECT_LOCK_MS);
     }
}

function extractMessage(data: unknown, fallback: string): string {
     if (!data || typeof data !== "object") return fallback;
     const d = data as Record<string, unknown>;

     const tryStr = (v: unknown): string | null =>
          typeof v === "string" && v.trim() ? v.trim() : null;

     const direct =
          tryStr(d.message) ||
          tryStr(d.detail) ||
          (Array.isArray(d.non_field_errors) && tryStr(d.non_field_errors[0])) ||
          (Array.isArray(d.errors) &&
               d.errors[0] &&
               typeof d.errors[0] === "object" &&
               tryStr((d.errors[0] as Record<string, unknown>).message));

     return direct || fallback;
}

function extractErrorCode(data: unknown): string | undefined {
     if (!data || typeof data !== "object") return undefined;
     const code = (data as Record<string, unknown>).error_code;
     return typeof code === "string" ? code : undefined;
}

function toApiError(err: unknown): ApiError {
     if (err instanceof ApiError) return err;

     if (axios.isAxiosError(err)) {
          const status = err.response?.status ?? 0;
          const data = err.response?.data;
          const message = extractMessage(
               data,
               err.message || "خطای نامشخص"
          );
          return new ApiError(message, status, data, extractErrorCode(data));
     }

     if (err instanceof Error) {
          return new ApiError(err.message || "خطای نامشخص", 0, null);
     }

     return new ApiError("خطای نامشخص", 0, err);
}

// ==================================================================
// Refresh با Mutex (جلوگیری از درخواست‌های همزمان)
// ==================================================================

let refreshPromise: Promise<boolean> | null = null;

export function refreshAccessToken(): Promise<boolean> {
     if (refreshPromise) return refreshPromise;

     refreshPromise = (async (): Promise<boolean> => {
          try {
               const res = await fetch(`${BASE_URL}auth/token/refresh/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
               });

               if (!res.ok) {
                    clearLocalStorage();
                    return false;
               }

               const json = await res.json().catch(() => null);
               const newToken =
                    json?.data?.access_token ??
                    json?.data ??
                    json?.access_token;

               if (typeof newToken === "string" && newToken) {
                    setLocalStorage(Token, newToken);
                    return true;
               }

               clearLocalStorage();
               return false;
          } catch (err) {
               console.error("[http] refresh error:", err);
               clearLocalStorage();
               return false;
          } finally {
               refreshPromise = null;
          }
     })();

     return refreshPromise;
}

async function ensureAuth(): Promise<boolean> {
     const token = getLocalStorage(Token);
     if (!token) {
          clearLocalStorage();
          safeRedirect(LOGIN_PATH);
          return false;
     }
     if (isTokenExpired(token)) {
          const ok = await refreshAccessToken();
          if (!ok) {
               clearLocalStorage();
               safeRedirect(LOGIN_PATH);
               return false;
          }
     }
     return true;
}

// ==================================================================
// Header builder (همیشه باAuth در صورت وجود توکن)
// ==================================================================

function buildHeaders(
     isFormData: boolean,
     withCsrf: boolean
): Record<string, string> {
     const headers: Record<string, string> = { Accept: "application/json" };
     if (!isFormData) headers["Content-Type"] = "application/json";

     const token = getLocalStorage(Token);
     if (token) headers.Authorization = `Bearer ${token}`;

     if (withCsrf) {
          const csrf = getCookie("csrftoken");
          if (csrf) headers["X-CSRFToken"] = csrf;
     }

     return headers;
}

// ==================================================================
// هسته‌ی درخواست (با retry پس از refresh)
// ==================================================================

type HttpMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

interface RequestOptions {
     url: string;
     method: HttpMethod;
     data?: unknown;
     params?: Record<string, unknown>;
     hasAuth?: boolean;
}

async function request<T = unknown>(opts: RequestOptions): Promise<T> {
     const hasAuth = opts.hasAuth ?? true;
     const isFormData =
          typeof FormData !== "undefined" && opts.data instanceof FormData;
     const withCsrf = opts.method !== "GET" && RunInServer;

     if (hasAuth && !(await ensureAuth())) {
          throw new ApiError("Unauthorized", 401);
     }

     const send = async (): Promise<T> => {
          const res = await axios.request<T>({
               url: opts.url,
               method: opts.method,
               data: opts.data,
               params: opts.params,
               headers: buildHeaders(isFormData, withCsrf),
               withCredentials: true,
               timeout: REQUEST_TIMEOUT_MS,
          });
          return res.data;
     };

     try {
          return await send();
     } catch (err) {
          // تلاش مجدد پس از refresh (فقط یک بار)
          if (axios.isAxiosError(err) && err.response?.status === 401 && hasAuth) {
               const refreshed = await refreshAccessToken();
               if (refreshed) {
                    try {
                         return await send();
                    } catch (retryErr) {
                         if (
                              axios.isAxiosError(retryErr) &&
                              retryErr.response?.status === 401
                         ) {
                              clearLocalStorage();
                              safeRedirect(LOGIN_PATH);
                         }
                         throw toApiError(retryErr);
                    }
               }
               clearLocalStorage();
               safeRedirect(LOGIN_PATH);
          }
          throw toApiError(err);
     }
}

// ==================================================================
// Public API
// ==================================================================

export const apiGET = <T = unknown>(
     url: string,
     params: Record<string, unknown> = {},
     hasAuth = true
): Promise<T> => request<T>({ url, method: "GET", params, hasAuth });

export const apiPOST = <T = unknown>(
     url: string,
     data: unknown,
     hasAuth = true
): Promise<T> => request<T>({ url, method: "POST", data, hasAuth });

export const apiPATCH = <T = unknown>(
     url: string,
     data: unknown,
     hasAuth = true
): Promise<T> => request<T>({ url, method: "PATCH", data, hasAuth });

export const apiPUT = <T = unknown>(
     url: string,
     data: unknown,
     hasAuth = true
): Promise<T> => request<T>({ url, method: "PUT", data, hasAuth });

export const apiDELETE = <T = unknown>(
     url: string,
     hasAuth = true
): Promise<T> => request<T>({ url, method: "DELETE", hasAuth });

// ==================================================================
// Generic fetch (برای ماژول‌های خاص)
// ==================================================================

export async function apiFetch<T>(
     path: string,
     init: RequestInit = {}
): Promise<T> {
     const token = getLocalStorage(Token);
     const headers = new Headers(init.headers);
     const isFormData =
          typeof FormData !== "undefined" && init.body instanceof FormData;

     if (!headers.has("Content-Type") && init.body && !isFormData) {
          headers.set("Content-Type", "application/json");
     }
     if (token) headers.set("Authorization", `Bearer ${token}`);
     headers.set("Accept", "application/json");

     const res = await fetch(`${BASE_URL.replace(/\/$/, "")}${path}`, {
          ...init,
          headers,
          credentials: "include",
          cache: "no-store",
     });

     if (res.status === 204) return undefined as T;

     const contentType = res.headers.get("content-type") || "";
     const payload = contentType.includes("application/json")
          ? await res.json().catch(() => null)
          : await res.text().catch(() => "");

     if (!res.ok) {
          throw new ApiError(
               extractMessage(payload, `خطای سرور (${res.status})`),
               res.status,
               payload
          );
     }
     return payload as T;
}