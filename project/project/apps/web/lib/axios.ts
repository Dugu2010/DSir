import axios from "axios";
import Cookies from "js-cookie";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

function subscribeToRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

function getAccessToken() {
  return Cookies.get("access_token");
}

function getRefreshToken() {
  return Cookies.get("refresh_token");
}

function setAccessToken(token: string) {
  Cookies.set("access_token", token, { expires: 1 / 48 }); // 30 minutes
}

function setRefreshToken(token: string) {
  Cookies.set("refresh_token", token, { expires: 7 });
}

export function clearAuthCookies() {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
}

export function saveTokens(accessToken: string, refreshToken: string) {
  setAccessToken(accessToken);
  setRefreshToken(refreshToken);
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeToRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(apiClient(originalRequest));
          });
        });
      }

      isRefreshing = true;
      const refreshToken = getRefreshToken();

      if (!refreshToken) {
        clearAuthCookies();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(`${API_BASE}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = response.data;
        saveTokens(access_token, refresh_token);

        apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`;
        onRefreshed(access_token);
        isRefreshing = false;

        return apiClient(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        clearAuthCookies();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export async function login(email: string, password: string) {
  const response = await apiClient.post("/auth/login", { email, password });
  const { access_token, refresh_token } = response.data;
  saveTokens(access_token, refresh_token);
  return response.data;
}

export async function register(email: string, password: string, fullName: string) {
  const response = await apiClient.post("/auth/register", {
    email,
    password,
    full_name: fullName,
  });
  const { access_token, refresh_token } = response.data;
  saveTokens(access_token, refresh_token);
  return response.data;
}

export async function logout() {
  const refreshToken = getRefreshToken();
  try {
    await apiClient.post("/auth/logout", { refresh_token: refreshToken });
  } finally {
    clearAuthCookies();
  }
}

export async function fetchMe() {
  const response = await apiClient.get("/auth/me");
  return response.data;
}
