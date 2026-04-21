<script setup lang="ts">
import { ref, onMounted } from 'vue';
import draggable from "vuedraggable";
import { getProjects, updateTask, reorderTasks } from "@/services/kanbanService";

const projects = ref<any[]>([]);
let ws: WebSocket;

const fetchProjects = async () => {
  const res = await getProjects();
  projects.value = res.data;
};

onMounted(() => {
  fetchProjects();

  // Connexion WebSocket
  ws = new WebSocket("ws://localhost:8000/ws/kanban/");
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'update') {
      fetchProjects();
    }
  };
});

const onChange = async (event: any, columnId: number) => {
  if (event.added) {
    const task = event.added.element;
    
    // Sauvegarde de l'état pour rollback
    const previousState = JSON.parse(JSON.stringify(projects.value));

    try {
      await updateTask(task.id, {
        column: columnId,
      });
    } catch (error) {
      console.error("Erreur lors de la mise à jour de la colonne:", error);
      // Rollback
      projects.value = previousState;
      alert("Erreur lors de la mise à jour. Annulation.");
    }
  }
};

const onDragEnd = async (column: any) => {
  if (!column.tasks || column.tasks.length === 0) return;

  const updatedTasks = column.tasks.map((task: any, index: number) => ({
    id: task.id,
    position: index,
    column_id: column.id
  }));

  // Sauvegarde de l'état pour rollback
  const previousState = JSON.parse(JSON.stringify(projects.value));

  try {
    await reorderTasks({ tasks: updatedTasks });
  } catch (error) {
    console.error("Erreur lors de la réorganisation des tâches:", error);
    // Rollback
    projects.value = previousState;
    alert("Erreur lors de la réorganisation. Annulation.");
  }
};
</script>

<template>
  <div>
    <h1>Kanban</h1>

    <div v-for="project in projects" :key="project.id">
      <h2>{{ project.name }}</h2>
      <div style="display: flex; gap: 20px">
        <div v-for="column in project.columns" :key="column.id">
          <h3>{{ column.name }}</h3>

          <!-- Drag zone -->
          <draggable
          v-model="column.tasks"
          group="tasks"
          @end="() => onDragEnd(column)"
          item-key="id"
          @change="(e: any) => onChange(e, column.id)"
          >
            <template #item="{ element }">
              <div class="task-card">
                {{ element.title }}
              </div>
            </template>
          </draggable>

        </div>
      </div>
    </div>
  </div>
</template>