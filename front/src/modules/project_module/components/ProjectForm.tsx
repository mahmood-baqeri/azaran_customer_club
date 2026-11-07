// src/modules/project_module/components/ProjectForm.tsx

import { useState, useEffect } from "react";
import type { ProjectType, Project } from "../interface/project.types";
import { PersianDatePicker } from "../../../shared/utils/persianDatePicker";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import { PhoneInput } from "../../../shared/components/inputs/Phone";
import TextInput from "../../../shared/components/inputs/Text";
import NumberInput from "../../../shared/components/inputs/Number";

export interface ProjectFormData {
     type: ProjectType;
     unit_count: number | null;
     address: string;
     owner_mobile: string;
     completion_at: Date | null;
     number_water_taps: number | null;
     number_gas_taps: number | null;
     number_connections: number | null;
     pipe_length: number | null;
}

interface Props {
     initialData?: Project | null;
     onChange: (data: ProjectFormData, isValid: boolean) => void;
}

export default function ProjectForm({ initialData, onChange }: Props) {
     const [type, setType] = useState<ProjectType>("water");
     const [unitCount, setUnitCount] = useState<number | null>(null);;
     const [address, setAddress] = useState("");
     const [ownerMobile, setOwnerMobile] = useState("");
     const [completionDate, setCompletionDate] = useState<Date | null>(null);
     const [waterTaps, setWaterTaps] = useState<number | null>(null);;
     const [gasTaps, setGasTaps] = useState<number | null>(null);
     const [connections, setConnections] = useState<number | null>(null);;
     const [pipeLength, setPipeLength] = useState<number | null>(null);;

     const [validMobile, setValidMobile] = useState(false);
     const [unitValid, setUnitValid] = useState(false);
     const [adressValid, setAddressValid] = useState(false);

     // پر کردن فرم با دیتای اولیه (در حالت ویرایش یا رفرش)
     useEffect(() => {
          if (initialData) {
               setType((initialData.type as ProjectType) || "water");
               setUnitCount(initialData.unit_count || 0);
               setAddress(initialData.address || "");
               setOwnerMobile(initialData.owner_mobile || "");
               setCompletionDate(initialData.completion_at ? new Date(initialData.completion_at) : null);
               setWaterTaps(initialData.meterage?.number_water_taps || 0);
               setGasTaps(initialData.meterage?.number_gas_taps || 0);
               setConnections(initialData.meterage?.number_connections || 0);
               setPipeLength(initialData.meterage?.pipe_length || 0);
          }
     }, [initialData]);

     const isValid = address.trim().length > 3 && !!completionDate && validMobile && unitValid && adressValid;

     // ارسال تغییرات به کامپوننت والد
     useEffect(() => {
          onChange(
               {
                    type,
                    unit_count: unitCount,
                    address,
                    owner_mobile: ownerMobile,
                    completion_at: completionDate,
                    number_water_taps: waterTaps,
                    number_gas_taps: gasTaps,
                    number_connections: connections,
                    pipe_length: pipeLength,
               },
               isValid
          );
     }, [type, unitCount, address, ownerMobile, completionDate, waterTaps, gasTaps, connections, pipeLength, isValid, onChange]);

     return (
          <div className="proj-body">
               <h3 className="proj-section-title mt-2">نوع پروژه</h3>
               <div className="proj-segment mb-3">
                    <button
                         type="button"
                         className={`proj-seg-btn ${type === "water" ? "active" : ""}`}
                         onClick={() => setType("water")}
                    >
                         <MyImage src={type === "water" ? ICONS.water_2 : ICONS.water_1} alt="آبی" className="w__10" />
                         <span className="me-1">آبی</span>
                    </button>
                    <button
                         type="button"
                         className={`proj-seg-btn ${type === "gas" ? "active" : ""}`}
                         onClick={() => setType("gas")}
                    >
                         <MyImage src={type === "gas" ? ICONS.gas_2 : ICONS.gas_1} alt="گازی" className="w__10" />
                         <span className="me-1">گازی</span>
                    </button>
               </div>

               <hr />

               <h3 className="proj-section-title mt-3">مشخصات محل پروژه</h3>
               <div className="row mb-3">
                    <div className="col-7 px-2">
                         <label className="proj-label">تاریخ اتمام پروژه</label>
                         <PersianDatePicker value={completionDate} onChange={setCompletionDate} placeholder="انتخاب تاریخ" />
                    </div>
                    <div className="col-5 px-2">
                         <label className="proj-label">تعداد واحد</label>
                         <NumberInput
                              value={unitCount}
                              onChange={(v) => setUnitCount(v)}
                              placeholder="0"
                              errorMessage="لطفاً یک عدد معتبر وارد کنید"
                              className="proj-input"
                              onValidityChange={setUnitValid}
                              max={100}
                         />
                    </div>
               </div>

               <label className="proj-label">آدرس محل اجرا</label>
               <TextInput
                    value={address}
                    onChange={setAddress}
                    minLength={10}
                    maxLength={200}
                    className="proj-input"
                    onValidityChange={setAddressValid}
                    required
                    placeholder="استان، شهر، خیایان، کوچه، پلاک"
                    errorMessage="آدرس  باید بین 10 تا 200 کاراکتر باشد"
               />

               <label className="proj-label mt-1">تلفن مالک/پیمانکار</label>
               <PhoneInput
                    value={ownerMobile}
                    className="proj-input"
                    onValidityChange={setValidMobile}
                    onChange={(raw) => setOwnerMobile(raw)}
                    errorMessage="شماره باید با ۰۹ شروع شده و ۱۱ رقم باشد"
               />

               <hr className="mt-3" />

               <h3 className="proj-section-title">محصولات آذر استفاده شده</h3>
               <div className="row mb-3">
                    {type === "water" ? (
                         <>
                              <div className="col-4">
                                   <label className="proj-label">تعداد شیرآبی</label>
                                   <NumberInput
                                        value={waterTaps}
                                        onChange={(v) => setWaterTaps(v)}
                                        placeholder="0"
                                        errorMessage="لطفاً یک عدد معتبر وارد کنید"
                                        className="proj-input"
                                   />
                              </div>
                              <div className="col-4">
                                   <label className="proj-label">تعداد اتصالات</label>
                                   <NumberInput
                                        value={connections}
                                        onChange={(v) => setConnections(v)}
                                        placeholder="0"
                                        errorMessage="لطفاً یک عدد معتبر وارد کنید"
                                        className="proj-input"
                                   />
                              </div>
                              <div className="col-4">
                                   <label className="proj-label">متراژ لوله</label>
                                   <NumberInput
                                        value={pipeLength}
                                        onChange={(v) => setPipeLength(v)}
                                        placeholder="0"
                                        errorMessage="لطفاً یک عدد معتبر وارد کنید"
                                        className="proj-input"
                                   />
                              </div>
                         </>
                    ) : (
                         <>
                              <div className="col-4"></div>
                              <div className="col-4">
                                   <label className="proj-label">تعداد شیرگازی</label>
                                   <NumberInput
                                        value={gasTaps}
                                        onChange={(v) => setGasTaps(v)}
                                        placeholder="0"
                                        errorMessage="لطفاً یک عدد معتبر وارد کنید"
                                        className="proj-input"
                                   />
                              </div>
                         </>
                    )}

               </div>
               <hr />
          </div>
     );
}