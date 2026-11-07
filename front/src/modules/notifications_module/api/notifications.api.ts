import { apiGET } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";

export const notificationsApi = {
  unreadCount: () =>
    apiGET(`${BASE_URL}notifications/not-seen/`, {}, true) as Promise<{
      count: number;
    }>,
};