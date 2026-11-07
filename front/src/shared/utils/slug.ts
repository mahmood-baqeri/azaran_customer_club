//  src/shared/utils/slug.ts

export const convertToSlug = (text: string): string => {
  if (!text) return "";
  return text
    .toString()
    .replace(/[\s\u200c]+/g, "-")
    .replace(/[^\u0600-\u06FF\u0750-\u077F\ufb50-\ufdff\ufe70-\ufeff0-9a-zA-Z-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-+/, "")
    .replace(/-+$/, "");
};

export const convertSlugToText = (slug: string): string =>
  slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

export const convertPersianToEnglish = (persian: string): string => {
  const fa = ["۰","۱","۲","۳","۴","۵","۶","۷","۸","۹"];
  const en = ["0","1","2","3","4","5","6","7","8","9"];
  let out = persian;
  fa.forEach((ch, i) => {
    out = out.replace(new RegExp(ch, "g"), en[i]);
  });
  return out;
};