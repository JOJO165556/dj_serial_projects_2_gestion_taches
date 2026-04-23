<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const theme = useThemeStore();
const router = useRouter();

const form = ref({ username: "", password: "" });
const loading = ref(false);

const submit = async () => {
  loading.value = true;
  try {
    await auth.loginUser(form.value);
    if (auth.isAuthenticated) router.push("/");
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12">

    <!-- Bouton switch thème sur les pages auth -->
    <button
      @click="theme.toggle()"
      class="fixed top-4 right-4 relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
      :class="theme.isDark ? 'bg-violet-600' : 'bg-gray-200'"
    >
      <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform duration-200"
        :class="theme.isDark ? 'translate-x-6' : 'translate-x-1'" />
    </button>

    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-violet-600 dark:text-violet-400">TaskFlow</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-2 text-sm">Gestion de tâches et projets Kanban</p>
      </div>

      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-800 p-8">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">Connexion</h2>

        <form @submit.prevent="submit" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              Nom d'utilisateur
            </label>
            <input
              v-model="form.username"
              type="text"
              placeholder="john_doe"
              autocomplete="username"
              required
              class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              Mot de passe
            </label>
            <input
              v-model="form.password"
              type="password"
              placeholder="••••••••"
              autocomplete="current-password"
              required
              class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
            />
          </div>

          <p v-if="auth.error" class="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3">
            {{ auth.error }}
          </p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-colors duration-200"
          >
            {{ loading ? 'Connexion...' : 'Se connecter' }}
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          Pas encore de compte ?
          <router-link to="/register" class="text-violet-600 dark:text-violet-400 hover:underline font-medium">
            Créer un compte
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>