import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from "./router"
import { useAuthStore } from "./store/authStore";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

const auth = useAuthStore();

const token = localStorage.getItem("access");

if (token) {
    await auth.fetchUser().catch(() => {
        auth.logout(); //token invalide
    });
} else {
    auth.isLoading = false;
}

app.mount('#app')
