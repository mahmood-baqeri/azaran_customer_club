// src/modules/visit_module/components/VisitTimeline.tsx

import { convertToJalaliDate } from "../../../shared/utils/date";
import type { RequestVisit } from "../interface/visit.types";

export default function VisitCard({ visit }: { visit: RequestVisit }) {
     return (
          <>
               <div className="vsc-row">
                    <p className="m-0 fs-12 color-primary w-100 d-flex justify-content-between">
                         <span>شماره درخواست: {visit.id}</span>
                         <span className={`fs-11 status_visit status ${visit.status}`}>
                              {visit.status_display}
                         </span>
                    </p>
               </div>
               <div className="vsc-row color-primary fs-12">
                    <span>تاریخ بازدید:</span>
                    <span className="fs-11">دوشنبه : {convertToJalaliDate(visit.visit.date)}</span>
               </div>
               <div className="vsc-row color-primary fs-12">
                    <span>تعداد بازدید کننده:</span>
                    {visit.companion &&
                         <span className="fs-11">2نفر (شما و یک همراه)</span>
                    }
               </div>
          </>
     );
}