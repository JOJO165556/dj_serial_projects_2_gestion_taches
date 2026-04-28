<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/authStore'
import { useThemeStore } from '@/store/themeStore'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()

const showLogoutModal = ref(false)
const loggingOut = ref(false)

const confirmLogout = async () => {
  loggingOut.value = true
  await auth.logout()
  showLogoutModal.value = false
  loggingOut.value = false
  router.push('/login')
}
</script>

<template>
  <header class="sticky top-0 z-40 h-14 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md">
    <div class="max-w-screen-xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between gap-4">

      <!-- Logo -->
      <router-link
        to="/"
        class="text-sm font-bold tracking-tight text-violet-600 dark:text-violet-400 shrink-0"
      >
        TaskFlow
      </router-link>

      <!-- Nav centrale -->
      <nav class="hidden sm:flex items-center gap-1">
        <router-link
          to="/"
          class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          active-class="bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400 hover:bg-violet-50 dark:hover:bg-violet-900/20"
        >
          Projets
        </router-link>
      </nav>

      <!-- Droite -->
      <div class="flex items-center gap-2.5 shrink-0">

        <!-- Toggle dark mode -->
        <button
          @click="theme.toggle()"
          :title="theme.isDark ? 'Mode clair' : 'Mode sombre'"
          aria-label="Basculer le thème"
          class="p-1.5 rounded-lg border border-gray-200/80 dark:border-gray-700/80 text-gray-500 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <!-- Icone Soleil -->
          <svg v-if="theme.isDark" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <!-- Icone Lune -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>

        <!-- Séparateur -->
        <div class="w-px h-4 bg-gray-200 dark:bg-gray-700" />

        <!-- Liens Profil et Amis -->
        <div v-if="auth.isAuthenticated" class="hidden sm:flex items-center gap-4">
          <router-link
            to="/profile"
            class="text-xs font-medium text-gray-600 hover:text-violet-600 dark:text-gray-300 dark:hover:text-violet-400 transition"
          >
            {{ auth.user?.username }} (Profil)
          </router-link>
          <router-link
            to="/friends"
            class="text-xs font-medium text-gray-600 hover:text-violet-600 dark:text-gray-300 dark:hover:text-violet-400 transition"
          >
            Mes Relations
          </router-link>
        </div>

        <!-- Déconnexion -->
        <button
          @click="showLogoutModal = true"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Déconnexion
        </button>
      </div>
    </div>
  </header>

  <!-- Modale de confirmation de déconnexion -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="showLogoutModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="showLogoutModal = false"
      >
        <div class="w-full max-w-sm bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
          <!-- Icône -->
          <div class="flex items-center gap-3">
            <div class="flex-shrink-0 w-9 h-9 rounded-full bg-red-50 dark:bg-red-900/30 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-red-500">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </div>
            <div>
              <h2 class="text-sm font-semibold text-gray-900 dark:text-white">Se déconnecter ?</h2>
              <p class="text-xs text-gray-500 dark:text-gray-400">Vous devrez vous reconnecter pour accéder à votre espace.</p>
            </div>
          </div>

          <!-- Boutons -->
          <div class="flex gap-2 pt-1">
            <button
              @click="showLogoutModal = false"
              :disabled="loggingOut"
              class="flex-1 py-2 text-sm font-medium rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              Annuler
            </button>
            <button
              @click="confirmLogout"
              :disabled="loggingOut"
              class="flex-1 py-2 text-sm font-semibold rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors disabled:opacity-50"
            >
              {{ loggingOut ? 'Déconnexion...' : 'Se déconnecter' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

