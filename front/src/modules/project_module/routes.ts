// src/modules/project_module/routes.ts

export const PROJECT_ROUTES = {
  list: "/projects",
  create: "/projects/create",
  detail: (id: number | string) => `/projects/${id}`,
  edit: (id: number | string) => `/projects/${id}/edit`,
  upload: (id: number | string) => `/projects/${id}/upload`,
};