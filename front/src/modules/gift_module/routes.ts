// src/modules/gift_module/routes.ts

export const GIFT_ROUTES = {
  list: "/gifts",
  detail: (id: number | string) => `/gifts/${id}`,
  success: (id: number | string) => `/gifts/success/${id}`,
      
  // سفارشات
  orders: "/orders",
  orderDetail: (id: number | string) => `/orders/${id}`,
};