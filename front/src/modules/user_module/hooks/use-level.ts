// src/modules/user_module/hooks/use-level.ts

import { useCallback, useEffect, useState } from "react";
import { userRepository } from "../repository/user.repository";
import type { LevelPerk } from "../interface/level.types";
import type { UserLevelInfo, UserMe } from "../interface/user.types";

// ✅ مزایای کاردان (تصویر سمت چپ)
const KARDAN_ACTIVE_PERKS: LevelPerk[] = [
  { id: "k1", title: "کسب امتیاز از چالش‌ها و ثبت پروژه", icon_name: "icon-star", is_locked: false },
  { id: "k2", title: "خرید هدایای متنوع با امتیاز", icon_name: "icon-gift", is_locked: false },
  { id: "k3", title: "پک تبلیغاتی در سال", icon_name: "icon-box", is_locked: false },
];

const KARDAN_LOCKED_PERKS: LevelPerk[] = [
  { id: "kl1", title: "۱۰٪ تخفیف روی هدایا", icon_name: "icon-discount", is_locked: true },
  { id: "kl2", title: "پک تبلیغاتی در سال", icon_name: "icon-box", is_locked: true },
  { id: "kl3", title: "هدایای مناسبتی ویژه", icon_name: "icon-cake", is_locked: true },
  { id: "kl4", title: "بازدید حضوری از کارخانه", icon_name: "icon-building", is_locked: true },
];

// ✅ مزایای استادکار (تصویر سمت راست)
const OSTADKAR_ACTIVE_PERKS: LevelPerk[] = [
  { id: "o1", title: "کسب امتیاز از چالش‌ها و ثبت پروژه", icon_name: "icon-star", is_locked: false },
  { id: "o2", title: "خرید هدایای متنوع با امتیاز", icon_name: "icon-gift", is_locked: false },
  { id: "o3", title: "پک تبلیغاتی در سال", icon_name: "icon-box", is_locked: false },
  { id: "o4", title: "۱۰٪ تخفیف روی هدایا", icon_name: "icon-discount", is_locked: false },
  { id: "o5", title: "هدایای مناسبتی ویژه", icon_name: "icon-cake", is_locked: false },
  { id: "o6", title: "بازدید حضوری از کارخانه", icon_name: "icon-building", is_locked: false },
];

export interface LevelProfileView {
  user_name: string;
  avatar: string | null;
  levelInfo: UserLevelInfo;
  activePerks: LevelPerk[];
  lockedPerks: LevelPerk[];
}

export const useLevel = () => {
  const [userFull, setUserFull] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchFullProfile = useCallback(async () => {
    setLoading(true);
    try {
      // ✅ فقط در این صفحه درخواست سنگین را می‌زنیم
      const me = await userRepository.loadMe();
      setUserFull(me);
    } catch (err) {
      console.error("[level] loadMe failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFullProfile();
  }, [fetchFullProfile]);

  // ساخت خروجی نهایی
  const profile: LevelProfileView | null = userFull?.level
    ? {
        user_name: userFull.short_name || userFull.name || "کاربر",
        avatar: userFull.avatar,
        levelInfo: userFull.level,
        activePerks:
          userFull.level.current_level === "ostadkar"
            ? OSTADKAR_ACTIVE_PERKS
            : KARDAN_ACTIVE_PERKS,
        lockedPerks:
          userFull.level.current_level === "ostadkar" ? [] : KARDAN_LOCKED_PERKS,
      }
    : null;

  return { profile, loading, refresh: fetchFullProfile };
};