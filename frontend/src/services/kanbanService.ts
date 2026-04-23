import api from "@/api/axios";

export const getProjects = () => api.get("projects/");
export const getTasks = () => api.get("tasks/");
export const getColumns = () => api.get("columns/");
export const getProjectKanban = (projectId: number | string, params: any = {}) => api.get(`projects/${projectId}/kanban/`, { params });
export const updateTask = (id: number, data: any) => api.patch(`tasks/${id}/`, data);
export const reorderTasks = (data: any) => api.patch("tasks/reorder/", data);
