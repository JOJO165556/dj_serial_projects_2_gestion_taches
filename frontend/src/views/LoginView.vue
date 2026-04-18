<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "../store/authStore.ts";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const form = ref({
  username: "",
  password: "",
});

const submit = async () => {
  await auth.loginUser(form.value);

  // redirection après login
  if (auth.isAuthenticated) {
    router.push("/");
  }
};
</script>

<template>
  <div>
    <h2>Login</h2>
    <input v-model="form.username" placeholder="username" />
    <input v-model="form.password" type="password">
    <button @click="submit">Login</button>
    <p v-if="auth.error" style="color: red;">
      {{ auth.error }}
    </p>
  </div>
</template>