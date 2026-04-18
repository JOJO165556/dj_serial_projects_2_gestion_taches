<script setup lang="ts">
import { useAuthStore } from "./store/authStore.ts";
const auth = useAuthStore();
</script>

<template>
  <div v-if="auth.isLoading">Chargement...</div>
  <router-view v-else />
</template>
