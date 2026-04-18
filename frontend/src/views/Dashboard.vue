<script setup lang="ts">
import { useAuthStore } from "../store/authStore";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const logout = () => {
  auth.logout();
  router.push("/login");
};
</script>

<template>
  <div>
    <h1>Dashboard</h1>

    <p v-if="auth.user">
      Bienvenue {{ auth.user.username }}
    </p>

    <button @click="logout">Logout</button>
  </div>
</template>