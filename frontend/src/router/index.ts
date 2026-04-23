import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import Dashboard from "../views/Dashboard.vue";
import { useAuthStore } from "../store/authStore";

const routes = [
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/", component: Dashboard, meta: { requiresAuth: true } },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, _, next) => {
    const auth = useAuthStore();

    // si page protégée et pas connecté
    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return next("/login");
    }

    // si connecté et veut aller sur login
    if (to.path === "/login" && auth.isAuthenticated) {
        return next("/");
    }
    next();
});

export default router;