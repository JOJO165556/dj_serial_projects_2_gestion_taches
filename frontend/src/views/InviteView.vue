<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getInvitation, respondToInvitation } from '../services/kanbanService';

const route = useRoute();
const router = useRouter();

const token = route.params.token as string;
const invitationData = ref<any>(null);
const loading = ref(true);
const error = ref("");
const successMessage = ref("");

onMounted(async () => {
  try {
    const res = await getInvitation(token);
    invitationData.value = res.data;
    if (res.data.status !== 'pending') {
      error.value = "Cette invitation a déjà été traitée.";
    }
  } catch (err: any) {
    if (err.response?.status === 404) {
      error.value = "Invitation introuvable ou expirée.";
    } else if (err.response?.status === 403) {
      error.value = "Vous n'êtes pas autorisé à voir cette invitation. Êtes-vous connecté avec le bon compte ?";
    } else {
      error.value = "Impossible de charger les détails de l'invitation.";
    }
  } finally {
    loading.value = false;
  }
});

const handleResponse = async (action: 'accept' | 'decline') => {
  try {
    await respondToInvitation(token, action);
    if (action === 'accept') {
      successMessage.value = "Vous avez rejoint le projet avec succès !";
      setTimeout(() => router.push('/dashboard'), 2000);
    } else {
      successMessage.value = "Vous avez décliné l'invitation.";
      setTimeout(() => router.push('/dashboard'), 2000);
    }
  } catch (err: any) {
    error.value = err.response?.data?.error || "Une erreur est survenue lors du traitement de l'invitation.";
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700">
      <div v-if="loading" class="flex flex-col items-center justify-center space-y-4">
        <div class="w-12 h-12 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
        <p class="text-gray-500 dark:text-gray-400">Chargement de l'invitation...</p>
      </div>

      <div v-else-if="error" class="text-center">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/30 mb-4">
          <svg class="h-6 w-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Oops!</h2>
        <p class="text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-xl p-3 text-sm">{{ error }}</p>
        <button @click="router.push('/dashboard')" class="mt-6 w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-xl transition-colors">
          Retour au Dashboard
        </button>
      </div>

      <div v-else-if="successMessage" class="text-center">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 dark:bg-green-900/30 mb-4">
          <svg class="h-6 w-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">C'est fait !</h2>
        <p class="text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 rounded-xl p-3 text-sm">{{ successMessage }}</p>
        <p class="text-xs text-gray-500 mt-4">Redirection en cours...</p>
      </div>

      <div v-else-if="invitationData" class="text-center">
        <h2 class="text-2xl font-extrabold text-gray-900 dark:text-white mb-2">Invitation au Projet</h2>
        <p class="text-gray-500 dark:text-gray-400 mb-8">
          <strong class="text-violet-600 dark:text-violet-400">{{ invitationData.owner_name }}</strong> vous a invité à rejoindre le projet 
          <strong class="text-gray-900 dark:text-white">{{ invitationData.project_name }}</strong>.
        </p>

        <div class="flex flex-col space-y-3">
          <button 
            @click="handleResponse('accept')"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-violet-600 hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-500 transition-colors"
          >
            Accepter l'invitation
          </button>
          <button 
            @click="handleResponse('decline')"
            class="w-full flex justify-center py-3 px-4 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-500 transition-colors"
          >
            Décliner
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
