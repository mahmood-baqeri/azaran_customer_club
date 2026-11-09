// src/modules/visit_module/repository/visit.repository.ts

import { visitApi } from "../api/visit.api";
import type { AvailableVisit, RequestVisit } from "../interface/visit.types";

export const visitRepository = {
  async listAvailable(): Promise<AvailableVisit[]> {
    const res = await visitApi.listAvailable();
    return Array.isArray(res.data) ? res.data : [];
  },

  async create(payload: Parameters<typeof visitApi.create>[0]): Promise<RequestVisit | null> {
    const res = await visitApi.create(payload);
    if (res.status === "Error") throw new Error(res.message);
    return res.data ?? null;
  },

  async list(): Promise<RequestVisit[]> {
    const res = await visitApi.list();
    return Array.isArray(res.data) ? res.data : [];
  },

  async detail(id: number): Promise<RequestVisit | null> {
    const res = await visitApi.detail(id);
    if (res.status === "Error") throw new Error(res.message);
    return res.data ?? null;
  },

  async delete(id: number): Promise<boolean> {
    const res = await visitApi.delete(id);
    if (res.status === "Error") throw new Error(res.message);
    return res.status === "Success";
  },
};