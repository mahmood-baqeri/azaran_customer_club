// src/modules/factor_module/components/FactorForm.tsx

import { useState, useEffect } from "react";
import { PersianDatePicker } from "../../../shared/utils/persianDatePicker";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import { DOMAIN } from "../../../shared/constants/env";
import type { Factor, FactorFormData } from "../interface/factor.types";

interface Props {
     initialData?: Factor | null;
     onChange: (data: FactorFormData, isValid: boolean) => void;
}

export default function FactorForm({ initialData, onChange }: Props) {
     const [invoiceNumber, setInvoiceNumber] = useState("");
     const [issueDate, setIssueDate] = useState<Date | null>(null);
     const [amount, setAmount] = useState("");
     const [waterTaps, setWaterTaps] = useState("");
     const [connections, setConnections] = useState("");
     const [pipeLength, setPipeLength] = useState("");
     const [shopName, setShopName] = useState("");
     const [sellerPhone, setSellerPhone] = useState("");
     const [sellerAddress, setSellerAddress] = useState("");

     const [photoFile, setPhotoFile] = useState<File | null>(null);
     const [photoPreview, setPhotoPreview] = useState<string | null>(null);

     // پر کردن فرم با دیتای اولیه در حالت ویرایش
     useEffect(() => {
          if (initialData) {
               setInvoiceNumber(initialData.invoice_number || "");
               setIssueDate(initialData.invoice_issue_at ? new Date(initialData.invoice_issue_at) : null);
               setAmount(initialData.amount?.toString() || "");
               setWaterTaps(initialData.meterage?.number_water_taps?.toString() || "");
               setConnections(initialData.meterage?.number_connections?.toString() || "");
               setPipeLength(initialData.meterage?.pipe_length?.toString() || "");
               setShopName(initialData.shop_name || "");
               setSellerPhone(initialData.seller?.phone || "");
               setSellerAddress(initialData.seller?.address || "");

               if (initialData.photo) {
                    setPhotoPreview(initialData.photo.startsWith("http") ? initialData.photo : `${DOMAIN}${initialData.photo}`);
               }
          }
     }, [initialData]);

     const isValid = !!photoFile || !!photoPreview; // عکس اجباری است

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
     }, [invoiceNumber, issueDate, amount, waterTaps, connections, pipeLength, shopName, sellerPhone, sellerAddress, photoFile, photoPreview, isValid, onChange]);

     const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
          const file = e.target.files?.[0];
          if (file) {
               setPhotoFile(file);
               setPhotoPreview(URL.createObjectURL(file));
          }
     };

     return (
          <div className="proj-body" style={{ paddingBottom: 100 }}>

               {/* بخش هدر تصویر */}
               <h3 className="proj-section-title mt-2">اطلاعات فاکتور</h3>

               <div style={{ position: "relative", marginBottom: 20 }}>
                    <label
                         style={{
                              display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                              height: 120, borderRadius: 12, border: "2px dashed #14306b",
                              color: "#14306b", fontWeight: 700, fontSize: 14, cursor: "pointer",
                              background: photoPreview ? "transparent" : "#f4f6fa",
                              overflow: "hidden"
                         }}
                    >
                         {photoPreview ? (
                              <img src={photoPreview} alt="Factor" style={{ width: "100%", height: "100%", objectFit: "cover", position: "absolute", inset: 0 }} />
                         ) : (
                              <>
                                   <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" /><circle cx="12" cy="13" r="4" /></svg>
                                   گرفتن عکس فاکتور
                              </>
                         )}
                         <input type="file" accept="image/*" onChange={handlePhotoChange} style={{ display: "none" }} />
                    </label>
               </div>

               <label className="proj-label">تاریخ صدور فاکتور</label>
               <PersianDatePicker value={issueDate} onChange={setIssueDate} placeholder="انتخاب تاریخ" />

               <div className="proj-row" style={{ marginTop: 16 }}>
                    <div className="proj-col">
                         <label className="proj-label">تعداد شیر</label>
                         <input type="number" className="proj-input" placeholder="0" value={waterTaps} onChange={e => setWaterTaps(e.target.value)} />
                    </div>
                    <div className="proj-col">
                         <label className="proj-label">تعداد اتصالات</label>
                         <input type="number" className="proj-input" placeholder="0" value={connections} onChange={e => setConnections(e.target.value)} />
                    </div>
                    <div className="proj-col">
                         <label className="proj-label">متراژ لوله</label>
                         <input type="number" className="proj-input" placeholder="0" value={pipeLength} onChange={e => setPipeLength(e.target.value)} />
                    </div>
               </div>

               <label className="proj-label">مبلغ فاکتور</label>
               <div style={{ position: "relative" }}>
                    <input
                         type="text"
                         className="proj-input"
                         placeholder="0"
                         value={amount}
                         onChange={e => setAmount(convertPersianToEnglish(e.target.value).replace(/\D/g, ""))}
                         style={{ textAlign: "left", paddingLeft: 50 }}
                    />
                    <span style={{ position: "absolute", left: 16, top: "50%", transform: "translateY(-50%)", color: "#a0aec0", fontSize: 12 }}>ریال</span>
               </div>

               <hr className="mt-4" />

               <h3 className="proj-section-title">اطلاعات فروشنده</h3>

               <label className="proj-label">نام فروشگاه</label>
               <input type="text" className="proj-input" placeholder="مثلا فروشگاه تاسیسات..." value={shopName} onChange={e => setShopName(e.target.value)} style={{ marginBottom: 16 }} />

               <label className="proj-label">تلفن فروشنده</label>
               <input type="tel" dir="ltr" className="proj-input" placeholder="021 0000 0000" value={sellerPhone} onChange={e => setSellerPhone(e.target.value)} style={{ marginBottom: 16 }} />

               <label className="proj-label">آدرس فروشنده</label>
               <input type="text" className="proj-input" placeholder="استان، شهر، خیابان، پلاک" value={sellerAddress} onChange={e => setSellerAddress(e.target.value)} />
          </div>
     );
}