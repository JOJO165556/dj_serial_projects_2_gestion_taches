import api from "../api/axios";
import type { TokenResponse, User } from "../types/auth";

export const login = async (data: {
    username: string,
    password: string,
}): Promise<TokenResponse> => {
    const res = await api.post<TokenResponse>("auth/token/", data);

    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);

    return res.data;
};

export const getMe = async (): Promise<User> => {
    const res = await api.get<User>("auth/me/")
    return res.data;
}

export const refreshToken = async () => {
    const refresh = localStorage.getItem("refresh");

    const res = await api.post("auth/refresh/", {
        refresh,
    });

    localStorage.setItem("access", res.data.access);

    return res.data.access;
}