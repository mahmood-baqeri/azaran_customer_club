// src/modules/project_module/screen/colleagues.screen.tsx

import { useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import Header from "../../../app/layouts/header";
import { useProjectDetail } from "../hooks/use-project-detail";
import { projectRepository } from "../repository/project.repository";
import { MyNotification } from "../../../shared/utils/notification";
import "../../../shared/styles/project.css";
import AddColleagueModal from "../components/AddColleagueModal";
import MyImage from "../../../shared/components/image-show";
import { ICONS } from "../../../shared/constants/icons";
// import ColleaguesModal from "../components/ColleaguesModal";

function extractErrorMessage(err: unknown, fallback: string): string {
     if (axios.isAxiosError(err)) {
          return err.response?.data?.message || err.message || fallback;
     }
     if (err instanceof Error) return err.message || fallback;
     if (typeof err === "object" && err !== null && "message" in err) {
          const m = (err as { message: unknown }).message;
          if (typeof m === "string") return m;
     }
     return fallback;
}

export default function ColleaguesScreen() {
     const { id } = useParams<{ id: string }>();
     const projectId = id ? Number(id) : null;
     const { project, loading, refresh } = useProjectDetail(projectId);
     const [showAddModal, setShowAddModal] = useState(false);

     if (loading || !project) return null;

     const colleagues = project.colleagues || [];
     const isLocked = project.status !== "pending";
     const totalPercent = colleagues
          .filter((c) => c.is_active)
          .reduce((sum, c) => sum + c.percent, 0);
     const remainingPercent = Math.max(0, 100 - totalPercent);

     const handleToggle = async (colleagueId: number) => {
          try {
               await projectRepository.toggleColleague(project.id, colleagueId);
               refresh();
          } catch (err) {
               MyNotification("خطا", extractErrorMessage(err, "خطا در تغییر وضعیت"), "error");
          }
     };

     const handleDelete = async (colleagueId: number) => {
          if (!window.confirm("آیا از حذف این همکار مطمئن هستید؟")) return;
          try {
               await projectRepository.deleteColleague(project.id, colleagueId);
               MyNotification("", "همکار حذف شد", "success");
               refresh();
          } catch (err) {
               MyNotification("خطا", extractErrorMessage(err, "خطا در حذف"), "error");
          }
     };

     return (
          <>
               <Header title="همکاران من پروژه" showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

               <div className="proj-body" style={{ paddingBottom: 100 }}>

                    <p className="fs-13">همکاران خود و درصد مشارکت آنها را وارد کنید.</p>

                    <div className="colleagues-list mt-4">
                         {colleagues.length === 0 ? (
                              <p className="colleagues-empty">
                                   هنوز همکاری اضافه نکرده‌اید.
                              </p>
                         ) : (
                              colleagues.map((c) => (
                                   <div key={c.id} className={`colleague-row mb-2 ${!c.is_active ? "disabled" : ""}`} >
                                        <div style={{ display: "flex", flexDirection: "column" }} >
                                             <span className="colleague-mobile" dir="ltr">
                                                  {c.user_mobile}
                                             </span>
                                             <span style={{ fontSize: 10, color: "#6b7794" }}>
                                                  {c.user_name}
                                             </span>
                                        </div>
                                        <div style={{ display: "flex", alignItems: "center", gap: 12, }}>
                                             <span className="fs-12" >
                                                  {c.percent}%
                                             </span>

                                             <label className="auth-switch" aria-label={`فعال/غیرفعال کردن ${c.user_name}`} >
                                                  <input type="checkbox" checked={c.is_active} onChange={() => !isLocked && handleToggle(c.id)} disabled={isLocked} />
                                                  <span className="slider" />
                                             </label>

                                             {!isLocked && (
                                                  <button
                                                       className="colleague-delete-btn"
                                                       onClick={() => handleDelete(c.id)}
                                                       aria-label={`حذف ${c.user_name}`}
                                                  >
                                                       <MyImage src={ICONS.trash} className="w__20 " />
                                                  </button>
                                             )}
                                        </div>
                                   </div>
                              ))
                         )}
                    </div>

                    {!isLocked ? (
                         <div className="proj-body mb-5">
                              <button
                                   className="proj-add-colleague-btn mb-3"
                                   onClick={() => setShowAddModal(true)}
                                   style={{ border: "1.5px dashed #14306b", color: "#14306b" }}
                              >
                                   <MyImage src={ICONS.user_add} className="w__20 " />

                                   <span className="mt-1"> افزودن همکاران</span>
                              </button>
                         </div>
                    ) : (
                         <p
                              style={{
                                   fontSize: 12,
                                   color: "#6b7794",
                                   textAlign: "center",
                                   marginBottom: 20,
                              }}
                         >
                              امکان ویرایش همکاران پس از تأیید پروژه وجود ندارد.
                         </p>
                    )}


                    <div className="colleagues-progress">
                         <div className="progress-labels">
                              <span>{totalPercent}%</span>
                              <span>{remainingPercent}%</span>
                         </div>
                         <div className="progress-bar">
                              <div
                                   className="progress-fill"
                                   style={{ width: `${Math.min(totalPercent, 100)}%` }}
                              />
                         </div>
                    </div>
               </div>

               <AddColleagueModal
                    isOpen={showAddModal}
                    onClose={() => setShowAddModal(false)}
                    projectId={project.id}
                    onAdded={refresh}
               />

               {/* <ColleaguesModal isOpen={showAddModal} onClose={() => setShowAddModal(false)} projectId={project.id} /> */}
          </>
     );
}