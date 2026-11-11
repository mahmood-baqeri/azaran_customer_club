// src/modules/user_module/interface/level.types.ts

export interface LevelPerk {
  id: string;
  title: string;
  icon: string;
  help: string;
  href: string;
  is_locked: boolean;
}