// src/modules/project_module/screen/projects_list.screen.tsx

import { useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";
import Header from "../../../app/layouts/header";
import { useProjects } from "../hooks/use-projects";
import { projectRepository } from "../repository/project.repository";
import { MyNotification } from "../../../shared/utils/notification";
import { convertToJalaliDate } from "../../../shared/utils/date";
import { PROJECT_ROUTES } from "../routes";
import "../../../shared/styles/project.css";
import { DeleteModal } from "../../../shared/components/modal/deleteModal";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";

export default function ProjectsListScreen() {
     const navigate = useNavigate();
     const { projects, loading, refresh } = useProjects();

     // ✅ کدوم آیتم داره حذف میشه (برای "در حال حذف...")
     const [deletingId, setDeletingId] = useState<number | null>(null);
     // ✅ کدوم مودال بازه (null = هیچ‌کدام)
     const [deleteId, setDeleteId] = useState<number | null>(null);

     const approved = projects.filter(p => p.status === "approved").length;
     const pending = projects.filter(p => p.status === "pending").length;
     const rejected = projects.filter(p => p.status === "rejected").length;

     const allColleagues = Array.from(
          new Map(projects.flatMap(p => p.colleagues || []).map(c => [c.user_uuid, c])).values()
     );

     const handleDelete = async (id: number) => {
          setDeletingId(id);
          try {
               const success = await projectRepository.deleteProject(id);
               if (success) {
                    MyNotification("", "پروژه با موفقیت حذف شد", "success");
                    refresh();
               }
          } catch (err: unknown) {
               let msg = "خطا در حذف پروژه";
               if (axios.isAxiosError(err) && err.response?.data?.message) {
                    msg = err.response.data.message;
               }
               MyNotification("خطا", msg, "error");
          } finally {
               setDeletingId(null);
          }
     };

     if (loading) return <p className="text-center mt-5">در حال بارگذاری...</p>;

     return (
          <>
               <Header title="پروژه‌های من" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc"
                    action={
                         <a href={PROJECT_ROUTES.create} className="header-action-btn">
                              <span className="color-primary fs-14 fw-400 me-1">ثبت پروژه</span>
                         </a>
                    }
               />

               <div className="proj-body" style={{ paddingBottom: 40 }}>
                    {allColleagues.length > 0 && (
                         <div className="proj-summary-card">
                              <h3>همکاران من</h3>
                              <div className="avatars-row">
                                   {allColleagues.slice(0, 5).map(c => (
                                        <div key={c.user_uuid} className="avatar-item">
                                             <div className="avatar-circle">
                                                  <MyImage src={c.avatar} alt="user" def={ICONS.user_2} className="w__100" />
                                             </div>
                                             <span>{c.user_name}</span>
                                        </div>
                                   ))}
                              </div>
                         </div>
                    )}

                    <div className="proj-summary-card">
                         <h3>وضعیت پروژه</h3>
                         <div className="stats-row">
                              <div className="stat-box green"><span>{approved}</span><label>تایید شده</label></div>
                              <div className="stat-box yellow"><span>{pending}</span><label>در انتظار</label></div>
                              <div className="stat-box red"><span>{rejected}</span><label>رد شده</label></div>
                         </div>
                    </div>

                    <h3 className="proj-section-title" style={{ marginTop: 24 }}>لیست پروژه ها</h3>

                    <div className="proj-history-list">
                         {projects.map(p => {
                              const isEditable = p.status === 'pending';
                              const isDeletable = p.status === 'pending' || p.status === 'rejected';
                              const isDeleting = deletingId === p.id;

                              return (
                                   <div key={p.id} className="proj-history-card">
                                        <div className="ph-header">
                                             <span className="ph-title">{p.title}</span>
                                             <span className={`ph-status ${p.status}`}>{p.status_display}</span>
                                        </div>

                                        <div className="ph-footer">
                                             <span>#{p.id}</span>
                                             <span>{convertToJalaliDate(p.created_at ?? "")}</span>
                                        </div>

                                        <div className="ph-actions">
                                             <button
                                                  type="button"
                                                  className="ph-btn ph-btn-detail"
                                                  onClick={(e) => {
                                                       e.stopPropagation();
                                                       navigate(PROJECT_ROUTES.detail(p.id));
                                                  }}
                                             >
                                                  جزئیات
                                             </button>

                                             {isEditable && (
                                                  <button
                                                       type="button"
                                                       className="ph-btn ph-btn-edit"
                                                       onClick={(e) => {
                                                            e.stopPropagation();
                                                            navigate(PROJECT_ROUTES.edit(p.id));
                                                       }}
                                                  >
                                                       ویرایش
                                                  </button>
                                             )}

                                             {isDeletable && (
                                                  <button
                                                       type="button"
                                                       className="ph-btn ph-btn-delete"
                                                       disabled={isDeleting}
                                                       onClick={(e) => {
                                                            e.stopPropagation();
                                                            setDeleteId(p.id);   // ✅ باز کردن مودال
                                                       }}
                                                  >
                                                       {isDeleting ? 'در حال حذف...' : 'حذف'}
                                                  </button>
                                             )}
                                        </div>
                                   </div>
                              );
                         })}
                    </div>
               </div>

               {/* ✅ فقط یک مودال، بیرون از map */}
               <DeleteModal
                    isOpen={deleteId !== null}
                    id={deleteId ?? 0}
                    onClose={() => setDeleteId(null)}
                    onApply={handleDelete}
               />
          </>
     );
}