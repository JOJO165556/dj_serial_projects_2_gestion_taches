<script setup lang="ts">
import { ref, onMounted } from 'vue';
import draggable from "vuedraggable";
import { getProjects, updateTask } from "@/services/kanbanService";

const projects = ref<any[]>([]);

onMounted(async () => {
  const res = await getProjects();
  projects.value = res.data;
});

const onChange = async (event: any, columnId: number) => {
  if (event.added) {
    const task = event.added.element;

    await updateTask(task.id, {
      column: columnId,
    });
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