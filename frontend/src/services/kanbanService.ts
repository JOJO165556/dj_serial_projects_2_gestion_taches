import api from "@/api/axios";

// Utilisateurs
export const getUsers = () => api.get("users/");

// Projets
export const getProjects = () => api.get("projects/");
export const createProject = (data: any) => api.post("projects/", data);
export const updateProject = (id: number, data: any) => api.patch(`projects/${id}/`, data);
export const deleteProject = (id: number) => api.delete(`projects/${id}/`);
export const addProjectMember = (id: number, userId: number) => api.post(`projects/${id}/add_member/`, { user_id: userId });
export const getProjectKanban = (projectId: number | string, params: any = {}) => api.get(`projects/${projectId}/kanban/`, { params });

// Invitations
export const getInvitation = (token: string) => api.get(`projects/invitations/${token}/`);
export const respondToInvitation = (token: string, action: 'accept' | 'decline') => api.post(`projects/invitations/${token}/`, { action });

// Colonnes
export const getColumns = () => api.get("columns/");
export const updateColumn = (id: number, data: any) => api.patch(`columns/${id}/`, data);

// Tâches
export const getTasks = () => api.get("tasks/");
export const createTask = (data: any) => api.post("tasks/", data);
export const updateTask = (id: number, data: any) => api.patch(`tasks/${id}/`, data);
export const deleteTask = (id: number) => api.delete(`tasks/${id}/`);
export const reorderTasks = (data: any) => api.patch("tasks/reorder/", data);
