import axios from "axios";
import { refreshToken } from "../services/authService";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || `${window.location.origin}/api/`,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

api.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest = error.config;

        if (
            error.response?.status === 401 &&
            !originalRequest._retry
        ) {
            originalRequest._retry = true;

            try {
                const newAccess = await refreshToken();

                localStorage.setItem("access", newAccess);

                originalRequest.headers.Authorization = `Bearer ${newAccess}`;

                return api(originalRequest);
            } catch (err) {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");

                window.location.href = "/login";
            }
        }

        return Promise.reject(error);
    }
);

export default api;
