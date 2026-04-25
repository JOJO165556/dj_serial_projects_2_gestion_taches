import { defineStore } from "pinia";
import { login, getMe, verifyMagicLink } from "../services/authService";
import type { User } from "../types/auth";

export const useAuthStore = defineStore("auth", {
    state: () => ({
        user: null as User | null,
        isAuthenticated: false,
        isLoading: true,
        error: null as string | null,
    }),

    actions: {
        // Appele au demarrage de l'app pour restaurer la session
        async init() {
            const token = localStorage.getItem("access");
            if (!token) {
                this.isLoading = false;
                return;
            }
            await this.fetchUser();
        },

        async loginUser(credentials: { username: string; password: string }) {
            try {
                this.error = null;
                await login(credentials);
                await this.fetchUser();
            } catch (err: any) {
                this.error = "Identifiants invalides";
            }
        },

        async fetchUser() {
            try {
                const user = await getMe();
                this.user = user;
                this.isAuthenticated = true;
            } catch {
                this.logout();
            } finally {
                this.isLoading = false;
            }
        },

        async loginWithMagicLink(payload: { email: string; token: string }) {
            try {
                this.error = null;
                const data = await verifyMagicLink(payload);
                this.user = data.user;
                this.isAuthenticated = true;
                this.isLoading = false;
            } catch (err: any) {
                this.error = err?.response?.data?.error ?? "Lien de connexion invalide";
                throw err;
            }
        },

        logout() {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            this.user = null;
            this.isAuthenticated = false;
            this.isLoading = false;
        },
    },
});
