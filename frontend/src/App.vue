<script setup lang="ts">
import { useAuthStore } from "./store/authStore";
import NavBar from "./components/NavBar.vue";

const auth = useAuthStore();
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <NavBar v-if="!auth.isLoading && auth.isAuthenticated" />

    <main class="flex-1">
      <div v-if="auth.isLoading" class="flex items-center justify-center min-h-screen">
        <div class="w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
      <router-view v-else />
    </main>
  </div>
</template>
