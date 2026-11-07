// src/modules/settings_module/repository/settings.repository.ts

import { settingsApi, sliderApi } from "../api/settings.api";
import type { SettingInterface, SliderItem } from "../interface/settings.types";

const arrayToObject = (
  arr: { key: string; value: unknown }[]
): SettingInterface =>
  arr.reduce((obj, item) => {
    if (item?.key) obj[item.key] = item.value;
    return obj;
  }, {} as SettingInterface);

export const settingsRepository = {
  async load(): Promise<SettingInterface> {
    const res = await settingsApi.fetch();
    
    // ✅ استخراج آرایه واقعی از داخل پاسخ سرور
    const items = res?.data ?? [];
    
    if (!Array.isArray(items)) {
      console.warn("[settings] unexpected response shape:", res);
      return {};
    }
    
    return arrayToObject(items);
  },
};


export const sliderRepository = {
  async list(): Promise<SliderItem[]> {
    const res = await sliderApi.list();
    if (!Array.isArray(res?.data)) return [];
    return res.data;
  },
};