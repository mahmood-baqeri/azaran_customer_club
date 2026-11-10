// src/modules/score_module/hooks/use-score.ts

import { useCallback, useEffect, useState } from "react";
import { scoreRepository } from "../repository/score.repository";
import type { BalanceInfo, FilterState, ScoreLog } from "../interface/score.types";

const formatDateToYYYYMMDD = (date: Date | null): string | undefined => {
  if (!date) return undefined;
  const offsetDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return offsetDate.toISOString().split("T")[0];
};

export const useScore = () => {
  const [balance, setBalance] = useState<BalanceInfo | null>(null);
  const [logs, setLogs] = useState<ScoreLog[]>([]);
  const [loading, setLoading] = useState(true);

  // ✅ استیت‌های صفحه‌بندی
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 7;

  // فیلترها
  const [filters, setFilters] = useState<FilterState>({
    direction: "all",
    startDate: null,
    endDate: null,
  });

  const fetchBalance = useCallback(async () => {
    try {
      setBalance(await scoreRepository.getBalance());
    } catch (err) {
      console.error("[score] balance failed:", err);
    }
  }, []);

  // ✅ اضافه شدن page به پارامترها
  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await scoreRepository.getLogs({
        direction: filters.direction === "all" ? undefined : filters.direction,
        start_date: formatDateToYYYYMMDD(filters.startDate),
        end_date: formatDateToYYYYMMDD(filters.endDate),
        page: page,             // ✅ ارسال شماره صفحه
        page_size: pageSize,    // ✅ ارسال تعداد در صفحه
      });
      if (res) {
        setLogs(res.items);
        setTotal(res.total);
      }
    } catch (err) {
      console.error("[score] logs failed:", err);
    } finally {
      setLoading(false);
    }
  }, [filters, page]); // ✅ page به dependencyها اضافه شد

  useEffect(() => {
    fetchBalance();
    fetchLogs();
  }, [fetchBalance, fetchLogs]);

  // ✅ اگر فیلتر عوض شد، برگرد به صفحه ۱
  const updateFilters = useCallback((newFilters: FilterState) => {
    setFilters(newFilters);
    setPage(1);
  }, []);

  const totalPages = Math.ceil(total / pageSize);

  return {
    balance,
    logs,
    loading,
    filters,
    setFilters: updateFilters,
    refresh: fetchLogs,
    // ✅ مقادیر صفحه‌بندی برای UI
    page,
    setPage,
    totalPages,
  };
};