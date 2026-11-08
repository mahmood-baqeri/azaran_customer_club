// src/modules/factor_module/screen/create_factor.screen.tsx

import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import FactorForm from "../components/FactorForm";
import { factorRepository } from "../repository/factor.repository";
import { MyNotification } from "../../../shared/utils/notification";
import { FACTOR_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import type { FactorFormData } from "../interface/factor.types";
import "../../../shared/styles/project.css"; // استفاده از استایل‌های مشترک فرم

export default function CreateFactorScreen() {
     const navigate = useNavigate();
     const [submitting, setSubmitting] = useState(false);
     const [formData, setFormData] = useState<FactorFormData | null>(null);
     const [isValid, setIsValid] = useState(false);

     const handleFormChange = useCallback((data: FactorFormData, valid: boolean) => {
          setFormData(data);
          setIsValid(valid);
     }, []);

     const handleSave = async () => {
          if (!formData || !isValid || !formData.photoFile) {
               MyNotification("خطا", "لطفاً تصویر فاکتور را انتخاب کنید.", "error");
               return;
          }

          setSubmitting(true);
          try {
               const fd = new FormData();
               fd.append("photo", formData.photoFile);

               if (formData.invoice_number) fd.append("invoice_number", formData.invoice_number);
               if (formData.invoice_issue_at) fd.append("invoice_issue_at", formData.invoice_issue_at.toISOString());
               if (formData.amount) fd.append("amount", convertPersianToEnglish(formData.amount.toString()));
               if (formData.number_water_taps) fd.append("number_water_taps", convertPersianToEnglish(formData.number_water_taps.toString()));
               if (formData.number_connections) fd.append("number_connections", convertPersianToEnglish(formData.number_connections.toString()));
               if (formData.pipe_length) fd.append("pipe_length", convertPersianToEnglish(formData.pipe_length.toString()));
               if (formData.shop_name) fd.append("shop_name", formData.shop_name);
               if (formData.seller_phone) fd.append("seller_phone", convertPersianToEnglish(formData.seller_phone));
               if (formData.seller_address) fd.append("seller_address", formData.seller_address);

               await factorRepository.create(fd);
               MyNotification("", "فاکتور با موفقیت ثبت شد", "success");
               navigate(FACTOR_ROUTES.list);
          } catch (err: unknown) {
               let msg = "خطا در ثبت فاکتور";
               if (err instanceof Error) msg = err.message;
               MyNotification("خطا", msg, "error");
          } finally {
               setSubmitting(false);
          }
     };

     return (
          <>
               <Header title="ثبت فاکتور" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="display-grid">

                    <FactorForm onChange={handleFormChange} />

                    <div className="proj-sticky-bottom my-4">
                         <button className="auth-btn" onClick={handleSave} disabled={submitting || !isValid}>
                              {submitting ? "در حال ثبت..." : "ثبت فاکتور"}
                         </button>
                    </div>

               </div>
          </>
     );
}