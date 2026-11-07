// src/modules/project_module/hooks/use-project-detail.ts
import { useCallback, useEffect, useState } from "react";
import { projectRepository } from "../repository/project.repository";
import type { Project } from "../interface/project.types";

export const useProjectDetail = (id: number | null) => {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setProject(await projectRepository.detail(id));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { project, loading, refresh, setProject };
};