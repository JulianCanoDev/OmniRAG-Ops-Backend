import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error(
    "[OmniRAG-Ops] NEXT_PUBLIC_API_URL is not defined. " +
      "Create a .env.local file in OmniRAG-Ops-Frontend/ with:\n" +
      "  NEXT_PUBLIC_API_URL=http://localhost:8000\n" +
      "The backend API is served on the /api/v1 prefix automatically.",
  );
}

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

if (process.env.NODE_ENV === "development") {
  console.log(
    `[OmniRAG-Ops] API client configured → base URL: ${apiClient.defaults.baseURL}`,
  );
}

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");
        const { data } = await axios.post(
          `${apiClient.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken },
        );
        localStorage.setItem("access_token", data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
