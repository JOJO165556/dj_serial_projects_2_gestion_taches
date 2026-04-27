<script setup lang="ts">
import { computed } from 'vue'
import type { Task, Priority } from '@/types/kanban'
import type { User } from '@/types/auth'

const props = defineProps<{
  task: Task
  users: User[]
  columnName?: string
  readonly?: boolean
}>()

const emit = defineEmits<{
  click: [task: Task]
  delete: [taskId: number]
}>()

const priorityBorder: Record<Priority, string> = {
  high: 'border-l-red-400 dark:border-l-red-500',
  medium: 'border-l-orange-400 dark:border-l-orange-500',
  low: 'border-l-sky-400 dark:border-l-sky-500',
}

const priorityBadge: Record<Priority, string> = {
  high:   'bg-red-50 dark:bg-red-900/25 text-red-600 dark:text-red-400',
  medium: 'bg-orange-50 dark:bg-orange-900/25 text-orange-600 dark:text-orange-400',
  low:    'bg-sky-50 dark:bg-sky-900/25 text-sky-600 dark:text-sky-400',
}

const priorityLabel: Record<Priority, string> = {
  high:   'Haute',
  medium: 'Moyenne',
  low:    'Basse',
}

const assignedUser = computed(() =>
  props.users.find(u => u.id === props.task.assigned_to)
)

const isOverdue = computed(() => {
  if (!props.task.due_date) return false
  if (props.columnName?.toLowerCase() === 'terminé') return false
  return new Date(props.task.due_date) < new Date()
})

const formattedDate = computed(() => {
  if (!props.task.due_date) return ''
  return new Date(props.task.due_date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
})

const initials = (name: string) => name.slice(0, 2).toUpperCase()

const confirmDelete = () => {
  if (confirm(`Supprimer « ${props.task.title} » ? Cette action est irréversible.`)) {
    emit('delete', props.task.id)
  }
}
</script>

<template>
  <div
    @click="emit('click', task)"
    class="group/card bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700/60 border-l-4 p-3.5 cursor-pointer hover:shadow-card-hover hover:-translate-y-px active:scale-[0.99] transition-all duration-150 select-none"
    :class="priorityBorder[task.priority]"
  >
    <!-- Titre + bouton supprimer -->
    <div class="flex justify-between items-start gap-2 mb-2">
      <p class="text-sm font-medium text-gray-900 dark:text-gray-100 leading-snug break-words flex-1">
        {{ task.title }}
      </p>
      <button
        v-if="!readonly"
        @click.stop="confirmDelete"
        class="p-1 rounded-md text-gray-300 dark:text-gray-600 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 opacity-100 sm:opacity-0 sm:group-hover/card:opacity-100 transition-all shrink-0 -mt-0.5 -mr-0.5"
        title="Supprimer"
        aria-label="Supprimer la tâche"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
        </svg>
      </button>
    </div>

    <!-- Description courte si présente -->
    <p v-if="task.description" class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-2.5 leading-relaxed break-words">
      {{ task.description }}
    </p>

    <!-- Footer carte : badges + avatar -->
    <div class="flex items-center justify-between gap-2 flex-wrap mt-1">
      <div class="flex items-center gap-1.5 flex-wrap">
        <!-- Badge priorité -->
        <span
          class="inline-flex items-center text-[11px] font-medium px-1.5 py-0.5 rounded-md"
          :class="priorityBadge[task.priority]"
        >
          {{ priorityLabel[task.priority] }}
        </span>

        <!-- Date limite -->
        <span
          v-if="task.due_date"
          class="inline-flex items-center gap-1 text-[11px] font-medium"
          :class="isOverdue
            ? 'text-red-500 dark:text-red-400'
            : 'text-gray-500 dark:text-gray-400'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          {{ formattedDate }}
          <span v-if="isOverdue" class="font-semibold">- Retard</span>
        </span>
      </div>

      <!-- Avatar assigné -->
      <div
        v-if="assignedUser"
        class="w-5 h-5 rounded-full bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 flex items-center justify-center text-[9px] font-bold shrink-0"
        :title="assignedUser.username"
      >
        {{ initials(assignedUser.username) }}
      </div>
    </div>
  </div>
</template>

