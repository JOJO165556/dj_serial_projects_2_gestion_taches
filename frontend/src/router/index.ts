import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import Dashboard from "../views/Dashboard.vue";
import KanbanView from "../views/KanbanView.vue";
import InviteView from "../views/InviteView.vue";
import MagicLinkView from "../views/MagicLinkView.vue";
import { useAuthStore } from "../store/authStore";

const routes = [
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/auth/magic", component: MagicLinkView },
    { path: "/", component: Dashboard, meta: { requiresAuth: true } },
    { path: "/kanban/:id", component: KanbanView, meta: { requiresAuth: true } },
    { path: "/invite/:token", component: InviteView, meta: { requiresAuth: true } },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, _) => {
    const auth = useAuthStore();

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return { path: '/register', query: { redirect: to.fullPath } }
    }

    // Empecher l'acces a /login ou /register si deja connecte
    if ((to.path === '/login' || to.path === '/register') && auth.isAuthenticated) {
        return '/'
    }

    return true
});

export default router;
