<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "../store/authStore";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const form = ref({
  username: "",
  password: "",
});

const error = ref("");
const loading = ref(false);

const submit = async () => {
  error.value = "";
  loading.value = true;

  try {
    await auth.loginUser(form.value);
    if (auth.isAuthenticated) {
      router.push("/");
    }
  } catch {
    // Rien a faire, l'erreur est dans auth.error
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-800">

      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold text-white tracking-tight">Connexion</h1>
        <p class="text-gray-400 mt-2 text-sm">Bon retour sur votre espace de travail</p>
      </div>

      <form @submit.prevent="submit" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Nom d'utilisateur</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="john_doe"
            autocomplete="username"
            class="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Mot de passe</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            class="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
          />
        </div>

        <!-- Message d'erreur sans rechargement -->
        <p v-if="auth.error" class="text-red-400 text-sm bg-red-900/30 border border-red-800 rounded-lg px-4 py-3">
          {{ auth.error }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition duration-200"
        >
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-400">
        Pas encore de compte ?
        <router-link to="/register" class="text-violet-400 hover:text-violet-300 font-medium transition">
          Créer un compte
        </router-link>
      </p>
    </div>
  </div>
</template>