// src/modules/promotion_module/routes.ts

export const PROMOTION_ROUTES = {
  list: "/promotions",
  success: (id: number | string) => `/promotions/success/${id}`,
  orders: "/promotions/orders",
  orderDetail: (id: number | string) => `/promotions/orders/${id}`,
};