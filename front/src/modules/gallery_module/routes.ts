// src/modules/gallery_module/routes.ts

export const GALLERY_ROUTES = {
  list: "/gallery",
  create: "/gallery/create",
  detail: (id: number | string) => `/gallery/${id}`,
};