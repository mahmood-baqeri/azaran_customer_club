
// import MyImage from "../../../shared/components/image-show";
// import { ICONS } from "../../../shared/constants/icons";
import { NotificationItemProps } from "../interface/notification.types"

export const NotificationItem: React.FC<NotificationItemProps> = ({ item }) => {
     return (
          <div className={`notification-card d-flex align-items-start p-3 mb-2 rounded-4 ${item.isUnread ? 'bg-unread' : 'bg-read opacity-50 p-2'}`}>

               {/* بخش آیکون */}
               <div className="d-flex align-items-center gap-3 ms-2">
                    <div className="text-secondary fs-5 d-flex justify-content-center align-items-center">
                         {/* <MyImage src={ICONS.fire} def="/assets/none.png" alt="photo" width={10} /> */}
                    </div>
               </div>

               {/* بخش محتوا */}
               <div className="flex-grow-1 text-end pe-2">
                    <h6 className="fw-bold mb-1 text-dark fs-13 color-primary">{item.title}</h6>
                    <p className="text-muted mb-2 fs-11 mt-2">
                         {item.description}
                    </p>
                    {item.time && (
                         <p className="color-primary fs-10 text-start m-0">
                              {item.time}
                         </p>
                    )}
               </div>

               {/* بخش نشانگر */}
               <div className="d-flex align-items-center gap-3 ms-2">
                    {item.isUnread ? (
                         <span className="unread-dot bg-danger rounded-circle"></span>
                    ) : (
                         <span className="unread-dot-placeholder"></span>
                    )}
               </div>

          </div>
     );
};





