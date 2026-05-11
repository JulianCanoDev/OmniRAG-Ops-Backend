import apiClient from "@/lib/api-client";
import type {
  CollectionListResponse,
  CreateCollectionPayload,
} from "@/types";

export async function listCollections(): Promise<CollectionListResponse> {
  const { data } = await apiClient.get<CollectionListResponse>("/collections");
  return data;
}

export async function createCollection(
  payload: CreateCollectionPayload,
): Promise<{ status: string; name: string }> {
  const { data } = await apiClient.post<{ status: string; name: string }>(
    "/collections",
    payload,
  );
  return data;
}

export async function deleteCollection(
  name: string,
): Promise<{ status: string; name: string }> {
  const { data } = await apiClient.delete<{ status: string; name: string }>(
    `/collections/${encodeURIComponent(name)}`,
  );
  return data;
}
