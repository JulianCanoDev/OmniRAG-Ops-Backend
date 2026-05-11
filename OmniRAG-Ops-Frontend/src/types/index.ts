export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
}

export interface CollectionInfo {
  name: string;
  status: string;
  vectors_count: number;
}

export interface CollectionListResponse {
  collections: CollectionInfo[];
}

export interface CreateCollectionPayload {
  name: string;
  vector_size?: number;
  distance?: "Cosine" | "Dot" | "Euclid";
}

export interface IngestResponse {
  status: string;
  document_id?: string | null;
  chunks_processed: number;
  metadata: Record<string, unknown>;
  message: string;
}

export interface ApiError {
  detail: string;
  timestamp?: string;
}
