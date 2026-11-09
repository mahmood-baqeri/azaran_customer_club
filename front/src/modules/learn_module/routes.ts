// src/modules/learn_module/routes.ts

export const LEARN_ROUTES = {
  list: "/learn",
  detail: (id: number | string) => `/learn/${id}`,
} as const;