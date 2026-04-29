<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import { getInvitation, respondToInvitation } from '@/services/kanbanService'
import type { Invitation } from '@/types/kanban'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
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
  } catch (err: any) {
    error.value = err?.response?.data?.error ?? "Invitation introuvable ou expirée."
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
      router.push('/')
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
          <div class="bg-gray-50 dark:bg-gray-800/60 rounded-xl border border-gray-100 dark:border-gray-700 p-5 mb-6">
            <p class="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2">Aperçu du projet</p>
            <p class="text-lg font-bold text-gray-900 dark:text-white mb-1">{{ invitation.project.name }}</p>
            <p v-if="invitation.project.description" class="text-sm text-gray-500 dark:text-gray-400 mb-4">
              {{ invitation.project.description }}
            </p>
            
            <!-- Colonnes Kanban -->
            <div class="flex flex-wrap gap-2 mb-4">
               <div v-for="col in (invitation.project as any).columns" :key="col.id" 
                    class="px-2 py-1 rounded-md bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-[10px] font-medium flex items-center gap-1.5 shadow-sm">
                 <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: col.color }"></span>
                 {{ col.name }}
               </div>
            </div>

            <div class="flex items-center gap-2 text-xs text-gray-400">
               <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
               {{ (invitation.project as any).members_count }} membres
            </div>
          </div>

          <!-- Actions -->
          <div v-if="!invitation.is_logged_in" class="flex flex-col-reverse sm:flex-row gap-3">
             <button
              @click="respond('decline')"
              :disabled="responding"
              class="flex-1 py-2.5 text-sm font-medium rounded-xl border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 transition-colors"
            >
              Refuser
            </button>
            <button
              @click="router.push({ path: '/register', query: { redirect: route.fullPath, token: token } })"
              class="flex-1 py-2.5 text-sm font-bold bg-violet-600 hover:bg-violet-700 text-white rounded-xl shadow-lg shadow-violet-500/20 transition-all"
            >
              Accepter & Rejoindre
            </button>
          </div>

          <div v-else-if="!invitation.is_correct_user" class="space-y-4">
             <p class="p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-xs rounded-lg border border-red-100 dark:border-red-800">
              Cette invitation est destinée à <strong>{{ invitation.user_email }}</strong>, mais vous êtes connecté en tant que <strong>{{ auth.user?.email }}</strong>.
            </p>
             <button
              @click="auth.logout().then(() => router.push({ path: '/login', query: { redirect: route.fullPath } }))"
              class="w-full py-2.5 text-sm font-medium border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              Changer de compte
            </button>
          </div>

          <div v-else class="flex flex-col-reverse sm:flex-row gap-3">
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
