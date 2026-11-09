// src/modules/learn_module/repository/learn.repository.ts

import { learnApi } from "../api/learn.api";
import type { LearnItem } from "../interface/learn.types";

export const learnRepository = {
  async list(size?: string): Promise<LearnItem[]> {
    const res = await learnApi.list(size);
    return Array.isArray(res.data) ? res.data : [];
  },

  async detail(id: number): Promise<LearnItem | null> {
    const res = await learnApi.detail(id);
    return res.data ?? null;
  },
};