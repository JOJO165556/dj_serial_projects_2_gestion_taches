import api from "../api/axios";
import type { TokenResponse, User, MagicLinkVerifyResponse } from "../types/auth";

export const register = async (data: {
    username: string;
    email: string;
    password: string;
}): Promise<void> => {
    await api.post("auth/register/", data);
};

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

export const requestMagicLink = async (email: string): Promise<void> => {
    await api.post("auth/magic-link/", { email });
}

export const verifyMagicLink = async (data: {
    email: string;
    token: string;
}): Promise<MagicLinkVerifyResponse> => {
    const res = await api.post<MagicLinkVerifyResponse>("auth/magic-link/verify/", data);
    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);
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
