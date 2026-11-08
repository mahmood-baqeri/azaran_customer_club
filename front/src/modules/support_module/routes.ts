// src/modules/support_module/routes.ts

export const SUPPORT_ROUTES = {
  list: "/support",
  create: "/support/create",
  detail: (id: number | string) => `/support/${id}`, // برای آینده (چت)
};