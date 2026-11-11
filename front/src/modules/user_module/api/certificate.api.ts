// src/modules/user_module/api/certificate.api.ts

import { apiGET, apiPOST, apiDELETE } from "../../../shared/api/http";
import { BASE_URL } from "../../../shared/constants/env";
import type { JobCertificate, JobCertificateType } from "../interface/user.types";

export interface JobCertificatesResponse {
  status: "Success" | "Error";
  message: string;
  data: JobCertificate[];
}

export interface JobCertificateResponse {
  status: "Success" | "Error";
  message: string;
  data: JobCertificate;
}

export interface SimpleResponse {
  status: "Success" | "Error";
  message: string;
}

export interface UploadJobCertificateInput {
  type: JobCertificateType;
  file: File;
}

export const certificateApi = {
  list: (): Promise<JobCertificatesResponse> =>
    apiGET(`${BASE_URL}user/profile/job-certificates/`, {}, true),

  upload: (input: UploadJobCertificateInput): Promise<JobCertificateResponse> => {
    const fd = new FormData();
    fd.append("type", input.type);
    fd.append("file", input.file);
    return apiPOST(`${BASE_URL}user/profile/job-certificate/upload/`, fd, true);
  },

  delete: (type: JobCertificateType): Promise<SimpleResponse> =>
    apiDELETE(`${BASE_URL}user/profile/job-certificate/${type}/`, true),
};