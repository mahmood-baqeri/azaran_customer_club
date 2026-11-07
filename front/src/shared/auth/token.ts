//  src/shared/auth/token.ts

import { getLocalStorage } from "../storage/local-storage";

export function isTokenExpired(token: string): boolean {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp < Math.floor(Date.now() / 1000);
  } catch (e) {
    console.error("Invalid token", e);
    return true;
  }
}

export const readAccessToken = (): string | null =>
  getLocalStorage("access_token");