// src/modules/visit_module/routes.ts

export const VISIT_ROUTES = {
  list: "/visits",
  create: "/visits/create",
  detail: (id: number | string) => `/visits/${id}`,
};