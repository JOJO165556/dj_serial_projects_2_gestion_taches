import api from "@/api/axios";

export const getProjects = () => api.get("projects/");
export const getTasks = () => api.get("tasks/");
export const getColumns = () => api.get("columns/");
export const updateTask = (id: number, data: any) => api.patch(`tasks/${id}/`, data);
export const reorderTasks = (data: any) => api.patch("tasks/reorder/", data);
