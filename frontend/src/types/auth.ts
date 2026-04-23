export interface User {
    id: number;
    username: string;
    email: string;
}

export interface TokenResponse {
    access: string;
    refresh: string;
}