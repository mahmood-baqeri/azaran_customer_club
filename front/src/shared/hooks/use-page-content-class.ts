// src/shared/hooks/use-page-content-class.ts

import { useEffect } from "react";

/**
 * هوک برای اضافه کردن کلاس‌های سفارشی به wrapper اصلی صفحه (page-content-wrapper)
 * @param className نام کلاس یا کلاس‌هایی که می‌خواهید اضافه شوند (با فاصله جدا شوند)
 */
export const usePageContentClass = (className: string) => {
  useEffect(() => {
    const wrapper = document.querySelector(".page-content-wrapper");
    if (!wrapper) return;

    // جدا کردن کلاس‌ها در صورتی که کاربر چند کلاس پشت سر هم بفرستد
    const classes = className.split(" ").filter(Boolean);
    
    // اضافه کردن کلاس‌ها
    classes.forEach((cls) => wrapper.classList.add(cls));

    // تابع پاکسازی هنگام خروج از صفحه
    return () => {
      classes.forEach((cls) => wrapper.classList.remove(cls));
    };
  }, [className]);
};