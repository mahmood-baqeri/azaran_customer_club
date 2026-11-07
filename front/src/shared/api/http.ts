// src/shared/api/http.ts

/* eslint-disable @typescript-eslint/no-explicit-any */
import axios, { AxiosError } from "axios";
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

// =========================================================
// ✅ تبدیل هر خطا به ApiError با پیام واقعی بک‌اند
// =========================================================
function toApiError(err: unknown): ApiError {
  if (err instanceof ApiError) return err;

  if (axios.isAxiosError(err)) {
    const status = err.response?.status ?? 0;
    const data = err.response?.data as
      | {
          status?: string;
          message?: string;
          error_code?: string;
          detail?: string;
          errors?: Array<{ message?: string }>;
        }
      | undefined;

    const message =
      (typeof data?.message === "string" && data.message.trim()) ||
      (typeof data?.detail === "string" && data.detail.trim()) ||
      (Array.isArray(data?.errors) && data.errors[0]?.message) ||
      err.message ||
      "خطای نامشخص";

    const errorCode =
      typeof data?.error_code === "string" ? data.error_code : undefined;

    return new ApiError(message, status, data, errorCode);
  }

  if (err instanceof Error) {
    return new ApiError(err.message || "خطای نامشخص", 0, null);
  }

  return new ApiError("خطای نامشخص", 0, err);
}

// ------- Refresh --------
export async function refreshAccessToken(): Promise<boolean> {
  try {
    // ✅ درخواست به بک‌اند؛ کوکی HttpOnly خودکار ارسال می‌شود
    const res = await fetch(`${BASE_URL}auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // 👈 حیاتی برای ارسال کوکی
    });

    if (!res.ok) {
      clearLocalStorage();
      return false;
    }

    const json = await res.json();
    // بک‌اند شما new_access_token را در data برمی‌گرداند
    const newToken = json.data?.access_token || json.data;

    if (newToken) {
      setLocalStorage(Token, newToken);
      return true;
    }
    return false;
  } catch (err) {
    console.error("[http] refresh error:", err);
    clearLocalStorage();
    return false;
  }
}

const ensureAuth = async (): Promise<boolean> => {
  const token = getLocalStorage(Token);
  if (!token) {
    clearLocalStorage();
    redirectTo("/login");
    return false;
  }
  if (isTokenExpired(token)) {
    const ok = await refreshAccessToken();
    if (!ok) {
      clearLocalStorage();
      redirectTo("/login");
      return false;
    }
  }
  return true;
};

const buildHeaders = (
  hasAuth: boolean,
  isFormData: boolean,
  withCsrf = false
): Record<string, string> => {
  const headers: Record<string, string> = {};
  if (!isFormData) headers["Content-Type"] = "application/json";
  if (hasAuth) headers["Authorization"] = `Bearer ${getLocalStorage(Token)}`;
  if (withCsrf) {
    const csrf = getCookie("csrftoken");
    if (csrf) headers["X-CSRFToken"] = csrf;
  }
  return headers;
};

// ⚠️ in all requests, withCredentials must be true to handle cookies
export const apiGET = async <T = unknown>(
  url: string,
  params: Record<string, unknown> = {},
  hasAuth = true
): Promise<T> => {
  if (hasAuth && !(await ensureAuth())) throw new ApiError("Unauthorized", 401);
  try {
    const res = await axios.get<T>(url, {
      headers: buildHeaders(hasAuth, false),
      params,
      withCredentials: true, // 👈
    });
    return res.data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.status === 401) {
      clearLocalStorage();
      redirectTo("/login");
    }
    throw toApiError(err);
  }
};

export const apiPOST = async <T = unknown>(
  url: string,
  data: any,
  hasAuth = true
): Promise<T> => {
  if (hasAuth && !(await ensureAuth())) throw new ApiError("Unauthorized", 401);
  try {
    const isFormData = data instanceof FormData;
    const res = await axios.post<T>(url, data, {
      headers: buildHeaders(hasAuth, isFormData, RunInServer),
      withCredentials: true, // 👈
    });
    return res.data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.status === 401) {
      clearLocalStorage();
      redirectTo("/login");
    }
    throw toApiError(err);
  }
};

export const apiPATCH = async (
  url: string,
  data: any,
  hasAuth = true
): Promise<any> => {
  if (hasAuth && !(await ensureAuth())) throw new ApiError("Unauthorized", 401);
  try {
    const isFormData = data instanceof FormData;
    const res = await axios.patch(url, data, {
      headers: buildHeaders(hasAuth, isFormData, RunInServer),
      withCredentials: RunInServer,
    });
    return res.data;
  } catch (err) {
    if (err instanceof AxiosError) {
      const code = (err.response?.data as any)?.error_code;
      if (code === "token_not_valid") {
        clearLocalStorage();
        redirectTo("/login");
      }
    }
    throw toApiError(err);
  }
};

// export async function apiDELETE<T = any>(
//   url: string,
//   withAuth: boolean = true
// ): Promise<T> {
//   const headers: Record<string, string> = {};
//   if (withAuth) {
//     const token = localStorage.getItem("access_token");
//     if (token) headers["Authorization"] = `Bearer ${token}`;
//   }

//   try {
//     const res = await fetch(url, { method: "DELETE", headers });
//     const contentType = res.headers.get("content-type") || "";
//     const payload = contentType.includes("application/json")
//       ? await res.json().catch(() => null)
//       : await res.text().catch(() => "");

//     if (!res.ok) {
//       const message =
//         (payload &&
//           typeof payload === "object" &&
//           typeof (payload as any).message === "string" &&
//           (payload as any).message) ||
//         (payload &&
//           typeof payload === "object" &&
//           typeof (payload as any).detail === "string" &&
//           (payload as any).detail) ||
//         `خطای سرور (${res.status})`;
//       throw new ApiError(message, res.status, payload);
//     }
//     return payload as T;
//   } catch (err) {
//     throw toApiError(err);
//   }
// }

export const apiDELETE = async <T = unknown>(
  url: string,
  hasAuth = true
): Promise<T> => {
  if (hasAuth && !(await ensureAuth())) throw new Error("Unauthorized");
  try {
    const res = await axios.delete<T>(url, {
      headers: buildHeaders(hasAuth, false, RunInServer),
      withCredentials: true,
    });
    return res.data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.status === 401) {
      clearLocalStorage();
      redirectTo("/login");
    }
    throw err;
  }
};

// ------- Generic fetch (برای ماژول‌های خاص مثل suggestions) ----
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
    const message =
      (typeof payload === "object" &&
        payload !== null &&
        "message" in payload &&
        String((payload as { message: unknown }).message)) ||
      (typeof payload === "object" &&
        payload !== null &&
        "detail" in payload &&
        String((payload as { detail: unknown }).detail)) ||
      `خطای سرور (${res.status})`;
    throw new ApiError(message, res.status, payload);
  }
  return payload as T;
}