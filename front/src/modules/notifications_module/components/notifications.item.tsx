// front/src/modules/notifications_module/components/notifications.item.tsx

import {
     FaRegCalendarAlt,
     FaRegCheckCircle,
     FaRegUserCircle,
     FaGift,
     FaRegCommentDots,
     FaBullhorn,
     FaFileInvoice,
     FaInfoCircle,
     FaBell,
} from "react-icons/fa";
import { NotificationItemProps, NotificationType } from "../interface/notification.types";
import { timeAgo } from "../utils/notification-time";
import { handel_photo_address } from "../../../shared/utils/handler";

const ICONS_BY_TYPE: Record<NotificationType, React.ReactNode> = {
     system: <FaInfoCircle />,
     promotion: <FaBullhorn />,
     gift: <FaGift />,
     project: <FaRegCheckCircle />,
     factor: <FaFileInvoice />,
     support: <FaRegCommentDots />,
     account: <FaRegUserCircle />,
     review: <FaRegCommentDots />,
     visit: <FaRegCalendarAlt />,
     other: <FaBell />,
};

export const NotificationItem: React.FC<NotificationItemProps> = ({ item, onOpen }) => {
     const isUnread = !item.is_read;
     const time = timeAgo(item.sent_at ?? item.created_at);

     return (
          <div
               className={`notification-card d-flex align-items-start p-3 mb-2 rounded-4 ${isUnread ? "bg-unread" : "bg-read opacity-50 p-2"
                    }`}
               onClick={() => onOpen(item)}
               role="button"
               style={{ cursor: "pointer" }}
          >
               {/* آیکون یا تصویر */}
               <div className="d-flex align-items-center gap-3 ms-2">
                    <div className="text-secondary fs-5 d-flex justify-content-center align-items-center">
                         {item.image ? (
                              <img
                                   src={handel_photo_address(item.image)}
                                   alt=""
                                   className="rounded-3"
                                   style={{ width: 40, height: 40, objectFit: "cover" }}
                              />
                         ) : (
                              ICONS_BY_TYPE[item.type] ?? <FaBell />
                         )}
                    </div>
               </div>

               {/* محتوا */}
               <div className="flex-grow-1 text-end pe-2">
                    <h6 className="fw-bold mb-1 text-dark fs-13 color-primary">{item.title}</h6>
                    <p
                         className="text-muted mb-2 fs-11 mt-2"
                         style={{
                              display: "-webkit-box",
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: "vertical",
                              overflow: "hidden",
                              whiteSpace: "pre-line",
                         }}
                    >
                         {item.body}
                    </p>
                    {time && <p className="color-primary fs-10 text-start m-0">{time}</p>}
               </div>

               {/* نشانگر خوانده/نخوانده */}
               <div className="d-flex align-items-center gap-3 ms-2">
                    {isUnread ? (
                         <span className="unread-dot bg-danger rounded-circle" />
                    ) : (
                         <span className="unread-dot-placeholder" />
                    )}
               </div>
          </div>
     );
};