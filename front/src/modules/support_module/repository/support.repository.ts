// src/modules/support_module/repository/support.repository.ts

import { supportApi } from "../api/support.api";
import type { SupportTicket } from "../interface/support.types";

export const supportRepository = {
  async createTicket(formData: FormData): Promise<SupportTicket | null> {
    const res = await supportApi.createTicket(formData);
    if (res.status === "Error") throw new Error(res.message);
    return res.data ?? null;
  },

  async listTickets(): Promise<SupportTicket[]> {
    const res = await supportApi.listTickets();
    return Array.isArray(res.data) ? res.data : [];
  },
};