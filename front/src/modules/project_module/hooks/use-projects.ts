// src/modules/project_module/hooks/use-projects.ts
import { useCallback, useEffect, useState } from "react";
import { projectRepository } from "../repository/project.repository";
import type { Project } from "../interface/project.types";

export const useProjects = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setProjects(await projectRepository.list());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { projects, loading, refresh };
};