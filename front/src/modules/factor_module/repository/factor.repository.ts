// src/modules/factor_module/repository/factor.repository.ts

import { factorApi } from "../api/factor.api";
import type { Factor } from "../interface/factor.types";

export const factorRepository = {
  async create(formData: FormData): Promise<Factor | null> {
    const res = await factorApi.create(formData);
    if (res.status === "Error") throw new Error(res.message);
    return res.data ?? null;
  },

  async list(): Promise<Factor[]> {
    const res = await factorApi.list();
    return Array.isArray(res.data) ? res.data : [];
  },

  async detail(id: number): Promise<Factor | null> {
    const res = await factorApi.detail(id);
    return res.data ?? null;
  },

  async update(id: number, formData: FormData): Promise<Factor | null> {
    const res = await factorApi.update(id, formData);
    if (res.status === "Error") throw new Error(res.message);
    return res.data ?? null;
  },

  async deleteFactor(id: number): Promise<boolean> {
    const res = await factorApi.deleteFactor(id);
    if (res.status === "Error") throw new Error(res.message);
    return res.status === "Success";
  },
};