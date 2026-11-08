// src/modules/support_module/hooks/use-tickets.ts

import { useCallback, useEffect, useState } from "react";
import { supportRepository } from "../repository/support.repository";
import type { SupportTicket } from "../interface/support.types";

export const useTickets = () => {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setTickets(await supportRepository.listTickets());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { tickets, loading, refresh };
};