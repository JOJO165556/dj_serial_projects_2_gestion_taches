<script setup lang="ts">
import { ref, watch } from 'vue'
import AppModal from './AppModal.vue'

const props = defineProps<{
  show: boolean
  title: string
  initialData?: { name: string, description: string }
  submitting?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', data: { name: string, description: string }): void
}>()

const form = ref({ name: '', description: '' })

// Synchroniser le formulaire si on passe des données initiales (édition)
watch(() => props.initialData, (newVal) => {
  if (newVal) {
    form.value = { ...newVal }
  } else {
    form.value = { name: '', description: '' }
  }
}, { immediate: true })

// Soumission du formulaire
const handleSubmit = () => {
  if (!form.value.name.trim()) return
  emit('submit', { ...form.value })
}
</script>

<template>
  <AppModal v-if="show" :title="title" @close="emit('close')">
    <div class="space-y-4">
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Nom *</label>
        <input
          v-model="form.name"
          type="text"
          placeholder="Mon projet..."
          autofocus
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
          @keyup.enter="handleSubmit"
        />
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Description</label>
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="Description optionnelle..."
          class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none"
        />
      </div>
    </div>
    <template #footer>
      <button @click="emit('close')" class="w-full sm:w-auto px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
        Annuler
      </button>
      <button 
        @click="handleSubmit" 
        :disabled="submitting || !form.name.trim()" 
        class="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors"
      >
        {{ submitting ? 'Envoi...' : 'Valider' }}
      </button>
    </template>
  </AppModal>
</template>
