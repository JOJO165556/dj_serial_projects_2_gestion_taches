import axios from "axios";
import { refreshToken } from "../services/authService";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api/',
    withCredentials: true,
});

let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
    accessToken = token;
};

export const getAccessToken = () => accessToken;

api.interceptors.request.use((config) => {
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
});

api.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest = error.config;

        const SKIP_REFRESH_URLS = ["auth/refresh/", "auth/logout/", "auth/token/"];

        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !SKIP_REFRESH_URLS.some((url) => originalRequest.url?.endsWith(url))
        ) {
            originalRequest._retry = true;

            try {
                const newAccess = await refreshToken();

                setAccessToken(newAccess);

                originalRequest.headers.Authorization = `Bearer ${newAccess}`;

                return api(originalRequest);
            } catch (err) {
                setAccessToken(null);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
