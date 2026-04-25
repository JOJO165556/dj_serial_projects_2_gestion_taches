<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getInvitation, respondToInvitation } from '@/services/kanbanService'
import type { Invitation } from '@/types/kanban'

const route = useRoute()
const router = useRouter()
const token = route.params.token as string

const invitation = ref<Invitation | null>(null)
const loading = ref(true)
const error = ref('')
const responding = ref(false)
const done = ref<'accepted' | 'declined' | null>(null)

onMounted(async () => {
  try {
    const res = await getInvitation(token)
    invitation.value = res.data
  } catch {
    error.value = "Invitation introuvable ou expirée."
  } finally {
    loading.value = false
  }
})

const respond = async (action: 'accept' | 'decline') => {
  responding.value = true
  try {
    await respondToInvitation(token, action)
    done.value = action === 'accept' ? 'accepted' : 'declined'
    if (action === 'accept') {
      setTimeout(() => router.push('/'), 1800)
    }
  } catch (e: any) {
    error.value = e?.response?.data?.error ?? "Une erreur est survenue."
  } finally {
    responding.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12 bg-gray-50 dark:bg-gray-950">
    <div class="w-full max-w-md">

      <!-- Chargement -->
      <div v-if="loading" class="flex flex-col items-center gap-4">
        <div class="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        <p class="text-sm text-gray-400">Chargement de l'invitation...</p>
      </div>

      <!-- Erreur -->
      <div v-else-if="error" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-card p-6 sm:p-8 text-center">
        <div class="w-12 h-12 rounded-full bg-red-50 dark:bg-red-900/20 flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-red-500">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-1">Invitation invalide</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">{{ error }}</p>
        <button
          @click="router.push('/')"
          class="text-sm text-violet-600 dark:text-violet-400 hover:underline font-medium"
        >
          Retour à l'accueil
        </button>
      </div>

      <!-- Résultat -->
      <div v-else-if="done" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-card p-6 sm:p-8 text-center">
        <div
          class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4"
          :class="done === 'accepted' ? 'bg-green-50 dark:bg-green-900/20' : 'bg-gray-100 dark:bg-gray-800'"
        >
          <svg v-if="done === 'accepted'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="text-green-500">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-400">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </div>
        <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-1">
          {{ done === 'accepted' ? 'Invitation acceptée !' : 'Invitation refusée' }}
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ done === 'accepted'
            ? 'Redirection vers le dashboard...'
            : 'Vous pouvez fermer cette page.' }}
        </p>
      </div>

      <!-- Contenu invitation -->
      <div v-else-if="invitation" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-card overflow-hidden">
        <!-- Bande couleur en haut -->
        <div class="h-1.5 bg-gradient-to-r from-violet-500 to-indigo-500" />

        <div class="p-6 sm:p-8">
          <!-- Logo -->
          <p class="text-sm font-bold text-violet-600 dark:text-violet-400 tracking-tight mb-6">TaskFlow</p>

          <h1 class="text-xl font-semibold text-gray-900 dark:text-white mb-1">
            Vous avez été invité
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
            {{ invitation.owner.username }} vous propose de rejoindre ce projet.
          </p>

          <!-- Détails projet -->
          <div class="bg-gray-50 dark:bg-gray-800/60 rounded-xl border border-gray-100 dark:border-gray-700 p-4 mb-6">
            <p class="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1">Projet</p>
            <p class="text-base font-semibold text-gray-900 dark:text-white">{{ invitation.project.name }}</p>
            <p v-if="invitation.project.description" class="text-sm text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">
              {{ invitation.project.description }}
            </p>
          </div>

          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1 sm:gap-3 text-xs text-gray-500 dark:text-gray-400 mb-6">
            <span class="break-all">Invite pour {{ invitation.user.email }}</span>
            <span class="capitalize">{{ invitation.status }}</span>
          </div>

          <!-- Actions -->
          <div class="flex flex-col-reverse sm:flex-row gap-3">
            <button
              @click="respond('decline')"
              :disabled="responding"
              class="flex-1 py-2.5 text-sm font-medium rounded-xl border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 transition-colors"
            >
              Refuser
            </button>
            <button
              @click="respond('accept')"
              :disabled="responding"
              class="flex-1 py-2.5 text-sm font-medium rounded-xl bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors"
            >
              {{ responding ? 'En cours...' : 'Accepter' }}
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
