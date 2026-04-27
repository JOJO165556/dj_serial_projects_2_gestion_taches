import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import './assets/transitions.css'
import App from './App.vue'
import router from "./router"
import { useAuthStore } from "./store/authStore";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
const auth = useAuthStore();
await auth.init();

app.use(router);

app.mount('#app')
