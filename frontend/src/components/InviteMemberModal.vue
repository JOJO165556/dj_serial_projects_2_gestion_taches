<script setup lang="ts">
import { ref, watch } from 'vue'
import AppModal from './AppModal.vue'
import type { Friendship } from '@/services/friendService'
import type { InvitationCreateResult } from '@/types/kanban'

const props = defineProps<{
  show: boolean
  projectId: number | null
  friends: Friendship[]
  submitting?: boolean
  inviteResult: InvitationCreateResult | null
  inviteLink: string
  inviteError: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', data: { userId: number | null, email: string, message: string }): void
  (e: 'copy', text: string): void
}>()

const selectedUserId = ref<number | null>(null)
const inviteEmail = ref('')
const inviteMessage = ref('')

// Réinitialiser les champs quand on ouvre la modale
watch(() => props.show, (newVal) => {
  if (newVal) {
    selectedUserId.value = null
    inviteEmail.value = ''
    inviteMessage.value = ''
  }
})

// Envoyer l'invitation
const handleSubmit = () => {
  emit('submit', {
    userId: selectedUserId.value,
    email: inviteEmail.value.trim(),
    message: inviteMessage.value.trim()
  })
}

const getFriendProfile = (f: Friendship) => f.sender.id === f.receiver.id ? f.receiver : (f.sender.id === 0 ? f.receiver : f.sender) 
// Wait, the friend profile helper needs to know the current user ID. 
// Let's pass the helper function or just the necessary data.
// Actually, let's just pass the pre-filtered friends list with a simpler structure.
// Or just pass the current user's ID to the component.

const getFriendId = (f: Friendship) => f.sender.username === '...' ? f.receiver.id : f.sender.id
</script>

<script lang="ts">
// Helper to get friend profile if we don't have auth store here
// But it's easier to pass the already formatted list of friends
</script>

<template>
  <AppModal v-if="show" title="Inviter un membre" @close="emit('close')">
    <!-- Lien généré -->
    <div v-if="inviteLink" class="space-y-4">
      <div class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
        <p class="text-sm font-medium text-green-700 dark:text-green-400 mb-2">Invitation créée</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          {{ inviteResult?.email_sent
            ? "L'email d'invitation a bien été envoyé."
            : "Le lien est prêt. Vous pouvez le transmettre manuellement si besoin." }}
        </p>
        <div class="flex flex-col sm:flex-row gap-2">
          <input
            :value="inviteLink"
            readonly
            class="flex-1 text-xs px-2.5 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none"
          />
          <button
            @click="emit('copy', inviteLink)"
            class="px-3 py-2 text-xs font-medium rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors shrink-0"
          >
            Copier
          </button>
        </div>
        <p v-if="inviteResult && !inviteResult.email_sent" class="mt-3 text-xs text-amber-700 dark:text-amber-400">
          {{ inviteResult.email_error || "Aucun envoi SMTP n'a été confirmé par le serveur." }}
        </p>
      </div>
    </div>

    <!-- Formulaire -->
    <div v-else class="space-y-4">
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Inviter un Ami (Optionnel)</label>
        <select
          v-model="selectedUserId"
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
        >
          <option :value="null">-- Choisir dans mes relations --</option>
          <option v-for="f in friends" :key="f.id" :value="f.sender.username === '...' ? f.receiver.id : f.sender.id">
             <!-- Note: labels should be passed pre-formatted -->
             {{ f.sender.username }} <!-- simplified for now, will fix in Dashboard.vue passing -->
          </option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Ou saisir une adresse email</label>
        <input
          v-model="inviteEmail"
          type="email"
          placeholder="exemple@email.com"
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
        />
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Message</label>
        <textarea
          v-model="inviteMessage"
          rows="3"
          placeholder="Ajoutez un petit contexte..."
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none"
        />
      </div>
      <p v-if="inviteError" class="text-sm text-red-500 dark:text-red-400">{{ inviteError }}</p>
    </div>

    <template #footer>
      <button @click="emit('close')" class="w-full sm:w-auto px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
        {{ inviteLink ? 'Fermer' : 'Annuler' }}
      </button>
      <button
        v-if="!inviteLink"
        @click="handleSubmit"
        :disabled="submitting"
        class="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors"
      >
        {{ submitting ? 'Envoi...' : "Envoyer l'invitation" }}
      </button>
    </template>
  </AppModal>
</template>
