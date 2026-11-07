// src/modules/settings_module/api/settings.api.ts

import { apiGET } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { City, Province, SliderItem } from "../interface/settings.types";


// -------- Settings --------
export interface SettingItem {
  key: string;
  value: unknown;
}

export interface SettingsResponse {
  status: "Success" | "Error";
  message: string;
  data: SettingItem[];
  help_data?: Record<string, unknown>;
}

export const settingsApi = {
  fetch: (): Promise<SettingsResponse> =>
    apiGET(`${BASE_URL}setting/`, {}, true),
};

// -------- Sliders --------
export interface SliderListResponse {
  status: "Success" | "Error";
  message: string;
  data: SliderItem[];
}

export const sliderApi = {
  list: (): Promise<SliderListResponse> =>
    apiGET(`${BASE_URL}slider/`, {}, true),
};

// -------- Locations --------
interface LocationListResponse<T> {
  status: "Success" | "Error";
  message: string;
  data: T[];
}

export const locationApi = {
  getProvinces: (): Promise<LocationListResponse<Province>> =>
    apiGET(`${BASE_URL}setting/provinces/`, {}, true),

  getCities: (provinceId: number): Promise<LocationListResponse<City>> =>
    apiGET(`${BASE_URL}setting/provinces/${provinceId}/cities/`, {}, true),
};