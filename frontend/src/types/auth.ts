export interface User {
    id: number;
    username: string;
    email: string;
    role?: string;
    first_name?: string;
    last_name?: string;
    avatar?: string;
    bio?: string;
}

export interface TokenResponse {
    access: string;
    refresh: string;
}

export interface MagicLinkVerifyResponse extends TokenResponse {
    user: User;
}
