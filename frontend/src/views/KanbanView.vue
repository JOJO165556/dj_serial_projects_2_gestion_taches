<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import draggable from "vuedraggable";
import { getProjects, getProjectKanban, updateTask, reorderTasks } from "@/services/kanbanService";

const projects = ref<any[]>([]);
const sockets = ref<{[key: number]: WebSocket}>({});

  // Filtres Kanban
const filters = ref({
  priority: '',
  deadline: '',
  overdue: false,
  search: '',
  assignee: ''
});

const applyFilters = () => {
  projects.value.forEach(p => {
    if (!p.fullKanban) return;
    
    // Creer une copie profonde pour l'affichage filtré
    const filteredBoard: Record<number | string, any[]> = {};
    const f = filters.value;
    
    for (const colId in p.fullKanban.board) {
      filteredBoard[colId] = p.fullKanban.board[colId].filter((task: any) => {
        // Priority
        if (f.priority && task.priority !== f.priority) return false;
        // Deadline
        if (f.deadline && task.due_date && !task.due_date.startsWith(f.deadline)) return false;
        // Search
        if (f.search && !task.title.toLowerCase().includes(f.search.toLowerCase())) return false;
        // Assignee
        if (f.assignee && task.assigned_to !== parseInt(f.assignee)) return false;
        // Overdue
        if (f.overdue) {
          if (!task.due_date) return false;
          if (new Date(task.due_date) >= new Date()) return false;
          // Ne pas afficher en retard si la tache est dans une colonne terminee
          const colName = p.fullKanban.columns.find((c: any) => c.id === Number(colId))?.name || '';
          if (colName.toLowerCase() === 'done') return false;
        }
        return true;
      });
    }
    
    p.kanban = {
      columns: p.fullKanban.columns,
      board: filteredBoard
    };
  });
};

const fetchProjects = async () => {
  try {
    const res = await getProjects();
    const projectsData = res.data;
    
    for (const p of projectsData) {
      const kRes = await getProjectKanban(p.id); // Sans filtres
      p.fullKanban = kRes.data;
      
      // Connexion WebSocket specifique a ce projet
      if (!sockets.value[p.id]) {
        const ws = new WebSocket(`ws://localhost:8000/ws/kanban/${p.id}/`);
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === 'update_board' && data.board_data) {
            p.fullKanban = data.board_data;
            applyFilters();
          }
        };
        sockets.value[p.id] = ws;
      }
    }
    
    projects.value = projectsData;
    applyFilters();
  } catch (err) {
    console.error("Erreur chargement projets", err);
  }
};

onMounted(() => {
  fetchProjects();
});

// Filtrage instantane (sans requete API)
watch(filters, () => {
  applyFilters();
}, { deep: true });

const onChange = async (event: any, columnId: number, project: any) => {
  if (event.added) {
    const task = event.added.element;
    
    // Sauvegarde de letat pour rollback
    const previousState = JSON.parse(JSON.stringify(projects.value));

    try {
      await updateTask(task.id, {
        column: columnId,
      });
    } catch (error) {
      console.error("Erreur lors de la mise à jour de la colonne:", error);
      projects.value = previousState;
      alert("Erreur lors de la mise à jour. Annulation.");
    }
  }
};

const onDragEnd = async (column: any, project: any) => {
  const tasksInColumn = project.kanban.board[column.id];
  if (!tasksInColumn || tasksInColumn.length === 0) return;

  const updatedTasks = tasksInColumn.map((task: any, index: number) => ({
    id: task.id,
    position: index,
    column_id: column.id
  }));

  const previousState = JSON.parse(JSON.stringify(projects.value));

  try {
    await reorderTasks({ tasks: updatedTasks });
  } catch (error) {
    console.error("Erreur lors de la réorganisation des tâches:", error);
    projects.value = previousState;
    alert("Erreur lors de la réorganisation. Annulation.");
  }
};

// Helpers pour lUI
const getPriorityColor = (priority: string) => {
  if (priority === 'high') return 'red';
  if (priority === 'medium') return 'orange';
  if (priority === 'low') return '#3b82f6'; // bleu
  return '#9ca3af'; // gris
};

const isOverdue = (dateString: string) => {
  if (!dateString) return false;
  return new Date(dateString) < new Date();
};
</script>

<template>
  <div>
    <h1>Kanban</h1>

    <!-- Barre de filtres -->
    <div class="filters-bar" style="margin-bottom: 20px; padding: 10px; background: #f3f4f6; border-radius: 8px; display: flex; gap: 15px; align-items: center;">
      <div>
        <label>Recherche: </label>
        <input v-model="filters.search" type="text" placeholder="Titre..." />
      </div>
      <div>
        <label>Priorité: </label>
        <select v-model="filters.priority">
          <option value="">Toutes</option>
          <option value="high">Haute</option>
          <option value="medium">Moyenne</option>
          <option value="low">Basse</option>
        </select>
      </div>
      <div>
        <label>Date Limite: </label>
        <input v-model="filters.deadline" type="date" />
      </div>
      <div>
        <label>Assigné (ID): </label>
        <input v-model="filters.assignee" type="number" placeholder="ID Utilisateur..." style="width: 120px;" />
      </div>
      <div>
        <label>
          <input v-model="filters.overdue" type="checkbox" /> En retard uniquement
        </label>
      </div>
    </div>

    <div v-for="project in projects" :key="project.id">
      <h2>{{ project.name }}</h2>
      <div style="display: flex; gap: 20px; overflow-x: auto; padding-bottom: 20px;" v-if="project.kanban">
        <div v-for="column in project.kanban.columns" :key="column.id" class="kanban-column" style="min-width: 300px; background: #f9fafb; padding: 15px; border-radius: 8px;">
          <h3 :style="{ borderBottom: '3px solid ' + (column.color || '#6366f1'), paddingBottom: '5px' }">{{ column.name }}</h3>

          <!-- Drag zone -->
          <draggable
            v-model="project.kanban.board[column.id]"
            group="tasks"
            @end="() => onDragEnd(column, project)"
            item-key="id"
            @change="(e: any) => onChange(e, column.id, project)"
            style="min-height: 50px;"
          >
            <template #item="{ element }">
              <div class="task-card" :style="{ borderLeft: '4px solid ' + getPriorityColor(element.priority) }" style="background: white; margin-bottom: 10px; padding: 10px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: grab;">
                <div style="font-weight: bold; margin-bottom: 5px;">{{ element.title }}</div>
                
                <div style="font-size: 0.85em; color: #6b7280; display: flex; justify-content: space-between; align-items: center;">
                  <span style="text-transform: capitalize; padding: 2px 6px; border-radius: 12px; font-size: 0.8em;" :style="{ background: getPriorityColor(element.priority), color: 'white' }">
                    {{ element.priority || 'Medium' }}
                  </span>
                  
                  <span v-if="element.due_date" :style="{ color: isOverdue(element.due_date) && column.name.toLowerCase() !== 'done' ? 'red' : 'inherit', fontWeight: isOverdue(element.due_date) && column.name.toLowerCase() !== 'done' ? 'bold' : 'normal' }">
                    {{ new Date(element.due_date).toLocaleDateString() }}
                  </span>
                </div>
              </div>
            </template>
          </draggable>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban-column {
  box-sizing: border-box;
}
.filters-bar input, .filters-bar select {
  padding: 5px;
  border-radius: 4px;
  border: 1px solid #d1d5db;
}
</style>