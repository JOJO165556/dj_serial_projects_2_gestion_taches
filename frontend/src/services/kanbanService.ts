import api from '@/api/axios'
import type { CreateTaskData, UpdateTaskData } from '@/types/kanban'

// Utilisateurs
export const getUsers = () =>
  api.get('users/')

// Projets
export const getProjects = () =>
  api.get('projects/')

export const createProject = (data: { name: string; description: string }) =>
  api.post('projects/', data)

export const updateProject = (id: number, data: Partial<{ name: string; description: string }>) =>
  api.patch(`projects/${id}/`, data)

export const deleteProject = (id: number) =>
  api.delete(`projects/${id}/`)

export const addProjectMember = (id: number, data: { userId: number; message?: string }) =>
  api.post(`projects/${id}/add_member/`, {
    user_id: data.userId,
    message: data.message ?? '',
  })

export const getProjectKanban = (projectId: number | string, params: Record<string, unknown> = {}) =>
  api.get(`projects/${projectId}/kanban/`, { params })

// Invitations
export const getInvitation = (token: string) =>
  api.get(`projects/invitations/${token}/`)

export const respondToInvitation = (token: string, action: 'accept' | 'decline') =>
  api.post(`projects/invitations/${token}/`, { action })

// Tâches
export const createTask = (data: CreateTaskData) =>
  api.post('tasks/', data)

export const updateTask = (id: number, data: UpdateTaskData) =>
  api.patch(`tasks/${id}/`, data)

export const deleteTask = (id: number) =>
  api.delete(`tasks/${id}/`)

export const reorderTasks = (data: { tasks: { id: number; position: number; column_id: number }[] }) =>
  api.patch('tasks/reorder/', data)
