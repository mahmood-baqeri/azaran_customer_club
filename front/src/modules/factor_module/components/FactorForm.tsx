// src/modules/factor_module/components/FactorForm.tsx

import { useState, useEffect } from "react";
import { PersianDatePicker } from "../../../shared/utils/persianDatePicker";
import { DOMAIN } from "../../../shared/constants/env";
import type { Factor, FactorFormData } from "../interface/factor.types";
import { CurrencyInput } from "../../../shared/components/inputs/Currency";
import { NumberInput } from "../../../shared/components/inputs/Number";
import { PhoneInput } from "../../../shared/components/inputs/Phone";
import { TextInput } from "../../../shared/components/inputs/Text";
import { ImageUpload } from "../../../shared/components/inputs/Image";

interface Props {
     initialData?: Factor | null;
     onChange: (data: FactorFormData, isValid: boolean) => void;
}

export default function FactorForm({ initialData, onChange }: Props) {
     const [invoiceNumber, setInvoiceNumber] = useState("");
     const [issueDate, setIssueDate] = useState<Date | null>(null);
     const [amount, setAmount] = useState<number | null>(null);
     const [waterTaps, setWaterTaps] = useState<number | null>(null);
     const [connections, setConnections] = useState<number | null>(null);
     const [pipeLength, setPipeLength] = useState<number | null>(null);
     const [shopName, setShopName] = useState("");
     const [sellerPhone, setSellerPhone] = useState("");
     const [sellerAddress, setSellerAddress] = useState("");

     const [photoFile, setPhotoFile] = useState<File | null>(null);
     const [photoPreview, setPhotoPreview] = useState<string | null>(null);

     const [addressValid, setAddressValid] = useState(false);
     const [shopNameValid, setShopNameValid] = useState(false);
     const [amountValid, setAmountValid] = useState(false);

     // پر کردن فرم با دیتای اولیه در حالت ویرایش
     useEffect(() => {
          if (initialData) {
               setInvoiceNumber(initialData.invoice_number || "");
               setIssueDate(
                    initialData.invoice_issue_at
                         ? new Date(initialData.invoice_issue_at)
                         : null
               );
               setAmount(initialData.amount);
               setWaterTaps(initialData.meterage?.number_water_taps ?? null);
               setConnections(initialData.meterage?.number_connections ?? null);
               setPipeLength(initialData.meterage?.pipe_length ?? null);
               setShopName(initialData.shop_name || "");
               setSellerPhone(initialData.seller?.phone || "");
               setSellerAddress(initialData.seller?.address || "");

               if (initialData.photo) {
                    setPhotoPreview(
                         initialData.photo.startsWith("http")
                              ? initialData.photo
                              : `${DOMAIN}${initialData.photo}`
                    );
               }
          }
     }, [initialData]);

     /* --------------------------- اعتبار فرم --------------------------- */
     // ✅ همه‌ی فیلدهای اجباری باید معتبر باشند
     const hasPhoto = !!photoFile || !!photoPreview;
     const isValid =
          hasPhoto && amountValid && shopNameValid && addressValid;

     // ارسال تغییرات به کامپوننت والد
     useEffect(() => {
          onChange(
               {
                    invoice_number: invoiceNumber,
                    invoice_issue_at: issueDate,
                    amount,
                    number_water_taps: waterTaps,
                    number_connections: connections,
                    pipe_length: pipeLength,
                    shop_name: shopName,
                    seller_phone: sellerPhone,
                    seller_address: sellerAddress,
                    photoFile,
                    photoPreview,
               },
               isValid
          );
     }, [
          invoiceNumber,
          issueDate,
          amount,
          waterTaps,
          connections,
          pipeLength,
          shopName,
          sellerPhone,
          sellerAddress,
          photoFile,
          photoPreview,
          isValid,
          onChange,
     ]);

     return (
          <div className="proj-body">
               <h3 className="proj-section-title mt-2">اطلاعات فاکتور</h3>

               <div style={{ position: "relative", marginBottom: 20 }}>
                    <ImageUpload
                         value={photoFile}
                         // ✅ نمایش عکس موجود از سرور در حالت ویرایش
                         externalPreviewUrl={photoPreview}
                         onChange={(file) => {
                              setPhotoFile(file);
                              // ✅ وقتی کاربر عکس رو حذف می‌کنه، preview قدیمی هم پاک بشه
                              if (!file) setPhotoPreview(null);
                         }}
                         label="گرفتن عکس فاکتور"
                    />
               </div>

               <label className="proj-label">تاریخ صدور فاکتور</label>
               <PersianDatePicker
                    value={issueDate}
                    onChange={setIssueDate}
                    placeholder="انتخاب تاریخ"
               />

               <div className="proj-row" style={{ marginTop: 16 }}>
                    <div className="proj-col mb-1">
                         <label className="proj-label">تعداد شیر</label>
                         <NumberInput
                              value={waterTaps}
                              onChange={(v) => setWaterTaps(v)}
                              placeholder="0"
                              errorMessage="لطفاً یک عدد معتبر وارد کنید"
                              className="proj-input"
                         />
                    </div>
                    <div className="proj-col mb-1">
                         <label className="proj-label">تعداد اتصالات</label>
                         <NumberInput
                              value={connections}
                              onChange={(v) => setConnections(v)}
                              placeholder="0"
                              errorMessage="لطفاً یک عدد معتبر وارد کنید"
                              className="proj-input"
                         />
                    </div>
                    <div className="proj-col mb-1">
                         <label className="proj-label">متراژ لوله</label>
                         <NumberInput
                              value={pipeLength}
                              onChange={(v) => setPipeLength(v)}
                              placeholder="0"
                              errorMessage="لطفاً یک عدد معتبر وارد کنید"
                              className="proj-input"
                         />
                    </div>
               </div>

               <label className="proj-label mb-1">مبلغ فاکتور *</label>
               <div style={{ position: "relative" }}>
                    <CurrencyInput
                         value={amount}
                         onChange={(v) => setAmount(v)}
                         min={100000}
                         className="proj-input"
                         textAlign="center"
                         required
                         onValidityChange={setAmountValid}
                         errorMessage="مبلغ معتبر وارد کنید (حداقل ۱۰۰٬۰۰۰ ریال)"
                    />
               </div>

               <hr className="mt-3" />

               <h3 className="proj-section-title">اطلاعات فروشنده</h3>

               <label className="proj-label mb-1">نام فروشگاه *</label>
               <TextInput
                    value={shopName}
                    onChange={setShopName}
                    minLength={3}
                    maxLength={200}
                    className="proj-input"
                    onValidityChange={setShopNameValid}
                    required
                    placeholder="مثلا فروشگاه تاسیسات..."
                    errorMessage="نام فروشگاه باید بین ۳ تا ۲۰۰ کاراکتر باشد"
               />

               <label className="proj-label mt-3 mb-1">تلفن فروشنده</label>
               <PhoneInput
                    value={sellerPhone}
                    onChange={(raw) => setSellerPhone(raw)}
                    placeholder="021 1234 5678"
                    className="proj-input"
               />

               <label className="proj-label mt-3 mb-1">آدرس فروشنده *</label>
               <TextInput
                    value={sellerAddress}
                    onChange={setSellerAddress}
                    minLength={10}
                    maxLength={200}
                    className="proj-input"
                    onValidityChange={setAddressValid}
                    required
                    placeholder="استان، شهر، خیابان، کوچه، پلاک"
                    errorMessage="آدرس باید بین ۱۰ تا ۲۰۰ کاراکتر باشد"
               />
          </div>
     );
}