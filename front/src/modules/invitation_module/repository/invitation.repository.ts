// src/modules/invitation_module/repository/invitation.repository.ts

import { invitationApi } from "../api/invitation.api";
import type { Invitation } from "../interface/invitation.types";

export const invitationRepository = {
  async list(): Promise<Invitation[]> {
    const res = await invitationApi.list();
    return Array.isArray(res.data) ? res.data : [];
  },
};