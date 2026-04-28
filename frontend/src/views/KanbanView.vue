<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useKanbanStore } from '@/store/kanbanStore'
import { useAuthStore } from '@/store/authStore'
import KanbanColumn from '@/components/KanbanColumn.vue'
import KanbanFilters from '@/components/KanbanFilters.vue'
import TaskDetailModal from '@/components/TaskDetailModal.vue'
import type { Task, Priority } from '@/types/kanban'

const route = useRoute()
const router = useRouter()
const store = useKanbanStore()
const auth = useAuthStore()

const projectId = computed(() => Number(route.params.id))
const showMobileFilters = ref(false)
const isArchivedProject = computed(() => store.fullKanban?.project?.is_active === false)
const isOwner = computed(() => store.fullKanban?.project?.owner?.id === auth.user?.id)
const taskPermError = ref(false)

// Filtres
const filters = ref({ search: '', priority: '' as Priority | '', overdue: false, assignee: '' })
const hasFilters = computed(() =>
  !!(filters.value.search || filters.value.priority || filters.value.overdue || filters.value.assignee)
)

const resetFilters = () => {
  filters.value = { search: '', priority: '', overdue: false, assignee: '' }
}

// Board filtré
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
        if (col?.name?.toLowerCase() === 'terminé') return false
        if (new Date(task.due_date) >= new Date()) return false
      }
      return true
    })
  }
  return result
})

// Modal détails tâche
const taskModal = ref(false)
const currentTask = ref<Partial<Task> | null>(null)
const savingTask = ref(false)

const openTaskModal = (task: Task) => {
  currentTask.value = {
    ...task,
    due_date: task.due_date ? task.due_date.split('T')[0] : null,
  }
  taskModal.value = true
}

const saveTask = async (data: Partial<Task>) => {
  if (!data.id || isArchivedProject.value) return
  savingTask.value = true
  await store.updateTask(data.id, {
    title: data.title,
    description: data.description,
    priority: data.priority as Priority,
    due_date: data.due_date || null,
    assigned_to: data.assigned_to || null,
  })
  savingTask.value = false
  taskModal.value = false
}

// Gestion des événements
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
  if (!isOwner.value) {
    taskPermError.value = true
    setTimeout(() => { taskPermError.value = false }, 3000)
    return
  }
  await store.deleteTask(taskId, columnId)
}

const onTaskMoved = async (taskId: number, toColumnId: number, newTasks: Task[]) => {
  if (isArchivedProject.value) return
  const snapshot = JSON.stringify(store.fullKanban)
  if (store.fullKanban) {
    store.fullKanban.board[toColumnId] = newTasks
    for (const colId in store.fullKanban.board) {
      if (Number(colId) !== toColumnId) {
        store.fullKanban.board[Number(colId)] = store.fullKanban.board[Number(colId)].filter(t => t.id !== taskId)
      }
    }
  }
  const ok = await store.moveTask(taskId, toColumnId)
  if (!ok && store.fullKanban) store.fullKanban = JSON.parse(snapshot)
}

const onTasksReordered = async (tasks: Task[], columnId: number) => {
  if (isArchivedProject.value) return
  if (store.fullKanban) store.fullKanban.board[columnId] = tasks
  await store.reorderTasks(tasks, columnId)
}

// Init & Lifecycle
onMounted(async () => {
  await store.fetchBoard(projectId.value)
  store.connectWebSocket(projectId.value)
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

const projectMembers = computed(() => {
  if (!store.fullKanban?.project) return []
  const owner = store.fullKanban.project.owner
  const members = store.fullKanban.project.members || []
  const memberIds = new Set(members.map((m: any) => m.id))
  if (!memberIds.has(owner.id)) return [owner, ...members]
  return members
})
</script>

<template>
  <div class="flex flex-col min-h-[calc(100vh-56px)] sm:h-[calc(100vh-56px)] overflow-hidden">

    <!-- En-tête du board -->
    <div class="px-4 sm:px-5 py-4 border-b border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-950/60 backdrop-blur-sm shrink-0">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div class="flex items-center gap-3">
          <button @click="router.push('/')" class="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <div class="min-w-0">
            <h1 class="text-base font-semibold text-gray-900 dark:text-white leading-tight">{{ store.fullKanban?.project?.name ?? 'Board Kanban' }}</h1>
            <p v-if="store.fullKanban?.project?.description" class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[14rem] sm:max-w-xs">{{ store.fullKanban.project.description }}</p>
          </div>
        </div>
        <span v-if="isArchivedProject" class="px-2.5 py-1 text-[11px] font-semibold uppercase bg-gray-100 dark:bg-gray-800 text-gray-500 rounded-md">Archive</span>
      </div>

      <!-- Composant Filtres -->
      <KanbanFilters 
        v-model="filters" 
        v-model:showMobile="showMobileFilters"
        :members="projectMembers"
        @reset="resetFilters"
      />
    </div>

    <!-- Zone board -->
    <div class="flex-1 overflow-hidden relative">
      <div v-if="isArchivedProject && store.fullKanban" class="mx-4 sm:mx-5 mt-3 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/70 text-xs text-gray-600 dark:text-gray-300">
        Ce projet est archivé. Les tâches ne peuvent plus être modifiées.
      </div>

      <!-- États -->
      <div v-if="store.loading" class="flex items-start gap-4 p-5 overflow-x-auto h-full">
        <div v-for="i in 4" :key="i" class="w-72 shrink-0 h-80 rounded-2xl bg-gray-100 dark:bg-gray-800/50 animate-pulse" />
      </div>
      <div v-else-if="store.error" class="flex items-center justify-center h-full">
        <div class="text-center">
          <p class="text-sm text-red-500 mb-3">{{ store.error }}</p>
          <button @click="store.fetchBoard(projectId)" class="text-xs text-violet-600 hover:underline">Réessayer</button>
        </div>
      </div>
      <div v-else-if="store.fullKanban && !store.fullKanban.columns.length" class="flex items-center justify-center h-full">
        <p class="text-sm text-gray-400">Aucune colonne disponible</p>
      </div>

      <!-- Colonnes -->
      <div v-else-if="store.fullKanban" class="flex-1 overflow-x-auto h-full scrollbar-thin">
        <div class="flex gap-3 sm:gap-4 p-4 sm:p-5 min-h-full w-fit mx-auto">
          <KanbanColumn
            v-for="column in store.fullKanban.columns"
            :key="column.id"
            :column="column"
            :tasks="filteredBoard[column.id] ?? []"
            :users="projectMembers"
            :readonly="isArchivedProject"
            @task-clicked="openTaskModal"
            @task-deleted="onTaskDeleted"
            @task-created="onTaskCreated"
            @tasks-reordered="onTasksReordered"
            @task-moved="onTaskMoved"
          />
        </div>
      </div>
    </div>

    <!-- Modal Détails -->
    <TaskDetailModal 
      :show="taskModal"
      :task="currentTask"
      :members="projectMembers"
      :saving="savingTask"
      :readonly="isArchivedProject"
      @close="taskModal = false"
      @save="saveTask"
    />

    <!-- Toasts -->
    <Teleport to="body">
      <Transition name="toast-slide">
        <div v-if="taskPermError" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-3 bg-red-600 text-white text-sm rounded-xl shadow-xl">
          Seul le propriétaire peut supprimer des tâches.
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
