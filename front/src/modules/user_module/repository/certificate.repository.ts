// src/modules/user_module/repository/certificate.repository.ts

import { certificateApi, type UploadJobCertificateInput } from "../api/certificate.api";
import type { JobCertificate, JobCertificateType } from "../interface/user.types";

export const certificateRepository = {
  async list(): Promise<JobCertificate[]> {
    const res = await certificateApi.list();
    return res.data;
  },

  async upload(input: UploadJobCertificateInput): Promise<JobCertificate> {
    const res = await certificateApi.upload(input);
    return res.data;
  },

  async delete(type: JobCertificateType): Promise<void> {
    await certificateApi.delete(type);
  },
};