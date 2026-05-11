import apiClient from "@/lib/api-client";
import type { AuthToken, RegisterPayload, User } from "@/types";

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const { data } = await apiClient.post<User>("/auth/register", payload);
  return data;
}

export async function loginUser(
  username: string,
  password: string,
): Promise<AuthToken> {
  const formData = new URLSearchParams();
  formData.set("username", username);
  formData.set("password", password);

  const { data } = await apiClient.post<AuthToken>("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}
