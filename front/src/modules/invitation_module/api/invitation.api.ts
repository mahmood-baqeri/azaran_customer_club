// src/modules/invitation_module/api/invitation.api.ts

import { apiGET } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { ApiResponse, Invitation } from "../interface/invitation.types";

export const invitationApi = {
  list: (): Promise<ApiResponse<Invitation[]>> =>
    apiGET(`${BASE_URL}user/invitation/list/`, {}, true),
};