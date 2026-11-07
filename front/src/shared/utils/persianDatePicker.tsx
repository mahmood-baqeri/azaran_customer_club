// front/src/shared/utils/persianDatePicker.tsx

import React from "react";
import DatePicker from "react-multi-date-picker";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";
import type DateObject from "react-date-object";

interface PersianDatePickerProps {
  value?: Date | null;
  onChange: (date: Date | null) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const PersianDatePicker: React.FC<PersianDatePickerProps> = ({
  value,
  onChange,
  placeholder = "انتخاب تاریخ",
  disabled,
}) => {
  return (
    <DatePicker
      value={value ?? ""}
      onChange={(dateObject: DateObject | DateObject[] | null) => {
        if (dateObject && !Array.isArray(dateObject)) {
          onChange(dateObject.toDate());
        } else {
          onChange(null);
        }
      }}
      calendar={persian}
      locale={persian_fa}
      calendarPosition="bottom-center"
      placeholder={placeholder}
      disabled={disabled}
      // 👇 استایل اینلاین برای هم‌شکل شدن دقیق با EditInput
      style={{
        width: "100%",
        height: "50px",
        padding: "0 16px",
        background: "#fff",
        border: "1.5px solid #E7E7E7",
        borderRadius: "12px",
        fontSize: "13px",
        color: "#14306b",
        fontFamily: "inherit",
        outline: "none",
        boxSizing: "border-box",
        textAlign: "center",
        cursor: "pointer",
      }}
    />
  );
};