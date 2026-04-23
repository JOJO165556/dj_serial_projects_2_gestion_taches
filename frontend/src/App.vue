<script setup lang="ts">
import { useAuthStore } from "./store/authStore";
import { useThemeStore } from "./store/themeStore";

const auth = useAuthStore();
const theme = useThemeStore();
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">

    <!-- Bouton switch theme -->
    <button
      v-if="!auth.isLoading"
      @click="theme.toggle()"
      class="fixed top-4 right-4 z-50 p-2 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors shadow-md"
      :title="theme.isDark ? 'Passer en mode clair' : 'Passer en mode sombre'"
    >
      <span v-if="theme.isDark" class="text-yellow-400 text-lg">&#9728;</span>
      <span v-else class="text-gray-600 text-lg">&#9790;</span>
    </button>

    <div v-if="auth.isLoading" class="flex items-center justify-center min-h-screen text-gray-500 dark:text-gray-400">
      Chargement...
    </div>
    <router-view v-else />
  </div>
</template>
