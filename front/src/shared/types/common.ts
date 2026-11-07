//  src/shared/types/common.ts

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}