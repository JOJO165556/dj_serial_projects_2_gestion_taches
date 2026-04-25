<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import draggable from 'vuedraggable'
import TaskCard from './TaskCard.vue'
import type { Task, Column } from '@/types/kanban'
import type { User } from '@/types/auth'

const props = defineProps<{
  column: Column
  tasks: Task[]
  users: User[]
  readonly?: boolean
}>()

const emit = defineEmits<{
  'task-clicked': [task: Task]
  'task-deleted': [taskId: number, columnId: number]
  'task-created': [data: { title: string; priority: string; columnId: number }]
  'tasks-reordered': [tasks: Task[], columnId: number]
  'task-moved': [taskId: number, toColumnId: number, tasks: Task[]]
}>()

// Copie locale pour vuedraggable (ne pas muter les props directement)
const localTasks = ref<Task[]>([...props.tasks])
watch(
  () => props.tasks,
  (val) => { localTasks.value = [...val] },
)

// Formulaire inline ajout tâche
const showAddForm = ref(false)
const newTitle = ref('')
const newPriority = ref('medium')
const addInput = ref<HTMLInputElement | null>(null)

const openAddForm = async () => {
  showAddForm.value = true
  await nextTick()
  addInput.value?.focus()
}

const cancelAdd = () => {
  showAddForm.value = false
  newTitle.value = ''
  newPriority.value = 'medium'
}

const submitTask = () => {
  if (props.readonly) return
  if (!newTitle.value.trim()) return
  emit('task-created', {
    title: newTitle.value.trim(),
    priority: newPriority.value,
    columnId: props.column.id,
  })
  cancelAdd()
}

// Événements drag & drop
const onChange = (event: any) => {
  if (props.readonly) return
  if (event.added) {
    emit('task-moved', event.added.element.id, props.column.id, localTasks.value)
  }
}

const onDragEnd = () => {
  if (props.readonly) return
  emit('tasks-reordered', localTasks.value, props.column.id)
}
</script>

<template>
  <div class="group/col w-[85vw] max-w-72 shrink-0 flex flex-col rounded-2xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/80 max-h-full snap-start">

    <!-- En-tête colonne -->
    <div class="flex items-center gap-2 px-3.5 py-3 border-b border-gray-200 dark:border-gray-800 shrink-0">
      <!-- Indicateur couleur -->
      <span
        class="w-2 h-2 rounded-full shrink-0 ring-1 ring-black/10"
        :style="{ backgroundColor: column.color || '#7C3AED' }"
      />

      <!-- Nom colonne -->
      <div class="flex-1 min-w-0">
        <div
          class="text-sm font-semibold text-gray-700 dark:text-gray-200 truncate w-full text-left"
        >
          {{ column.name }}
        </div>
      </div>

      <!-- Compteur tâches -->
      <span class="text-xs font-medium text-gray-400 dark:text-gray-500 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-1.5 py-0.5 rounded-md tabular-nums shrink-0">
        {{ tasks.length }}
      </span>

    </div>

    <!-- Liste des tâches (draggable) -->
    <draggable
      v-model="localTasks"
      group="tasks"
      item-key="id"
      :disabled="readonly"
      ghost-class="sortable-ghost"
      drag-class="sortable-drag"
      class="flex-1 p-2.5 space-y-2 min-h-[80px] overflow-y-auto scrollbar-thin"
      @change="onChange"
      @end="onDragEnd"
    >
      <template #item="{ element }">
        <TaskCard
          :task="element"
          :users="users"
          :column-name="column.name"
          :readonly="readonly"
          @click="emit('task-clicked', element)"
          @delete="(id) => emit('task-deleted', id, column.id)"
        />
      </template>
    </draggable>

    <!-- Ajouter une tâche -->
    <div class="p-2.5 border-t border-gray-200 dark:border-gray-800 shrink-0">
      <div v-if="showAddForm" class="space-y-2">
        <input
          ref="addInput"
          v-model="newTitle"
          type="text"
          placeholder="Titre de la tâche..."
          class="w-full text-sm px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-violet-500 transition"
          @keyup.enter="submitTask"
          @keyup.esc="cancelAdd"
        />
        <div class="flex items-center gap-2 flex-wrap">
          <select
            v-model="newPriority"
            class="text-xs px-2 py-1.5 rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none w-full sm:w-auto"
          >
            <option value="low">Basse</option>
            <option value="medium">Moyenne</option>
            <option value="high">Haute</option>
          </select>
          <div class="hidden sm:block flex-1" />
          <button
            @click="cancelAdd"
            class="text-xs text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-2 py-1 rounded transition-colors flex-1 sm:flex-none"
          >
            Annuler
          </button>
          <button
            @click="submitTask"
            class="text-xs bg-violet-600 hover:bg-violet-700 text-white px-3 py-1.5 rounded-lg transition-colors font-medium flex-1 sm:flex-none"
          >
            Ajouter
          </button>
        </div>
      </div>

      <button
        v-else
        @click="openAddForm"
        :disabled="readonly"
        class="flex items-center gap-1.5 w-full px-2.5 py-1.5 text-sm text-gray-400 hover:text-violet-600 dark:text-gray-500 dark:hover:text-violet-400 hover:bg-white dark:hover:bg-gray-800 rounded-lg transition-all"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        {{ readonly ? 'Projet archive' : 'Ajouter une tâche' }}
      </button>
    </div>
  </div>
</template>
