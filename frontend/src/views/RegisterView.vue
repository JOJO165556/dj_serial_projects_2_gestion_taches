<script setup lang="ts">
import { ref } from "vue";
import { register } from "../services/authService";
import { useRouter } from "vue-router";

const router = useRouter();

const form = ref({
  username: "",
  email: "",
  password: "",
  passwordConfirm: "",
});

const error = ref("");
const loading = ref(false);

const submit = async () => {
  error.value = "";

  if (form.value.password !== form.value.passwordConfirm) {
    error.value = "Les mots de passe ne correspondent pas";
    return;
  }

  loading.value = true;

  try {
    await register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
    });
    router.push("/login");
  } catch (err: any) {
    // Conserver les valeurs du formulaire, juste afficher l'erreur
    const data = err?.response?.data;
    if (data?.username) {
      error.value = "Ce nom d'utilisateur est deja pris";
    } else if (data?.email) {
      error.value = "Cet email est deja utilise";
    } else {
      error.value = "Une erreur est survenue, veuillez reessayer";
    }
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-800">

      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold text-white tracking-tight">Créer un compte</h1>
        <p class="text-gray-400 mt-2 text-sm">Rejoignez votre espace Kanban</p>
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
          <label class="block text-sm font-medium text-gray-300 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="john@example.com"
            autocomplete="email"
            class="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Mot de passe</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
            class="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Confirmer le mot de passe</label>
          <input
            v-model="form.passwordConfirm"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
            class="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
          />
        </div>

        <!-- Message d'erreur sans rechargement -->
        <p v-if="error" class="text-red-400 text-sm bg-red-900/30 border border-red-800 rounded-lg px-4 py-3">
          {{ error }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition duration-200"
        >
          {{ loading ? 'Création...' : 'Créer mon compte' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-400">
        Déjà un compte ?
        <router-link to="/login" class="text-violet-400 hover:text-violet-300 font-medium transition">
          Se connecter
        </router-link>
      </p>
    </div>
  </div>
</template>
