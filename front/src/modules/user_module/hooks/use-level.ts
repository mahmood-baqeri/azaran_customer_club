// src/modules/user_module/hooks/use-level.ts

import { useMemo } from "react";
import type { LevelPerk } from "../interface/level.types";
import type { UserLevelInfo } from "../interface/user.types";
import { ICONS } from "../../../shared/constants/icons";
import { GIFT_ROUTES } from "../../gift_module/routes";
import { PROMOTION_ROUTES } from "../../promotion_module/routes";
import { VISIT_ROUTES } from "../../visit_module/routes";
import { useUser } from "./use-user";

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
  const { user, loading } = useUser();

  const profile = useMemo<LevelProfileView | null>(() => {
    if (!user?.level) return null;
    const isOstadkar = user.level.current_level === "ostadkar";
    return {
      user_name: user.short_name || user.name || "کاربر",
      avatar: user.avatar,
      levelInfo: user.level,
      activePerks: isOstadkar ? OSTADKAR_ACTIVE_PERKS : KARDAN_ACTIVE_PERKS,
      lockedPerks: isOstadkar ? [] : KARDAN_LOCKED_PERKS,
    };
  }, [user]);

  return { profile, loading };
};