import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
import { convertToJalaliDate } from "../../../shared/utils/date";
import type { RequestVisit } from "../interface/visit.types";


export default function VisitTimeline({ visit }: { visit: RequestVisit }) {
     const isApproved = visit.status === "approved";
     const isPending = visit.status === "pending";
     const isRejected = visit.status === "rejected";

     const createdDate = convertToJalaliDate(visit.created_at ?? "");
     const approved_at = convertToJalaliDate(visit.approved_at ?? "");
     const rejected_at = convertToJalaliDate(visit.rejected_at ?? "");

     // تاریخ بررسی (اگر تایید یا رد شده بود، تاریخ تایید/رد را نشان میدهد، وگرنه همان تاریخ ثبت)
     const reviewDate = isApproved ? approved_at : isRejected ? rejected_at : createdDate;

     return (
          <div className="visit-timeline-card" dir="rtl">

               {/* === تایم‌لاین === */}
               <div className="vt-timeline-body">

                    {/* مرحله ۱: ثبت درخواست */}
                    <div className="vt-row">
                         <div className="vt-step">
                              <div className="vt-step-right">
                                   <div className="vt-icon active">
                                        <MyImage src={ICONS.verify} className="w__25" />
                                   </div>
                                   <div className="vt-line active" />
                              </div>
                              <div className="vt-step-left">
                                   <span className="vt-title">ثبت درخواست</span>
                                   <span className="vt-desc">درخواست ثبت شد</span>
                              </div>
                         </div>
                         <span className="vt-date">{createdDate}</span>
                    </div>

                    {/* مرحله ۲: بررسی درخواست */}
                    <div className="vt-row">
                         <div className="vt-step">
                              <div className="vt-step-right">
                                   <div className={`vt-icon ${isPending ? "" : "active"}`}>
                                        {isPending ? (
                                             <MyImage src={ICONS.pending} className="w__25" />
                                        ) : (
                                             <MyImage src={ICONS.verify} className="w__25" />
                                        )}
                                   </div>
                                   <div className={`vt-line ${!isPending ? "active" : "inactive"}`} />
                              </div>
                              <div className="vt-step-left">
                                   <span className="vt-title">بررسی درخواست</span>
                                   <span className="vt-desc">
                                        {isPending ? "در حال بررسی توسط آذر" : "درخواست توسط آذر بررسی شد"}
                                   </span>
                              </div>
                         </div>
                         {!isPending && <span className="vt-date">{reviewDate}</span>}
                    </div>

                    {/* مرحله ۳: نتیجه */}
                    <div className="vt-row">
                         <div className="vt-step">
                              <div className="vt-step-right">
                                   <div className={`vt-icon ${isApproved ? "active" : isRejected ? "rejected" : "inactive"}`}>
                                        {isApproved && <MyImage src={ICONS.verify} className="w__25" />}
                                        {isRejected && <MyImage src={ICONS.reject} className="w__25" />}
                                   </div>
                              </div>
                              <div className="vt-step-left">
                                   <span className={`vt-title ${isApproved ? "text-success" : isRejected ? "text-danger" : "text-muted"}`}>
                                        نتیجه
                                   </span>
                                   <span className="vt-desc">
                                        {isApproved ? "درخواست شما تایید شد" : isRejected ? "درخواست شما رد شد" : "در انتظار تایید"}
                                   </span>
                              </div>
                         </div>
                         {!isPending && (
                              <span className="vt-date">{isApproved ? approved_at : rejected_at}</span>
                         )}
                    </div>
               </div>

               {/* === پیام پایین صفحه === */}
               <div className={`vt-bottom-message status ${visit.status}`}>
                    {isApproved && (
                         <span>بازدید تایید شد <br /> <span className="fs-11 fw-400 text-dark opacity-75">زمان حضور و آدرس دقیق برای شما پیامک خواهد شد</span></span>
                    )}
                    {isRejected && (
                         <span>درخواست تایید نشد <br /> <span className="fs-11 fw-400 text-dark opacity-75">{visit.rejection_reason || "متأسفانه امکان تایید این درخواست وجود ندارد."}</span></span>
                    )}
                    {isPending && (
                         <span className="fs-11">درخواست در حال بررسی است. نتیجه همین جا نشان داده می‌شود. (زمان و نحوه اطلاع رسانی را اینجا می‌نویسیم)</span>
                    )}
               </div>

          </div>
     );
}