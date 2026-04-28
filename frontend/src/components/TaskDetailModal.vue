<script setup lang="ts">
import { ref, watch } from 'vue'
import AppModal from './AppModal.vue'
import type { Task, Priority } from '@/types/kanban'
import type { User } from '@/types/auth'

const props = defineProps<{
  show: boolean
  task: Partial<Task> | null
  members: User[]
  saving?: boolean
  readonly?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', task: Partial<Task>): void
}>()

const editTask = ref<Partial<Task>>({})

// Réinitialiser les données quand la tâche sélectionnée change
watch(() => props.task, (newVal) => {
  if (newVal) {
    editTask.value = { ...newVal }
  }
}, { immediate: true })

// Sauvegarder les modifications
const handleSave = () => {
  if (props.readonly) return
  emit('save', editTask.value)
}
</script>

<template>
  <AppModal
    v-if="show && editTask"
    title="Détails de la tâche"
    max-width="max-w-lg"
    @close="emit('close')"
  >
    <div class="space-y-4">
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Titre</label>
        <input
          v-model="editTask.title"
          type="text"
          :disabled="readonly"
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition disabled:opacity-75"
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Description</label>
        <textarea
          v-model="editTask.description"
          rows="4"
          :disabled="readonly"
          placeholder="Ajouter une description..."
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none disabled:opacity-75"
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Priorité</label>
          <select
            v-model="editTask.priority"
            :disabled="readonly"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition disabled:opacity-75"
          >
            <option value="low">Basse</option>
            <option value="medium">Moyenne</option>
            <option value="high">Haute</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Date limite</label>
          <input
            v-model="editTask.due_date"
            type="date"
            :disabled="readonly"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition disabled:opacity-75"
          />
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Assigné à</label>
        <select
          v-model="editTask.assigned_to"
          :disabled="readonly"
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition disabled:opacity-75"
        >
          <option :value="null">Non assigné</option>
          <option v-for="user in members" :key="user.id" :value="user.id">
            {{ user.username }}
          </option>
        </select>
      </div>
    </div>

    <template #footer>
      <button
        @click="emit('close')"
        class="w-full sm:w-auto px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        {{ readonly ? 'Fermer' : 'Annuler' }}
      </button>
      <button
        v-if="!readonly"
        @click="handleSave"
        :disabled="saving"
        class="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors"
      >
        {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
      </button>
    </template>
  </AppModal>
</template>
