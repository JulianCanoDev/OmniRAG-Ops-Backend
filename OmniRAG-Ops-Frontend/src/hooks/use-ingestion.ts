"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { uploadFile } from "@/services/ingestion.service";

export function useIngestFile() {
  return useMutation({
    mutationFn: ({
      file,
      onProgress,
    }: {
      file: File;
      onProgress?: (percent: number) => void;
    }) => uploadFile(file, onProgress),
    onSuccess: (data) => {
      toast.success(
        data.message || `Ingested — ${data.chunks_processed} chunks processed`,
      );
    },
    onError: (error: unknown) => {
      const msg =
        error && typeof error === "object" && "response" in error
          ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (error as any).response?.data?.detail ?? "Ingestion failed"
          : "Ingestion failed";
      toast.error(msg);
    },
  });
}
