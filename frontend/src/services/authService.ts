import api, { setAccessToken } from "../api/axios";
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

    setAccessToken(res.data.access);

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
    setAccessToken(res.data.access);
    return res.data;
}

export const refreshToken = async () => {
    const res = await api.post("auth/refresh/", {});

    setAccessToken(res.data.access);

    return res.data.access;
}

export const logout = async () => {
    await api.post("auth/logout/");
    setAccessToken(null);
}
