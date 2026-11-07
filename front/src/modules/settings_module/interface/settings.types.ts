// src/modules/settings_module/interface/location.types.ts

export interface SettingInterface {
  currentDay?: string;
  FavIcon?: string;
  Logo?: string;
  MoneyFlag?: string;
  SiteName?: string;
  SiteURL?: string;
  ActiveGiftOrder?: string;
  userScore?: string;
  userAccess?: string;
  userFullname?: string;
  userFirstname?: string;
  userLastname?: string;
  userPersonCode?: string;
  userAvatar?: string;
  address?: string;
  postCode?: string;
  phone?: string;
  userID?: number;
  [key: string]: unknown;
}


export interface Province {
  id: number;
  name: string;
  code: string;
}

export interface City {
  id: number;
  name: string;
}

// -------- اسلایدر --------
export interface SliderItem {
  id: number;
  title: string;
  paragraph: string;
  photo: string | null;
}