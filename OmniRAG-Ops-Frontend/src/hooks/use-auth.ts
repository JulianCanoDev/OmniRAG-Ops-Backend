"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { loginUser, registerUser, getMe } from "@/services/auth.service";
import type { RegisterPayload } from "@/types";

const CURRENT_USER_KEY = ["currentUser"];

export function useCurrentUser() {
  return useQuery({
    queryKey: CURRENT_USER_KEY,
    queryFn: getMe,
    retry: false,
    staleTime: 60_000,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      loginUser(email, password),
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY });
      toast.success("Logged in successfully");
      router.push("/dashboard");
    },
    onError: () => {
      toast.error("Invalid email or password");
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: (payload: RegisterPayload) => registerUser(payload),
    onSuccess: () => {
      toast.success("Account created — you can now log in");
      router.push("/login");
    },
    onError: (error: unknown) => {
      const msg =
        error && typeof error === "object" && "response" in error
          ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (error as any).response?.data?.detail ?? "Registration failed"
          : "Registration failed";
      toast.error(msg);
    },
  });
}
