// src/shared/hooks/use-form-validity.ts

export function useFormValidity(checks: boolean[]): boolean {
  return checks.every(Boolean);
}