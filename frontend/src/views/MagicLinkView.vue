<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const token = route.query.token
  const email = route.query.email

  if (typeof token !== 'string' || typeof email !== 'string') {
    error.value = 'Lien de connexion incomplet.'
    loading.value = false
    return
  }

  try {
    await auth.loginWithMagicLink({ email, token })
    router.replace('/')
  } catch (err: any) {
    error.value = err?.response?.data?.error ?? auth.error ?? 'Lien de connexion invalide.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12 bg-gray-50 dark:bg-gray-950">
    <div class="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-card p-6 sm:p-8 text-center">
      <div v-if="loading" class="space-y-4">
        <div class="w-10 h-10 mx-auto border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        <h1 class="text-base font-semibold text-gray-900 dark:text-white">Connexion en cours</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">Nous verifions votre lien magique.</p>
      </div>

      <div v-else-if="error" class="space-y-4">
        <div class="w-12 h-12 rounded-full bg-red-50 dark:bg-red-900/20 flex items-center justify-center mx-auto">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-red-500">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <h1 class="text-base font-semibold text-gray-900 dark:text-white">Lien indisponible</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ error }}</p>
        <button
          @click="router.push('/login')"
          class="px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white transition-colors"
        >
          Retour a la connexion
        </button>
      </div>
    </div>
  </div>
</template>
