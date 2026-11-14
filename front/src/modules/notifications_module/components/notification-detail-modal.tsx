// front/src/modules/notifications_module/components/notification-detail-modal.tsx

// import { useNavigate } from "react-router-dom";
import { FaTimes } from "react-icons/fa";
import { NotificationItemData } from "../interface/notification.types";
import { formatFullDateTime } from "../utils/notification-time";
import GlobalModal from "../../../shared/components/GlobalModal";
import { handel_photo_address } from "../../../shared/utils/handler";

interface Props {
     item: NotificationItemData | null;
     onClose: () => void;
     onDismiss: (item: NotificationItemData) => void;
}

export const NotificationDetailModal: React.FC<Props> = ({ item, onClose }) => {
     // const navigate = useNavigate();

     // ✅ وقتی item=null است، isOpen=false → GlobalModal به‌درستی unmount می‌کند
     const isOpen = item !== null;

     // const handleAction = () => {
     //      if (!item) return;
     //      const url = item.action_url;
     //      if (!url) return;
     //      if (/^https?:\/\//.test(url)) {
     //           window.location.href = url;
     //      } else {
     //           navigate(url);
     //      }
     //      onClose();
     // };

     // const handleDismiss = () => {
     //      if (!item) return;
     //      onDismiss(item);
     // };

     // const hasAction = !!(item?.action_url || item?.action_type);

     return (
          <GlobalModal isOpen={isOpen} onClose={onClose}>
               {item && (
                    <div dir="rtl" className="p-3">
                         {/* ─── Header: دکمه بستن ─── */}
                         <div className="d-flex justify-content-between align-items-center mb-3">
                              <div className="d-flex align-items-center gap-2">
                                   <span
                                        className={`badge rounded-pill fs-10 px-2 py-1 ${item.priority === "high"
                                             ? "bg-danger bg-opacity-10 text-danger"
                                             : "bg-primary bg-opacity-10 color-primary"
                                             }`}
                                   >
                                        {item.type_display}
                                   </span>
                                   {item.priority === "high" && (
                                        <span className="badge bg-warning bg-opacity-10 text-dark fs-10 px-2 py-1">
                                             فوری
                                        </span>
                                   )}
                              </div>

                              <button
                                   type="button"
                                   className="btn btn-sm btn-light rounded-circle d-flex align-items-center justify-content-center"
                                   onClick={onClose}
                                   aria-label="بستن"
                                   style={{ width: 32, height: 32, padding: 0 }}
                              >
                                   <FaTimes size={12} />
                              </button>
                         </div>

                         {/* ─── تصویر ─── */}
                         {item.image && (
                              <div className="mb-3 text-center">
                                   <img
                                        src={handel_photo_address(item.image)}
                                        alt=""
                                        className="rounded-3 w-100"
                                        style={{ maxHeight: 240, objectFit: "cover" }}
                                   />
                              </div>
                         )}

                         {/* ─── محتوا ─── */}
                         <h6 className="fw-bold fs-14 color-primary mb-2">{item.title}</h6>
                         <p
                              className="text-muted fs-12 mb-3"
                              style={{ whiteSpace: "pre-line", lineHeight: 1.9 }}
                         >
                              {item.body}
                         </p>

                         <p className="text-secondary fs-10 text-start m-0 mb-3">
                              {formatFullDateTime(item.sent_at ?? item.created_at)}
                         </p>

                         {/* ─── Footer ─── */}
                         {/* <div className="d-flex gap-2 justify-content-between pt-2 border-top"> */}
                         {/* <button
                                   type="button"
                                   className="btn btn-light rounded-3 fs-12 d-flex align-items-center gap-1"
                                   onClick={handleDismiss}
                              >
                                   <FaTrash size={11} />
                                   حذف از لیست
                              </button> */}

                         {/* {hasAction && (
                                   <button
                                        type="button"
                                        className="btn bg-primary text-white rounded-3 fs-12"
                                        onClick={handleAction}
                                   >
                                        مشاهده
                                   </button>
                              )} */}
                         {/* </div> */}
                    </div>
               )}
          </GlobalModal>
     );
};