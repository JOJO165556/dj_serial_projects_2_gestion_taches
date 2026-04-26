<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/authStore'
import { useThemeStore } from '@/store/themeStore'
import { useRoute, useRouter } from 'vue-router'
import { requestMagicLink } from '@/services/authService'

const auth = useAuthStore()
const theme = useThemeStore()
const route = useRoute()
const router = useRouter()

const form = ref({ username: '', password: '' })
const magicEmail = ref('')
const loading = ref(false)
const magicLoading = ref(false)
const magicError = ref('')
const magicSuccess = ref('')
const showPassword = ref(false)

const submit = async () => {
  loading.value = true
  try {
    await auth.loginUser(form.value)
    if (auth.isAuthenticated) {
      const redirect = route.query.redirect as string || '/'
      router.push(redirect)
    }
  } finally {
    loading.value = false
  }
}

const submitMagicLink = async () => {
  magicError.value = ''
  magicSuccess.value = ''
  magicLoading.value = true
  try {
    await requestMagicLink(magicEmail.value)
    magicSuccess.value = 'Si un compte existe pour cet email, un lien de connexion a ete envoye.'
  } catch (err: any) {
    magicError.value = err?.response?.data?.email?.[0] ?? 'Impossible d’envoyer le lien pour le moment.'
  } finally {
    magicLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12 bg-gray-50 dark:bg-gray-950">

    <!-- Toggle thème -->
    <button
      @click="theme.toggle()"
      class="fixed top-4 right-4 p-2 rounded-lg text-gray-500 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white bg-white/90 dark:bg-gray-900/90 border border-gray-200 dark:border-gray-700 transition-all"
      :title="theme.isDark ? 'Mode clair' : 'Mode sombre'"
    >
      <svg v-if="theme.isDark" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="5"/>
        <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
        <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
    </button>

    <div class="w-full max-w-sm">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-violet-600 mb-4 shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
        </div>
        <h1 class="text-lg font-bold text-gray-900 dark:text-white tracking-tight">TaskFlow</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">Gestion de projets Kanban</p>
      </div>

      <!-- Carte -->
      <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-card p-7">
        <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-5">Connexion</h2>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">
              Nom d'utilisateur
            </label>
            <input
              v-model="form.username"
              type="text"
              placeholder="john_doe"
              autocomplete="username"
              required
              class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">
              Mot de passe
            </label>
            <div class="relative">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                autocomplete="current-password"
                required
                class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition pr-10"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
          </div>

          <!-- Erreur -->
          <div v-if="auth.error" class="flex items-start gap-2 px-3 py-2.5 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" class="text-red-500 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <p class="text-xs text-red-600 dark:text-red-400">{{ auth.error }}</p>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-2.5 mt-1 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-60 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors"
          >
            {{ loading ? 'Connexion...' : 'Se connecter' }}
          </button>
        </form>

        <div class="my-5 flex items-center gap-3">
          <div class="h-px flex-1 bg-gray-100 dark:bg-gray-800" />
          <span class="text-[11px] uppercase tracking-wider text-gray-500 dark:text-gray-400">ou</span>
          <div class="h-px flex-1 bg-gray-100 dark:bg-gray-800" />
        </div>

        <form @submit.prevent="submitMagicLink" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">
              Lien magique par email
            </label>
            <input
              v-model="magicEmail"
              type="email"
              placeholder="john@example.com"
              autocomplete="email"
              required
              class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
            />
          </div>

          <div v-if="magicError" class="flex items-start gap-2 px-3 py-2.5 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p class="text-xs text-red-600 dark:text-red-400">{{ magicError }}</p>
          </div>

          <div v-if="magicSuccess" class="flex items-start gap-2 px-3 py-2.5 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <p class="text-xs text-green-700 dark:text-green-400">{{ magicSuccess }}</p>
          </div>

          <button
            type="submit"
            :disabled="magicLoading"
            class="w-full py-2.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 disabled:opacity-60 disabled:cursor-not-allowed text-gray-700 dark:text-gray-200 text-sm font-semibold transition-colors"
          >
            {{ magicLoading ? 'Envoi...' : 'Recevoir un lien de connexion' }}
          </button>
        </form>

        <p class="mt-5 text-center text-xs text-gray-500 dark:text-gray-400">
          Pas encore de compte ?
          <router-link to="/register" class="text-violet-600 dark:text-violet-400 hover:underline font-medium">
            Créer un compte
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>
