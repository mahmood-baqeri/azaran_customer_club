// front/src/modules/notifications_module/interface/notification.types.ts

export interface NotificationItemData {
     id: number;
     title: string;
     description: string;
     time?: string; // اختیاری است چون در برخی آیتم‌ها وجود ندارد
     icon: React.ReactNode;
     isUnread: boolean;
}

export interface NotificationGroupData {
     id: number;
     group: string;
     items: NotificationItemData[];
}

export interface NotificationItemProps {
     item: NotificationItemData;
}

