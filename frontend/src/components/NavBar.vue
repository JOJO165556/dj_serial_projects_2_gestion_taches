<script setup lang="ts">
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const theme = useThemeStore();
const router = useRouter();

const logout = () => {
  auth.logout();
  router.push("/login");
};
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">

      <!-- Logo -->
      <router-link to="/" class="text-xl font-bold text-violet-600 dark:text-violet-400 shrink-0">
        TaskFlow
      </router-link>

      <!-- Navigation centrale (masquée sur mobile) -->
      <nav class="hidden sm:flex items-center gap-2">
        <router-link
          to="/"
          class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white transition-colors"
          active-class="bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400"
        >
          Projets
        </router-link>
        <router-link
          to="/kanban"
          class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white transition-colors"
          active-class="bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400"
        >
          Kanban
        </router-link>
      </nav>

      <!-- Droite : switch + user -->
      <div class="flex items-center gap-3 shrink-0">

        <!-- Toggle switch thème -->
        <button
          @click="theme.toggle()"
          :title="theme.isDark ? 'Mode clair' : 'Mode sombre'"
          class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-gray-950"
          :class="theme.isDark ? 'bg-violet-600' : 'bg-gray-200'"
        >
          <span
            class="inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform duration-200"
            :class="theme.isDark ? 'translate-x-6' : 'translate-x-1'"
          >
          </span>
          <!-- Icone soleil/lune dans le fond du toggle -->
          <span class="absolute left-1 text-[10px]" v-if="!theme.isDark">☀</span>
          <span class="absolute right-1 text-[10px] text-white" v-if="theme.isDark">☾</span>
        </button>

        <!-- User info -->
        <span v-if="auth.user" class="hidden sm:block text-sm text-gray-600 dark:text-gray-300">
          {{ auth.user.username }}
        </span>

        <!-- Logout -->
        <button
          @click="logout"
          class="px-3 py-1.5 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400 transition-colors"
        >
          Déconnexion
        </button>
      </div>
    </div>
  </header>
</template>
