// src/modules/auth_module/screens/register.screen.tsx

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../hooks/use-auth";
import { AUTH_ROUTES } from "../routes";
import { convertPersianToEnglish } from "../../../shared/utils/slug";
import { MyNotification } from "../../../shared/utils/notification";
import {
     IconUser,
     IconStore,
     IconLock,
     IconEye,
     IconEyeOff,
     IconLoader,
} from "../../../shared/components/AuthIcons";
import SelectElement, { type Option } from "../../../shared/tools/select";
import { useCities, useProvinces } from "../../settings_module/hooks/use-locations";
import "../../../shared/styles/AuthTemplate.css";
import "../../../shared/styles/react-select.css";
import AuthFootbar from "../components/auth-footbar";
import AuthTopbar from "../components/auth-topbar";

type Nature = "executive" | "seller";

export default function RegisterScreen() {
     const { register } = useAuth();


     const { provinces, loading: provincesLoading } = useProvinces();

     const [nature, setNature] = useState<Nature>("executive");
     const [firstName, setFirstName] = useState("");
     const [lastName, setLastName] = useState("");
     const [password, setPassword] = useState("");
     const [showPass, setShowPass] = useState(false);
     const [hasReferral, setHasReferral] = useState(false);
     const [referralCode, setReferralCode] = useState("");
     const [selectedProvince, setSelectedProvince] = useState<Option | null>(null);
     const [selectedCity, setSelectedCity] = useState<Option | null>(null);
     const [address, setAddress] = useState("");
     const [postalCode, setPostalCode] = useState("");
     const [loading, setLoading] = useState(false);

     // استان انتخاب‌شده → fetch شهرها
     const provinceId = selectedProvince ? Number(selectedProvince.value) : null;
     const { cities, loading: citiesLoading } = useCities(provinceId);

     const provinceOptions: Option[] = useMemo(
          () => provinces.map((p) => ({ label: p.name, value: p.id })),
          [provinces]
     );

     const cityOptions: Option[] = useMemo(
          () => cities.map((c) => ({ label: c.name, value: c.id })),
          [cities]
     );

     const addressSectionTitle = nature === "seller" ? "آدرس فروشگاه" : "آدرس";
     const addressPlaceholder =
          nature === "seller"
               ? "خیابان، کوچه، پلاک فروشگاه"
               : "خیابان، کوچه، پلاک، واحد";

     const cleanPostal = useMemo(
          () => convertPersianToEnglish(postalCode).replace(/\D/g, ""),
          [postalCode]
     );

     // هنگام تغییر استان، شهر را ریست کن
     useEffect(() => {
          setSelectedCity(null);
     }, [provinceId]);

     const isFirstNameValid = firstName.trim().length > 1;
     const isLastNameValid = lastName.trim().length > 1;
     const isPasswordValid = password.length >= 6;
     const isProvinceValid = !!selectedProvince;
     const isCityValid = !!selectedCity;
     const isAddressValid = address.trim().length >= 5;
     const isPostalValid = cleanPostal.length === 10;
     const isReferralValid = !hasReferral || referralCode.trim().length > 0;

     const canSubmit =
          isFirstNameValid &&
          isLastNameValid &&
          isPasswordValid &&
          isProvinceValid &&
          isCityValid &&
          isAddressValid &&
          isPostalValid &&
          isReferralValid &&
          !loading;

     const handleSubmit = async (e: React.FormEvent) => {
          e.preventDefault();
          if (!canSubmit) {
               MyNotification("اخطار ! ", "لطفاً همه فیلدها را کامل کنید", "error");
               return;
          }
          setLoading(true);
          try {
               await register({
                    first_name: firstName.trim(),
                    last_name: lastName.trim(),
                    nature,
                    password,
                    referral_code: hasReferral ? referralCode.trim() : undefined,
                    province_id: selectedProvince ? Number(selectedProvince.value) : null,
                    city_id: selectedCity ? Number(selectedCity.value) : null,
                    address: address.trim(),
                    postal_code: cleanPostal,
               });
          } finally {
               setLoading(false);
          }
     };

     return (
          <div className="auth-root">
               <div className="auth-shell">

                    <AuthTopbar backTo={AUTH_ROUTES.login} title="تکمیل ثبت‌نام" />

                    <div className="auth-body" style={{ paddingTop: 0 }}>

                         <form onSubmit={handleSubmit}>

                              <div className="auth-section-title">اطلاعات اصلی</div>

                              <div className="auth-form-row cols-2">
                                   <div>
                                        <div className="auth-label" style={{ fontSize: 12 }}>نام</div>
                                        <div className="auth-field" style={{ marginBottom: 0 }}>
                                             <input
                                                  type="text"
                                                  value={firstName}
                                                  onChange={(e) => setFirstName(e.target.value)}
                                                  style={{ paddingLeft: 16, paddingRight: 16 }}
                                             />
                                        </div>
                                   </div>
                                   <div>
                                        <div className="auth-label" style={{ fontSize: 12 }}>نام خانوادگی</div>
                                        <div className="auth-field" style={{ marginBottom: 0 }}>
                                             <input
                                                  type="text"
                                                  value={lastName}
                                                  onChange={(e) => setLastName(e.target.value)}
                                                  style={{ paddingLeft: 16, paddingRight: 16 }}
                                             />
                                        </div>
                                   </div>
                              </div>

                              <div style={{ marginTop: 14 }}>
                                   <div className="auth-label" style={{ fontSize: 12 }}>نوع فعالیت</div>
                                   <div className="auth-form-row cols-2" style={{ marginBottom: 0 }}>
                                        <button
                                             type="button"
                                             className={`auth-segment-btn ${nature === "executive" ? "active" : ""}`}
                                             onClick={() => setNature("executive")}
                                        >
                                             <IconUser size={16} />
                                             مجری
                                        </button>
                                        <button
                                             type="button"
                                             className={`auth-segment-btn ${nature === "seller" ? "active" : ""}`}
                                             onClick={() => setNature("seller")}
                                        >
                                             <IconStore size={16} />
                                             فروشنده
                                        </button>
                                   </div>
                              </div>

                              <div style={{ marginTop: 14 }}>
                                   <div className="auth-label" style={{ fontSize: 12 }}>رمز عبور</div>
                                   <div className="auth-field" style={{ marginBottom: 0 }}>
                                        <input
                                             type={showPass ? "password" : "text"}
                                             value={password}
                                             onChange={(e) => setPassword(e.target.value)}
                                             placeholder="یک رمز عبور تعیین کنید"
                                             style={{ paddingRight: 46, paddingLeft: 46, textAlign: "left" }}
                                        />
                                        <div className="auth-field-icon">
                                             <IconLock />
                                        </div>
                                        <div
                                             className="auth-field-icon clickable"
                                             style={{ left: "auto", right: 14 }}
                                             onClick={() => setShowPass((s) => !s)}
                                        >
                                             {showPass ? <IconEyeOff /> : <IconEye />}
                                        </div>
                                   </div>
                              </div>

                              <div className="auth-checkbox-row" style={{ marginTop: 12 }}>
                                   <span>کد معرف دارم</span>
                                   <label className="auth-switch">
                                        <input
                                             type="checkbox"
                                             checked={hasReferral}
                                             onChange={(e) => setHasReferral(e.target.checked)}
                                        />
                                        <span className="slider" />
                                   </label>
                              </div>

                              {hasReferral && (
                                   <div className="auth-field">
                                        <input
                                             type="text"
                                             value={referralCode}
                                             onChange={(e) => setReferralCode(e.target.value)}
                                             placeholder="کد معرف"
                                             style={{ paddingLeft: 16, paddingRight: 16 }}
                                        />
                                   </div>
                              )}

                              <div className="auth-section-title">{addressSectionTitle}</div>

                              <div className="auth-form-row cols-2">
                                   <div>
                                        <div className="auth-label" style={{ fontSize: 12 }}>استان</div>
                                        <SelectElement
                                             options={provinceOptions}
                                             value={selectedProvince}
                                             onChange={setSelectedProvince}
                                             placeholder="انتخاب کنید"
                                             isLoading={provincesLoading}
                                             isSearchable
                                        />
                                   </div>
                                   <div>
                                        <div className="auth-label" style={{ fontSize: 12 }}>شهر</div>
                                        <SelectElement
                                             options={cityOptions}
                                             value={selectedCity}
                                             onChange={setSelectedCity}
                                             placeholder="انتخاب کنید"
                                             isLoading={citiesLoading}
                                             isDisabled={!provinceId}
                                             isSearchable
                                        />
                                   </div>
                              </div>

                              <div style={{ marginTop: 12 }}>
                                   <div className="auth-label" style={{ fontSize: 12 }}>نشانی</div>
                                   <textarea
                                        className="auth-textarea"
                                        value={address}
                                        onChange={(e) => setAddress(e.target.value)}
                                        placeholder={addressPlaceholder}
                                   />
                              </div>

                              <div style={{ marginTop: 12 }}>
                                   <div className="auth-label" style={{ fontSize: 12 }}>کد پستی</div>
                                   <div className="auth-field" style={{ marginBottom: 0 }}>
                                        <input
                                             type="text"
                                             inputMode="numeric"
                                             value={postalCode}
                                             onChange={(e) => setPostalCode(e.target.value)}
                                             placeholder="۱۰ رقم"
                                             maxLength={10}
                                             dir="ltr"
                                             style={{ textAlign: "left", paddingRight: 16, paddingLeft: 16 }}
                                        />
                                   </div>
                              </div>

                              <button
                                   type="submit"
                                   className="auth-btn"
                                   style={{ marginTop: 22 }}
                                   disabled={!canSubmit}
                              >
                                   {loading ? (
                                        <>
                                             <IconLoader size={20} />
                                             <span>در حال ثبت...</span>
                                        </>
                                   ) : (
                                        <span>ثبت نام</span>
                                   )}
                              </button>
                         </form>
                    </div>

                    <AuthFootbar />

               </div>
          </div>
     );
}