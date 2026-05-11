import apiClient from "@/lib/api-client";
import type { IngestResponse } from "@/types";
import type { AxiosProgressEvent } from "axios";

export async function uploadFile(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<IngestResponse> {
  const formData = new FormData();
  formData.set("file", file);

  const { data } = await apiClient.post<IngestResponse>(
    "/ingest/file",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (event: AxiosProgressEvent) => {
        if (event.total && onProgress) {
          onProgress(Math.round((event.loaded * 100) / event.total));
        }
      },
    },
  );
  return data;
}
