// src/modules/invitation_module/hooks/use-invitations.ts

import { useCallback, useEffect, useState } from "react";
import { invitationRepository } from "../repository/invitation.repository";
import type { Invitation } from "../interface/invitation.types";

export const useInvitations = () => {
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setInvitations(await invitationRepository.list());
    } catch (err) {
      console.error("[invitations] load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { invitations, loading, refresh };
};