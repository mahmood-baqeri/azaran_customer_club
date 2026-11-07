//  src/shared/storage/local-storage.ts

export const getLocalStorage = (key: string): string | null =>
  localStorage.getItem(key);

export const setLocalStorage = (key: string, value: unknown): void => {
  localStorage.setItem(key, String(value));
};

export const clearLocalStorage = (): void => {
  localStorage.clear();
};

export function getCookie(name: string): string | null {
  if (!document.cookie) return null;
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const trimmed = cookie.trim();
    if (trimmed.startsWith(name + "=")) {
      return decodeURIComponent(trimmed.substring(name.length + 1));
    }
  }
  return null;
}