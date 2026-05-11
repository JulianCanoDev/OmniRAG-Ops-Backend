"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { toast } from "sonner";
import {
  listCollections,
  createCollection,
  deleteCollection,
} from "@/services/collections.service";
import type { CreateCollectionPayload } from "@/types";

const COLLECTIONS_KEY = ["collections"];

export function useCollections() {
  return useQuery({
    queryKey: COLLECTIONS_KEY,
    queryFn: listCollections,
    staleTime: 30_000,
  });
}

export function useCreateCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateCollectionPayload) => createCollection(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: COLLECTIONS_KEY });
      toast.success(`Collection "${data.name}" created`);
    },
    onError: (error: unknown) => {
      const msg =
        error && typeof error === "object" && "response" in error
          ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (error as any).response?.data?.detail ?? "Failed to create collection"
          : "Failed to create collection";
      toast.error(msg);
    },
  });
}

export function useDeleteCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (name: string) => deleteCollection(name),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: COLLECTIONS_KEY });
      toast.success(`Collection "${data.name}" deleted`);
    },
    onError: (error: unknown) => {
      const msg =
        error && typeof error === "object" && "response" in error
          ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (error as any).response?.data?.detail ?? "Failed to delete collection"
          : "Failed to delete collection";
      toast.error(msg);
    },
  });
}
