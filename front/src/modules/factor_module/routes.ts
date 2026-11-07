// src/modules/factor_module/routes.ts

export const FACTOR_ROUTES = {
  list: "/factors",
  create: "/factors/create",
  edit: (id: number | string) => `/factors/${id}/edit`,
};