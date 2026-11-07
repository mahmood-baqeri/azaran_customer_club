import Header from "../../../app/layouts/header";
import {
     FaRegCalendarAlt,
     FaRegCheckCircle,
     FaRegUserCircle,
     FaGift,
     FaRegUser,
     FaRegCommentDots
} from 'react-icons/fa';
import "../../../shared/styles/notification-page.css"
import { NotificationGroupData, NotificationItemData } from "../interface/notification.types";
import { NotificationItem } from "../components/notifications.item";



// ==========================================
// داده‌های نمونه
// ==========================================
const timelineData: NotificationGroupData[] = [
     {
          id: 1,
          group: 'امروز',
          items: [
               {
                    id: 101,
                    title: 'چالش روز آماده است',
                    description: 'امروز هنوز بازی نکردی، برو سکه بگیر',
                    time: '1 ساعت پیش',
                    icon: <FaRegCalendarAlt />,
                    isUnread: true,
               },
               {
                    id: 102,
                    title: 'پروژه‌ی شما تایید شد',
                    description: 'پروژه‌ی ثبت شده تایید و ۵۰ امتیاز اضافه شد',
                    time: '۲ ساعت پیش',
                    icon: <FaRegCheckCircle />,
                    isUnread: true,
               }
          ]
     },
     {
          id: 2,
          group: 'قبل تر',
          items: [
               {
                    id: 201,
                    title: 'تبریک به سطح استاد کار رسیدید',
                    description: 'مزایای جدید برای شما فعال شد',
                    icon: <FaRegUserCircle />,
                    isUnread: false,
               }
               ,
               {
                    id: 301,
                    title: 'هدیه ی شما ارسال شد',
                    description: 'کد رهگیری مرسوله در بخش سفارش ها موجود است',
                    time: '۳ روز پیش',
                    icon: <FaGift />,
                    isUnread: false,
               },
               {
                    id: 302,
                    title: 'همکار معرفی شده پیوست',
                    description: 'رضا قوامی آبادی با کد معرف شما ثبت نام کرده است، ۴۵۰ امتیاز دریافت کردید',
                    time: '۴ روز پیش',
                    icon: <FaRegUser />,
                    isUnread: false,
               },
               {
                    id: 303,
                    title: 'پاسخ به سوال شما ثبت شد',
                    description: 'کارشناس فنی به پرسش از اهل فن شما جواب داد',
                    time: '۵ روز پیش',
                    icon: <FaRegCommentDots />,
                    isUnread: false,
               }
          ]
     }
];


export default function NotificationScreen() {
     return (
          <>
               <Header title="اعلان ها" showLogo={false} showBack={true} menuBg="f7f8fb" buttonBg="white" />

               <div className="">

                    {timelineData.map((group: NotificationGroupData) => (
                         <div key={group.id} className="mb-4">
                              {/* عنوان گروه */}
                              <div className="text-end mb-2 pe-1">
                                   <span className="color-primary fs-13">
                                        {group.group}
                                   </span>
                              </div>

                              {/* لیست اعلان‌های گروه */}
                              <div className="d-flex flex-column gap-2">
                                   {group.items.map((item: NotificationItemData) => (
                                        <NotificationItem key={item.id} item={item} />
                                   ))}
                              </div>
                         </div>
                    ))}

               </div>
          </>
     );
}
