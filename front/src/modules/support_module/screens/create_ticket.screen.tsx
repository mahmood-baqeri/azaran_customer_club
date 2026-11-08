// src/modules/support_module/screen/create_ticket.screen.tsx

import { useState } from "react";
// import { useNavigate } from "react-router-dom";
import axios from "axios";
import Header from "../../../app/layouts/header";
import { supportRepository } from "../repository/support.repository";
import { MyNotification } from "../../../shared/utils/notification";
// import { SUPPORT_ROUTES } from "../routes";
import type { SupportCategory } from "../interface/support.types";
import "../../../shared/styles/support.css";
import Textarea from "../../../shared/components/inputs/Textarea";

const CATEGORIES: { key: SupportCategory; label: string }[] = [
  { key: "site_issue", label: "مشکلات سایت" },
  { key: "invoice", label: "ثبت فاکتور" },
  { key: "gift_order", label: "سفارش هدیه" },
  { key: "complaint", label: "انتقاد" },
  { key: "suggestion", label: "پیشنهاد" },
  { key: "other", label: "سایر" },
];

export default function CreateTicketScreen() {
  // const navigate = useNavigate();
  const [category, setCategory] = useState<SupportCategory>("site_issue");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const isValid = text.trim().length > 10;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    const MAX_SIZE = 5 * 1024 * 1024; // 5MB
    const ALLOWED = ["image/jpeg", "image/png", "image/jpg", "application/pdf"];

    if (selected.size > MAX_SIZE) {
      MyNotification("خطا", "حجم فایل نباید بیشتر از ۵ مگابایت باشد.", "error");
      return;
    }
    if (!ALLOWED.includes(selected.type)) {
      MyNotification("خطا", "فقط تصویر یا PDF مجاز است.", "error");
      return;
    }
    setFile(selected);
  };

  const handleSubmit = async () => {
    if (!isValid) {
      MyNotification("خطا", "لطفاً موضوع را با جزئیات بیشتری شرح دهید (حداقل ۱۰ کاراکتر).", "error");
      return;
    }

    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.append("category", category);
      // چون فیلد موضوع در UI نداریم، ۳۰ کاراکتر اول متن را به عنوان موضوع می‌فرستیم
      fd.append("subject", text.substring(0, 30) + "...");
      fd.append("text", text.trim());

      if (file) {
        fd.append("file", file);
      }

      await supportRepository.createTicket(fd);

      MyNotification("", "درخواست شما با موفقیت ثبت شد.", "success");
      // navigate(SUPPORT_ROUTES.list);
    } catch (err: unknown) {
      let msg = "خطا در ثبت درخواست";
      if (axios.isAxiosError(err) && err.response?.data?.message) {
        msg = err.response.data.message;
      } else if (err instanceof Error) {
        msg = err.message;
      }
      MyNotification("خطا", msg, "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Header title="پشتیبانی" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

      <div className="display-grid">

        <div className="support-body">
          <h2 className="support-title">چگونه می‌توانیم به شما کمک کنیم؟</h2>
          <p className="support-subtitle">موضوع درخواست خود را انتخاب و توضیحات را وارد کنید</p>

          <h3 className="support-section-title">موضوع درخواست</h3>

          <div className="support-categories">
            {CATEGORIES.map((c) => (
              <button
                key={c.key}
                type="button"
                className={`support-pill ${category === c.key ? "active" : ""}`}
                onClick={() => setCategory(c.key)}
              >
                {c.label}
              </button>
            ))}
          </div>

          <h3 className="support-section-title mt-5">لطفا موضوع را شرح دهید</h3>

          <Textarea
            value={text}
            onChange={setText}
            minLength={10}
            maxLength={1000}
            required
            showCounter
            className="support-textarea"
            placeholder="نوع مشکل و صفحه‌ای که در آن رخ داده را بنویسید"
            errorMessage="نظر باید بین ۱۰ تا ۱۰۰۰ کاراکتر باشد"
          />



          <label className="support-file-upload">
            <input type="file" accept="image/*, .pdf" onChange={handleFileChange} hidden />
            <div className="support-file-content">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#14306b" strokeWidth="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
              <div className="support-file-text me-3">
                <strong>پیوست فایل</strong>
                <span>تصویر یا PDF، اختیاری</span>
              </div>
            </div>
            {file && <span className="support-file-name">{file.name}</span>}
          </label>

        </div>

        <button
          className="support-submit-btn"
          onClick={handleSubmit}
          disabled={!isValid || submitting}
        >
          {submitting ? "در حال ارسال..." : "ارسال درخواست"}
        </button>
      </div>
    </>
  );
}