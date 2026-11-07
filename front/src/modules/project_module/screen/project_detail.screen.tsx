// src/modules/project_module/screen/project_detail.screen.tsx

import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useProjectDetail } from "../hooks/use-project-detail";
import ColleaguesModal from "../components/ColleaguesModal";
import { PROJECT_ROUTES } from "../routes";
import { convertToJalaliDate } from "../../../shared/utils/date";
import "../../../shared/styles/project.css";

const UPLOAD_TYPES = [
     { key: "exterior_view_building" as const, title: "نمای خارجی ساختمان" },
     { key: "azar_products_installed" as const, title: "محصولات آذر نصب شده" },
     { key: "azar_products_depot" as const, title: "دپو محصولات آذر قبل از نصب" },
];

export default function ProjectDetailScreen() {
     const { id } = useParams<{ id: string }>();
     const projectId = id ? Number(id) : null;
     const navigate = useNavigate();

     const { project, loading } = useProjectDetail(projectId);
     const [showColleagues, setShowColleagues] = useState(false);

     if (loading || !project) return null;

     const attachments = project.attachments || [];
     const uploadedTypes = attachments.map((a) => a.type);
     const missingBasic = UPLOAD_TYPES.filter((t) => !uploadedTypes.includes(t.key)).length;

     const isPending = project.status === "pending";

     return (
          <>
               <Header title="جزئیات پروژه" showBack showLogo={false} menuBg="f7f8fb" />

               <div className="proj-body" style={{ paddingBottom: 100 }}>
                    <div className="proj-summary-card">
                         <h3>اطلاعات پروژه</h3>
                         <div style={{ fontSize: 12, color: "#6b7794", lineHeight: 2 }}>
                              <div>
                                   نوع: <strong>{project.type_display}</strong>
                              </div>
                              <div>
                                   تاریخ ثبت: <strong>{convertToJalaliDate(project.created_at ?? "")}</strong>
                              </div>
                              <div>
                                   وضعیت: <strong>{project.status_display}</strong>
                              </div>
                         </div>
                    </div>

                    <button
                         className="proj-add-colleague-btn"
                         onClick={() => setShowColleagues(true)}
                    >
                         مدیریت همکاران پروژه ({project.colleagues?.length || 0} نفر)
                    </button>

                    {isPending && (
                         <button
                              className="auth-btn"
                              style={{ marginTop: 16 }}
                              onClick={() =>
                                   navigate(PROJECT_ROUTES.upload(project.id))
                              }
                         >
                              ادامه و بارگذاری تصاویر
                              {missingBasic > 0 && ` (${missingBasic} تصویر باقی‌مانده)`}
                         </button>
                    )}
               </div>

               <ColleaguesModal
                    isOpen={showColleagues}
                    onClose={() => setShowColleagues(false)}
                    projectId={project.id}
               />
          </>
     );
}