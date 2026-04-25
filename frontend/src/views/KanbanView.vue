<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useKanbanStore } from '@/store/kanbanStore'
import KanbanColumn from '@/components/KanbanColumn.vue'
import AppModal from '@/components/AppModal.vue'
import type { Task, Priority } from '@/types/kanban'

const route = useRoute()
const router = useRouter()
const store = useKanbanStore()

const projectId = computed(() => Number(route.params.id))
const showMobileFilters = ref(false)
const isArchivedProject = computed(() => store.fullKanban?.project?.is_active === false)

// Filtres
const filters = ref({ search: '', priority: '' as Priority | '', overdue: false, assignee: '' })
const hasFilters = computed(() =>
  !!(filters.value.search || filters.value.priority || filters.value.overdue || filters.value.assignee)
)

const resetFilters = () => {
  filters.value = { search: '', priority: '', overdue: false, assignee: '' }
}

// Board filtré (calcul côté client, zéro requête supplémentaire)
const filteredBoard = computed(() => {
  if (!store.fullKanban) return {}
  const f = filters.value
  const result: Record<number, Task[]> = {}

  for (const colId in store.fullKanban.board) {
    result[Number(colId)] = store.fullKanban.board[Number(colId)].filter((task) => {
      if (f.priority && task.priority !== f.priority) return false
      if (f.search && !task.title.toLowerCase().includes(f.search.toLowerCase())) return false
      if (f.assignee && task.assigned_to !== parseInt(f.assignee)) return false
      if (f.overdue) {
        if (!task.due_date) return false
        const col = store.fullKanban!.columns.find(c => c.id === Number(colId))
        if (col?.name?.toLowerCase() === 'termine') return false
        if (new Date(task.due_date) >= new Date()) return false
      }
      return true
    })
  }

  return result
})

// Modal détails tâche
const taskModal = ref(false)
const editTask = ref<Partial<Task> | null>(null)
const savingTask = ref(false)

const openTaskModal = (task: Task) => {
  editTask.value = {
    ...task,
    due_date: task.due_date ? task.due_date.split('T')[0] : null,
  }
  taskModal.value = true
}

const closeTaskModal = () => {
  taskModal.value = false
  editTask.value = null
}

const saveTask = async () => {
  if (!editTask.value?.id) return
  if (isArchivedProject.value) return
  savingTask.value = true
  await store.updateTask(editTask.value.id, {
    title: editTask.value.title,
    description: editTask.value.description,
    priority: editTask.value.priority as Priority,
    due_date: editTask.value.due_date || null,
    assigned_to: editTask.value.assigned_to || null,
  })
  savingTask.value = false
  closeTaskModal()
}

// Modal nouvelle colonne
// Gestion des événements colonnes
const onTaskCreated = async (data: { title: string; priority: string; columnId: number }) => {
  if (isArchivedProject.value) return
  await store.createTask({
    title: data.title,
    project: projectId.value,
    column: data.columnId,
    priority: data.priority as Priority,
  })
}

const onTaskDeleted = async (taskId: number, columnId: number) => {
  if (isArchivedProject.value) return
  await store.deleteTask(taskId, columnId)
}

const onTaskMoved = async (taskId: number, toColumnId: number, newTasks: Task[]) => {
  const snapshot = JSON.stringify(store.fullKanban)
  // Mise à jour optimiste du board
  if (store.fullKanban) {
    store.fullKanban.board[toColumnId] = newTasks
    // Supprimer la tâche des autres colonnes
    for (const colId in store.fullKanban.board) {
      if (Number(colId) !== toColumnId) {
        store.fullKanban.board[Number(colId)] = store.fullKanban.board[Number(colId)].filter(t => t.id !== taskId)
      }
    }
  }
  if (isArchivedProject.value) return
  const ok = await store.moveTask(taskId, toColumnId)
  if (!ok && store.fullKanban) store.fullKanban = JSON.parse(snapshot)
}

const onTasksReordered = async (tasks: Task[], columnId: number) => {
  if (store.fullKanban) {
    store.fullKanban.board[columnId] = tasks
  }
  if (isArchivedProject.value) return
  await store.reorderTasks(tasks, columnId)
}

// Init
onMounted(async () => {
  await store.fetchBoard(projectId.value)
  store.connectWebSocket(projectId.value)
  if (!store.allUsers.length) await store.fetchUsers()
})

onUnmounted(() => {
  store.disconnectWebSocket()
})

watch(projectId, async () => {
  store.reset()
  showMobileFilters.value = false
  await store.fetchBoard(projectId.value)
  store.connectWebSocket(projectId.value)
})

</script>

<template>
  <div class="flex flex-col min-h-[calc(100vh-56px)] sm:h-[calc(100vh-56px)] overflow-hidden">

    <!-- En-tête du board -->
    <div class="px-4 sm:px-5 py-4 border-b border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-950/60 backdrop-blur-sm shrink-0">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div class="flex items-center gap-3">
          <button
            @click="router.push('/')"
            class="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            title="Retour aux projets"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div class="min-w-0">
            <h1 class="text-base font-semibold text-gray-900 dark:text-white leading-tight">
              {{ store.fullKanban?.project?.name ?? 'Board Kanban' }}
            </h1>
            <p v-if="store.fullKanban?.project?.description" class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[14rem] sm:max-w-xs">
              {{ store.fullKanban.project.description }}
            </p>
          </div>
        </div>

        <span
          v-if="isArchivedProject"
          class="inline-flex items-center px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider rounded-md bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-300"
        >
          Archive
        </span>

      </div>

      <!-- Filtres -->
      <div class="flex items-center justify-between gap-2 sm:hidden mb-2">
        <button
          @click="showMobileFilters = !showMobileFilters"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="3 4 21 4 14 12 14 19 10 21 10 12 3 4"/>
          </svg>
          Filtres
        </button>
        <span class="text-[11px] text-gray-500 dark:text-gray-400">Glissez horizontalement</span>
      </div>

      <div
        class="grid grid-cols-1 sm:flex sm:flex-wrap items-center gap-2"
        :class="showMobileFilters ? 'grid' : 'hidden sm:flex'"
      >
        <div class="relative w-full sm:w-auto">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Rechercher..."
            class="pl-7 pr-3 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-violet-500 w-full sm:w-40 transition"
          />
        </div>

        <select
          v-model="filters.priority"
          class="px-2.5 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500 transition w-full sm:w-auto"
        >
          <option value="">Priorité</option>
          <option value="high">Haute</option>
          <option value="medium">Moyenne</option>
          <option value="low">Basse</option>
        </select>

        <select
          v-model="filters.assignee"
          class="px-2.5 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500 transition w-full sm:w-auto"
        >
          <option value="">Assigné</option>
          <option v-for="u in store.allUsers" :key="u.id" :value="String(u.id)">{{ u.username }}</option>
        </select>

        <label class="flex items-center gap-1.5 cursor-pointer select-none py-1 sm:py-0">
          <input
            v-model="filters.overdue"
            type="checkbox"
            class="rounded border-gray-300 dark:border-gray-600 text-violet-600 focus:ring-violet-500 focus:ring-1 h-3.5 w-3.5"
          />
          <span class="text-xs text-gray-500 dark:text-gray-400">En retard</span>
        </label>

        <button
          v-if="hasFilters"
          @click="resetFilters"
          class="text-xs text-gray-400 hover:text-red-500 dark:hover:text-red-400 px-2 py-1 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        >
          Réinitialiser
        </button>
      </div>
    </div>

    <!-- Zone board -->
    <div class="flex-1 overflow-hidden relative">
      <div
        v-if="isArchivedProject && store.fullKanban"
        class="mx-4 sm:mx-5 mt-3 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/70 text-xs text-gray-600 dark:text-gray-300"
      >
        Ce projet est archive. Le board reste consultable, mais les taches ne peuvent plus etre modifiees.
      </div>

      <!-- Chargement -->
      <div v-if="store.loading" class="flex items-start gap-4 p-5 overflow-x-auto h-full">
        <div
          v-for="i in 4" :key="i"
          class="w-72 shrink-0 h-80 rounded-2xl bg-gray-100 dark:bg-gray-800/50 animate-pulse"
        />
      </div>

      <!-- Erreur -->
      <div v-else-if="store.error" class="flex items-center justify-center h-full">
        <div class="text-center">
          <p class="text-sm text-red-500 dark:text-red-400 mb-3">{{ store.error }}</p>
          <button
            @click="store.fetchBoard(projectId)"
            class="text-xs text-violet-600 dark:text-violet-400 hover:underline"
          >
            Réessayer
          </button>
        </div>
      </div>

      <!-- Board vide -->
      <div v-else-if="store.fullKanban && !store.fullKanban.columns.length" class="flex items-center justify-center h-full">
        <div class="text-center">
          <p class="text-sm text-gray-400 dark:text-gray-500 mb-3">Aucune colonne disponible dans ce board</p>
        </div>
      </div>

      <!-- Colonnes -->
      <div
        v-else-if="store.fullKanban"
        class="flex gap-3 sm:gap-4 p-4 sm:p-5 h-full overflow-x-auto scrollbar-thin snap-x snap-mandatory"
      >
        <KanbanColumn
          v-for="column in store.fullKanban.columns"
          :key="column.id"
          :column="column"
          :tasks="filteredBoard[column.id] ?? []"
          :users="store.allUsers"
          :readonly="isArchivedProject"
          @task-clicked="openTaskModal"
          @task-deleted="onTaskDeleted"
          @task-created="onTaskCreated"
          @tasks-reordered="onTasksReordered"
          @task-moved="onTaskMoved"
        />
      </div>
    </div>

    <!-- Modal détails tâche -->
    <AppModal
      v-if="taskModal && editTask"
      title="Détails de la tâche"
      max-width="max-w-lg"
      @close="closeTaskModal"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Titre</label>
          <input
            v-model="editTask.title"
            type="text"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Description</label>
          <textarea
            v-model="editTask.description"
            rows="4"
            placeholder="Ajouter une description..."
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Priorité</label>
            <select
              v-model="editTask.priority"
              class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
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
              class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Assigné à</label>
          <select
            v-model="editTask.assigned_to"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
          >
            <option :value="null">Non assigné</option>
            <option v-for="user in store.allUsers" :key="user.id" :value="user.id">
              {{ user.username }}
            </option>
          </select>
        </div>
      </div>

      <template #footer>
        <button
          @click="closeTaskModal"
          class="w-full sm:w-auto px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          Annuler
        </button>
        <button
          @click="saveTask"
          :disabled="savingTask || isArchivedProject"
          class="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors"
        >
          {{ isArchivedProject ? 'Projet archive' : savingTask ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>
