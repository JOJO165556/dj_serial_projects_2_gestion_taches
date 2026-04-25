import type { User } from './auth'

export type Priority = 'low' | 'medium' | 'high'
export type InvitationStatus = 'pending' | 'accepted' | 'declined'

export interface Project {
  id: number
  name: string
  description: string
  owner: User
  members: User[]
  is_active: boolean
  start_date: string
  end_date: string | null
  created_at: string
  updated_at: string
}

export interface Column {
  id: number
  name: string
  order: number
  color: string
  project: number
}

export interface Task {
  id: number
  title: string
  description: string
  priority: Priority
  position: number
  due_date: string | null
  assigned_to: number | null
  column: number | null
  project: number
  created_at: string
  updated_at: string
}

export interface KanbanBoard {
  project: Project
  columns: Column[]
  board: Record<number, Task[]>
}

export interface Invitation {
  token: string
  project: Pick<Project, 'id' | 'name' | 'description'>
  owner: User
  user: User
  status: InvitationStatus
}

export interface InvitationCreateResult {
  message: string
  token: string
  email_sent: boolean
  email_error: string | null
}

export interface CreateTaskData {
  title: string
  project: number
  column: number
  priority?: Priority
}

export interface UpdateTaskData {
  title?: string
  description?: string
  priority?: Priority
  due_date?: string | null
  assigned_to?: number | null
  column?: number
}

export interface CreateColumnData {
  project: number
  name: string
  color?: string
  order?: number
}
