// src/modules/project_module/repository/project.repository.ts

import { projectApi } from "../api/project.api";
import type { Project, CreateProjectPayload, Colleague, Attachment, AttachmentType } from "../interface/project.types";

export const projectRepository = {
  async create(payload: CreateProjectPayload): Promise<Project | null> {
    const res = await projectApi.create(payload);
    return res.data ?? null;
  },
  
  async update(id: number, payload: CreateProjectPayload): Promise<Project | null> {
    const res = await projectApi.update(id, payload);
    return res.data ?? null;
  },

  async list(): Promise<Project[]> {
    const res = await projectApi.list();
    return Array.isArray(res.data) ? res.data : [];
  },

  async detail(id: number): Promise<Project | null> {
    const res = await projectApi.detail(id);
    return res.data ?? null;
  },


  async uploadAttachment(projectId: number, type: AttachmentType, file: File): Promise<Attachment | null> {
    const res = await projectApi.uploadAttachment(projectId, type, file);
    return res.data ?? null;
  },

  
  async addColleague(projectId: number, mobile: string, percent: number): Promise<Colleague | null> {
    const res = await projectApi.addColleague(projectId, mobile, percent);
    // ✅ اگر بک‌اند خطای منطقی برگرداند (حتی با کد 203)، پرتاب خطا می‌کنیم
    if (res.status === "Error") {
      throw new Error(res.message);
    }
    return res.data ?? null;
  },

  async toggleColleague(projectId: number, colleagueId: number): Promise<Colleague | null> {
    const res = await projectApi.toggleColleague(projectId, colleagueId);
    if (res.status === "Error") {
      throw new Error(res.message);
    }
    return res.data ?? null;
  },

  async deleteColleague(projectId: number, colleagueId: number): Promise<boolean> {
    const res = await projectApi.deleteColleague(projectId, colleagueId);
    if (res.status === "Error") {
      throw new Error(res.message);
    }
    return res.status === "Success";
  },

  // همین کار را برای حذف پروژه و پیوست‌ها نیز انجام دهید:
  async deleteProject(id: number): Promise<boolean> {
    const res = await projectApi.deleteProject(id);
    if (res.status === "Error") throw new Error(res.message);
    return res.status === "Success";
  },

  async deleteAttachment(projectId: number, attachmentId: number): Promise<boolean> {
    const res = await projectApi.deleteAttachment(projectId, attachmentId);
    if (res.status === "Error") throw new Error(res.message);
    return res.status === "Success";
  },
  
  
  // ✅ متد جدید: آپلود یکجای همه فایل‌ها
  async uploadAttachmentsBatch(
    projectId: number,
    files: { [key in AttachmentType]?: File }
  ): Promise<boolean> {
    const res = await projectApi.uploadAttachmentsBatch(projectId, files);
    if (res.status === "Error") {
      throw new Error(res.message);
    }
    return true;
  },
  
};