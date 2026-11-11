// src/modules/user_module/hooks/use-level.ts

import { useCallback, useEffect, useState } from "react";
import { userRepository } from "../repository/user.repository";
import type { LevelPerk } from "../interface/level.types";
import type { UserLevelInfo, UserMe } from "../interface/user.types";
import { ICONS } from "../../../shared/constants/icons";
import { GIFT_ROUTES } from "../../gift_module/routes";
import { PROMOTION_ROUTES } from "../../promotion_module/routes";
import { VISIT_ROUTES } from "../../visit_module/routes";

// ✅ مزایای کاردان (تصویر سمت چپ)
const KARDAN_ACTIVE_PERKS: LevelPerk[] = [
  { id: "k1", title: "کسب امتیاز از چالش‌ها و ثبت پروژه", icon: ICONS.star, is_locked: false, help: "", href: "" },
  { id: "k2", title: "خرید هدایای متنوع با امتیاز", icon: ICONS.basket_verify, is_locked: false, help: "", href: GIFT_ROUTES.list },
  { id: "k3", title: " 1 پک تبلیغاتی در سال", icon:  ICONS.box, is_locked: false, help: "", href: PROMOTION_ROUTES.list },
];

const KARDAN_LOCKED_PERKS: LevelPerk[] = [
  { id: "kl1", title: "۱۰٪ تخفیف روی هدایا", icon: ICONS.percentage_square, is_locked: true, help: "", href: GIFT_ROUTES.list  },
  { id: "kl2", title: " 2 پک تبلیغاتی در سال", icon:  ICONS.box, is_locked: true , help: "", href: PROMOTION_ROUTES.list},
  { id: "kl3", title: "هدایای مناسبتی ویژه", icon: ICONS.gift_5, is_locked: true, help: "", href: "" },
  { id: "kl4", title: "بازدید حضوری از کارخانه", icon: ICONS.building, is_locked: true, help: "ویژه اعضای اصفهان", href: VISIT_ROUTES.create },
];

// ✅ مزایای استادکار (تصویر سمت راست)
const OSTADKAR_ACTIVE_PERKS: LevelPerk[] = [
  { id: "o1", title: "کسب امتیاز از چالش‌ها و ثبت پروژه", icon: ICONS.star, is_locked: false, help: "", href: "" },
  { id: "o2", title: "خرید هدایای متنوع با امتیاز", icon: ICONS.basket_verify, is_locked: false, help: "", href: GIFT_ROUTES.list },
  { id: "o3", title: " 2 پک تبلیغاتی در سال", icon: ICONS.box, is_locked: false, help: "", href: PROMOTION_ROUTES.list },
  { id: "o4", title: "۱۰٪ تخفیف روی هدایا", icon: ICONS.percentage_square, is_locked: false, help: "", href: GIFT_ROUTES.list  },
  { id: "o5", title: "هدایای مناسبتی ویژه", icon: ICONS.gift_5, is_locked: false, help: "", href: "" },
  { id: "o6", title: "بازدید حضوری از کارخانه", icon: ICONS.building, is_locked: false, help: "ویژه اعضای اصفهان" , href: VISIT_ROUTES.create },
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