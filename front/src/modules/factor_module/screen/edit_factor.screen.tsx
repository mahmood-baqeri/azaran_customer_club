// src/modules/factor_module/screen/edit_factor.screen.tsx

import { useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import FactorForm from "../components/FactorForm";
import { factorRepository } from "../repository/factor.repository";
import { useFactorDetail } from "../hooks/use-factor-detail";
import { MyNotification } from "../../../shared/utils/notification";
import { FACTOR_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import type { FactorFormData } from "../interface/factor.types";
import "../../../shared/styles/project.css";

export default function EditFactorScreen() {
     const { id } = useParams<{ id: string }>();
     const factorId = id ? Number(id) : null;
     const navigate = useNavigate();

     const { factor, loading } = useFactorDetail(factorId);
     const [submitting, setSubmitting] = useState(false);
     const [formData, setFormData] = useState<FactorFormData | null>(null);
     const [isValid, setIsValid] = useState(false);

     const handleFormChange = useCallback((data: FactorFormData, valid: boolean) => {
          setFormData(data);
          setIsValid(valid);
     }, []);

     const handleSave = async () => {
          if (!formData || !isValid || !factorId) return;

          setSubmitting(true);
          try {
               const fd = new FormData();
               if (formData.photoFile) fd.append("photo", formData.photoFile); // فقط اگر عکس جدید آپلود شده

               if (formData.invoice_number) fd.append("invoice_number", formData.invoice_number);
               if (formData.invoice_issue_at) fd.append("invoice_issue_at", formData.invoice_issue_at.toISOString());
               if (formData.amount) fd.append("amount", formData.amount.toString());
               if (formData.number_water_taps) fd.append("number_water_taps", formData.number_water_taps.toString());
               if (formData.number_connections) fd.append("number_connections", formData.number_connections.toString());
               if (formData.pipe_length) fd.append("pipe_length", formData.pipe_length.toString());
               if (formData.shop_name) fd.append("shop_name", formData.shop_name);
               if (formData.seller_phone) fd.append("seller_phone", convertPersianToEnglish(formData.seller_phone));
               if (formData.seller_address) fd.append("seller_address", formData.seller_address);

               await factorRepository.update(factorId, fd);
               MyNotification("", "فاکتور با موفقیت ویرایش شد", "success");
               navigate(FACTOR_ROUTES.list);
          } catch (err: unknown) {
               let msg = "خطا در ویرایش فاکتور";
               if (err instanceof Error) msg = err.message;
               MyNotification("خطا", msg, "error");
          } finally {
               setSubmitting(false);
          }
     };

     if (loading) return <div className="text-center mt-5">در حال بارگذاری...</div>;
     if (factor?.status !== "pending") return <div className="text-center mt-5">این فاکتور قابل ویرایش نیست.</div>;

     return (
          <>
               <Header title="ویرایش فاکتور" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <FactorForm initialData={factor} onChange={handleFormChange} />

               <div className="proj-sticky-bottom mb-4">
                    <button className="auth-btn" onClick={handleSave} disabled={submitting || !isValid}>
                         {submitting ? "در حال ذخیره..." : "ذخیره تغییرات"}
                    </button>
               </div>
          </>
     );
}