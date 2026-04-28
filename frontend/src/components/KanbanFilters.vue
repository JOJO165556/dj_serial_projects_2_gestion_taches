<script setup lang="ts">
import type { Priority } from '@/types/kanban'
import type { User } from '@/types/auth'

const props = defineProps<{
  modelValue: {
    search: string
    priority: Priority | ''
    overdue: boolean
    assignee: string
  }
  members: User[]
  showMobile: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
  (e: 'update:showMobile', value: boolean): void
  (e: 'reset'): void
}>()

// Vérifier si des filtres sont actifs
const hasFilters = () => 
  !!(props.modelValue.search || props.modelValue.priority || props.modelValue.overdue || props.modelValue.assignee)

// Mettre à jour un champ de filtre individuel
const updateFilter = (key: string, value: any) => {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
</script>

<template>
  <div>
    <!-- Toggle Mobile -->
    <div class="flex items-center justify-between gap-2 sm:hidden mb-2">
      <button
        @click="emit('update:showMobile', !showMobile)"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="3 4 21 4 14 12 14 19 10 21 10 12 3 4"/>
        </svg>
        Filtres
      </button>
      <span class="text-[11px] text-gray-500 dark:text-gray-400">Glissez horizontalement</span>
    </div>

    <!-- Filtres Desktop/Mobile -->
    <div
      class="grid grid-cols-1 sm:flex sm:flex-wrap items-center gap-2"
      :class="showMobile ? 'grid' : 'hidden sm:flex'"
    >
      <!-- Recherche -->
      <div class="relative w-full sm:w-auto">
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          :value="modelValue.search"
          @input="e => updateFilter('search', (e.target as HTMLInputElement).value)"
          type="text"
          placeholder="Rechercher..."
          class="pl-7 pr-3 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-violet-500 w-full sm:w-40 transition"
        />
      </div>

      <!-- Priorité -->
      <select
        :value="modelValue.priority"
        @change="e => updateFilter('priority', (e.target as HTMLSelectElement).value)"
        class="px-2.5 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500 transition w-full sm:w-auto"
      >
        <option value="">Priorité</option>
        <option value="high">Haute</option>
        <option value="medium">Moyenne</option>
        <option value="low">Basse</option>
      </select>

      <!-- Assigné -->
      <select
        :value="modelValue.assignee"
        @change="e => updateFilter('assignee', (e.target as HTMLSelectElement).value)"
        class="px-2.5 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500 transition w-full sm:w-auto"
      >
        <option value="">Assigné</option>
        <option v-for="u in members" :key="u.id" :value="String(u.id)">{{ u.username }}</option>
      </select>

      <!-- En retard -->
      <label class="flex items-center gap-1.5 cursor-pointer select-none py-1 sm:py-0">
        <input
          :checked="modelValue.overdue"
          @change="e => updateFilter('overdue', (e.target as HTMLInputElement).checked)"
          type="checkbox"
          class="rounded border-gray-300 dark:border-gray-600 text-violet-600 focus:ring-violet-500 focus:ring-1 h-3.5 w-3.5"
        />
        <span class="text-xs text-gray-500 dark:text-gray-400">En retard</span>
      </label>

      <!-- Réinitialiser -->
      <button
        v-if="hasFilters()"
        @click="emit('reset')"
        class="text-xs text-gray-400 hover:text-red-500 dark:hover:text-red-400 px-2 py-1 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
      >
        Réinitialiser
      </button>
    </div>
  </div>
</template>
