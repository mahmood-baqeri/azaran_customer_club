import Header from "../../../app/layouts/header";
import { FaChevronLeft } from 'react-icons/fa';
import SliderSection from "../../settings_module/components/slider-section";
import "../../../shared/styles/home-page.css"
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import { GIFT_ROUTES } from "../../gift_module/routes";
import { PROMOTION_ROUTES } from "../../promotion_module/routes";
import { FAQ_ROUTES } from "../../faq_module/routes";
import { PROJECT_ROUTES } from "../../project_module/routes";
import { FACTOR_ROUTES } from "../../factor_module/routes";
import SupportModal from "../components/SupportModal";
import { useCallback, useMemo, useState } from "react";
import { GALLERY_ROUTES } from "../../gallery_module/routes";
import { VISIT_ROUTES } from "../../visit_module/routes";
import { REVIEW_ROUTES } from "../../review_module/routes";

export default function HomeScreen() {
     return (
          <>
               <Header />
               <div className="py-2">

                    <SliderSection />

                    <div className="py-3">
                         <TopActionCards />
                         <EarnPointsSection />
                         <GiftsSection />
                         <SupportSection />
                    </div>
               </div>
          </>
     );
}


// ==========================================
// ۱. کامپوننت باکس‌های بالایی (ثبت پروژه و چالش روز)
// ==========================================
const TopActionCards = () => {
     return (
          <>
               <div className="row g-3 mb-4 rtl">
                    {/* چالش روز */}
                    <div className="col-6">
                         <div className="action-card bg-warning text-dark h-90 p-3 rounded-4 d-flex flex-column justify-content-between">
                              <div className="d-flex justify-content-between align-items-start mb-2">
                                   <MyImage src={ICONS.calendar} def="/assets/none.png" alt="photo" width={30} />

                                   <div className="chalaneg-date">
                                        <MyImage src={ICONS.fire} def="/assets/none.png" alt="photo" width={10} />
                                        <span className="fs-10 me-2">5 روز پیاپی</span>
                                   </div>
                              </div>
                              <h6 className="fw-bold mb-2 fs-12">چالش روز</h6>
                              <p className="small mb-0 opacity-75 fs-11">هر روز امتیاز بگیر</p>
                         </div>
                    </div>

                    {/* ثبت پروژه */}
                    <div className="col-6">
                         <a href={PROJECT_ROUTES.list} className="action-card bg-warning text-dark h-90 p-3 rounded-4 d-flex flex-column justify-content-between">
                              <div className="d-flex justify-content-between align-items-start mb-2">
                                   <MyImage src={ICONS.project} def="/assets/none.png" alt="photo" width={30} />
                              </div>
                              <h6 className="fw-bold mb-2 fs-12">ثبت پروژه</h6>
                              <p className="small mb-0 opacity-75 fs-11 fw-400">پروژه‌ات را ثبت کن</p>
                         </a>
                    </div>
               </div>

          </>
     );
};

// ==========================================
// ۲. کامپوننت سکشن «کسب امتیاز»
// ==========================================
const EarnPointsSection = () => {
     const items = [
          { title: 'پرسش از اهل فن', icon: ICONS.question, bg: 'bg-light-blue', class: "img20_20", href: FAQ_ROUTES.list },
          { title: 'گالری مجریان', icon: ICONS.gallery, bg: 'bg-light-blue', class: "img20_20", href: GALLERY_ROUTES.list },
          { title: 'معرفی همکاران', icon: ICONS.user, bg: 'bg-light-blue', class: "img25_25", href: "" },
          { title: 'نظرسنجی', icon: ICONS.notebook, bg: 'bg-light-blue', class: "img20_20", href: "" },
          { title: 'ثبت فاکتور', icon: ICONS.notebook, bg: 'bg-light-blue', class: "img20_20", href: FACTOR_ROUTES.list },
          { title: ' بازدید کارخانه', icon: ICONS.notebook, bg: 'bg-light-blue', class: "img20_20", href: VISIT_ROUTES.list },
          { title: 'بازخورد', icon: ICONS.notebook, bg: 'bg-light-blue', class: "img20_20", href: REVIEW_ROUTES.main },
     ];

     return (
          <div className="mb-4 rtl ">
               <h6 className="fw-bold text-end mb-2 fs-15">کسب امتیاز</h6>
               <div className="bg-white rounded-4 p-3 shadow-sm">
                    <div className="row g-3">
                         {items.map((item, index) => (
                              <a className="col-6 fw-400" key={index} href={item.href}>
                                   <div className={`d-flex align-items-center justify-content-between p-3 rounded-3 ${item.bg}`}>
                                        <MyImage src={item.icon} def="/assets/none.png" alt="photo" className={item.class} />

                                        <span className="fs-11 color-primary">{item.title}</span>
                                   </div>
                              </a>
                         ))}
                    </div>
               </div>
          </div>
     );
};

// ==========================================
// ۳. کامپوننت سکشن «هدایا»
// ========================================== 
const GiftsSection = () => {
     return (
          <div className="mb-4 rtl">
               <div className="d-flex justify-content-between align-items-center mb-3">
                    <h6 className="fw-bold mb-0 fs-15">هدایا</h6>
                    <a href={GIFT_ROUTES.orders} className="text-decoration-none  d-flex align-items-center gap-1 fw-500 fs-12 color-primary">
                         <span> وضعیت سفارش</span>
                         <FaChevronLeft size={12} />
                    </a>
               </div>
               <div className="bg-white rounded-4 p-3 shadow-sm">
                    <div className="row g-3">
                         <div className="col-6">
                              <a href={GIFT_ROUTES.list} className="d-flex align-items-center justify-content-between p-3 rounded-3 bg-light-blue">
                                   <MyImage src={ICONS.gift} def="/assets/none.png" alt="photo" className="img20_20" />
                                   <span className="fs-12 fw-400 color-primary">ویترین هدایا</span>
                              </a>
                         </div>
                         <div className="col-6">
                              <a href={PROMOTION_ROUTES.list} className="d-flex align-items-center justify-content-between p-3 rounded-3 bg-light-blue">
                                   <MyImage src={ICONS.ads} def="/assets/none.png" alt="photo" className="img25_25" />
                                   <span className="fs-12 fw-400 color-primary">اقلام تبلیغاتی</span>
                              </a>
                         </div>
                    </div>
               </div>
          </div>
     );
};

// ==========================================
// ۴. کامپوننت سکشن «پشتیبانی»
// ==========================================
const SupportSection = () => {
     const [showGuideModal, setShowGuideModal] = useState(false);

     const openSupportChat = useCallback(() => {
          setShowGuideModal(true)
     }, []);

     const openGuide = useCallback(() => setShowGuideModal(true), []);

     const items = useMemo(
          () => [
               {
                    title: 'پشتیبانی',
                    icon: ICONS.support_2,
                    imgClass: 'img20_20',
                    onClick: openSupportChat,
               },
               {
                    title: 'راهنمای باشگاه',
                    icon: ICONS.help,
                    imgClass: 'img20_20',
                    onClick: openGuide,
               },
          ],
          [openSupportChat, openGuide],
     );

     return (
          <>
               <div className="mb-4">
                    <h6 className="fw-bold fs-15 mb-3">پشتیبانی</h6>
                    <div className="bg-white rounded-4 shadow-sm overflow-hidden">
                         {items.map((item, index) => (
                              <div
                                   key={item.title}
                                   role="button"
                                   tabIndex={0}
                                   className={`d-flex align-items-center justify-content-between p-3 ${index !== items.length - 1 ? 'border-bottom' : ''
                                        }`}
                                   style={{ cursor: 'pointer' }}
                                   onClick={item.onClick}
                                   onKeyDown={(e) => {
                                        if (e.key === 'Enter' || e.key === ' ') {
                                             e.preventDefault();
                                             item.onClick();
                                        }
                                   }}
                              >
                                   <div className="d-flex align-items-center gap-3">
                                        <MyImage
                                             src={item.icon}
                                             def="/assets/none.png"
                                             alt={item.title}
                                             className={item.imgClass}
                                        />
                                        <span className="fs-12 color-primary">{item.title}</span>
                                   </div>
                                   <FaChevronLeft className="text-muted" size={14} />
                              </div>
                         ))}
                    </div>
               </div>

               <SupportModal
                    isOpen={showGuideModal}
                    onClose={() => setShowGuideModal(false)}
               />
          </>
     );
};