import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import Dashboard from "../views/Dashboard.vue";
import KanbanView from "../views/KanbanView.vue";
import InviteView from "../views/InviteView.vue";
import { useAuthStore } from "../store/authStore";

const routes = [
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/", component: Dashboard, meta: { requiresAuth: true } },
    { path: "/kanban/:id", component: KanbanView, meta: { requiresAuth: true } },
    { path: "/invite/:token", component: InviteView, meta: { requiresAuth: true } },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, _, next) => {
    const auth = useAuthStore();

    // Attendre que l'init soit terminee avant de decider la redirection
    if (auth.isLoading) {
        // L'init dans main.ts est await, donc isLoading = false avant le premier rendu
        // Ce cas ne devrait pas se produire mais on laisse passer par securite
        return next();
    }

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return next("/login");
    }

    // Empecher l'acces a /login ou /register si deja connecte
    if ((to.path === "/login" || to.path === "/register") && auth.isAuthenticated) {
        return next("/");
    }

    next();
});

export default router;