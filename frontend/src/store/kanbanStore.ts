import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { KanbanBoard, Task, CreateTaskData, UpdateTaskData } from '@/types/kanban'
import type { User } from '@/types/auth'
import {
  getProjectKanban,
  createTask as apiCreateTask,
  updateTask as apiUpdateTask,
  deleteTask as apiDeleteTask,
  reorderTasks as apiReorderTasks,
  getUsers,
} from '@/services/kanbanService'

const buildWsUrl = (projectId: number) => {
  const configuredUrl = import.meta.env.VITE_WS_BASE_URL
  if (configuredUrl) {
    return `${configuredUrl.replace(/\/$/, '')}/ws/kanban/${projectId}/`
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/ws/kanban/${projectId}/`
}

export const useKanbanStore = defineStore('kanban', () => {
  const fullKanban = ref<KanbanBoard | null>(null)
  const loading = ref(false)
  const error = ref('')
  const allUsers = ref<User[]>([])

  let ws: WebSocket | null = null

  // --- Données ---

  const fetchBoard = async (projectId: number) => {
    loading.value = true
    error.value = ''
    try {
      const res = await getProjectKanban(projectId)
      fullKanban.value = res.data
    } catch {
      error.value = 'Impossible de charger le board'
    } finally {
      loading.value = false
    }
  }

  const fetchUsers = async () => {
    try {
      const res = await getUsers()
      allUsers.value = res.data
    } catch (e) {
      console.error('Erreur chargement utilisateurs', e)
    }
  }

  const reset = () => {
    fullKanban.value = null
    error.value = ''
    loading.value = false
  }

  // --- WebSocket ---

  const connectWebSocket = (projectId: number) => {
    if (ws) ws.close()
    ws = new WebSocket(buildWsUrl(projectId))
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'update_board' && data.board_data) {
          fullKanban.value = data.board_data
        }
      } catch { /* ignore */ }
    }
  }

  const disconnectWebSocket = () => {
    ws?.close()
    ws = null
  }

  // --- Tâches ---

  const createTask = async (data: CreateTaskData): Promise<Task | null> => {
    try {
      const res = await apiCreateTask(data)
      const task: Task = res.data
      if (fullKanban.value && task.column !== null) {
        if (!fullKanban.value.board[task.column]) {
          fullKanban.value.board[task.column] = []
        }
        fullKanban.value.board[task.column].push(task)
      }
      return task
    } catch {
      return null
    }
  }

  const updateTask = async (id: number, data: UpdateTaskData): Promise<boolean> => {
    if (!fullKanban.value) return false
    const snapshot = JSON.stringify(fullKanban.value)
    try {
      await apiUpdateTask(id, data)
      // Mise à jour locale
      for (const colId in fullKanban.value.board) {
        const tasks = fullKanban.value.board[Number(colId)]
        const idx = tasks.findIndex(t => t.id === id)
        if (idx !== -1) {
          tasks[idx] = { ...tasks[idx], ...data } as Task
          break
        }
      }
      return true
    } catch {
      fullKanban.value = JSON.parse(snapshot)
      return false
    }
  }

  const deleteTask = async (taskId: number, columnId: number): Promise<boolean> => {
    if (!fullKanban.value) return false
    const snapshot = JSON.stringify(fullKanban.value)
    // Suppression optimiste
    fullKanban.value.board[columnId] = fullKanban.value.board[columnId]?.filter(t => t.id !== taskId) ?? []
    try {
      await apiDeleteTask(taskId)
      return true
    } catch {
      fullKanban.value = JSON.parse(snapshot)
      return false
    }
  }

  const moveTask = async (taskId: number, toColumnId: number): Promise<boolean> => {
    try {
      await apiUpdateTask(taskId, { column: toColumnId })
      return true
    } catch {
      return false
    }
  }

  const reorderTasks = async (tasks: Task[], columnId: number): Promise<boolean> => {
    const payload = tasks.map((t, i) => ({ id: t.id, position: i, column_id: columnId }))
    try {
      await apiReorderTasks({ tasks: payload })
      return true
    } catch {
      return false
    }
  }
  return {
    fullKanban,
    loading,
    error,
    allUsers,
    fetchBoard,
    fetchUsers,
    reset,
    connectWebSocket,
    disconnectWebSocket,
    createTask,
    updateTask,
    deleteTask,
    moveTask,
    reorderTasks,
  }
})
