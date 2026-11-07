//  src/shared/utils/date.ts


import moment from "moment-jalaali";

export const convertToJalaliDateTime = (iso: string): string => {
  if (!iso) return "-";
  return moment(iso).format("jYYYY/jMM/jDD - HH:mm");
};

export const convertToJalaliDate = (iso: string): string => {
  if (!iso) return "-";
  return moment(iso).format("jYYYY/jMM/jDD");
};


const persianMonths = [
  "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
];


export const convertToJalaliDateMonth = (iso: string): string => {
  if (!iso) return "-";
  const m = moment(iso);
  const monthIndex = parseInt(m.format("jM"), 10) - 1;
  return `${m.format("jD")} ${persianMonths[monthIndex]} ${m.format("jYYYY")}`;
};

export function formatDateToYMD(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function persianYearMonth(): string {
  return new Intl.DateTimeFormat("fa", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date());
}