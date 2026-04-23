<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import draggable from "vuedraggable";
import { getProjectKanban, updateTask, reorderTasks, createTask, deleteTask, updateColumn, getUsers } from "@/services/kanbanService";
const route = useRoute();
const projectId = computed(() => Number(route.params.id));

const fullKanban = ref<any>(null);
const loading = ref(true);
const error = ref("");
let ws: WebSocket | null = null;

const allUsers = ref<any[]>([]);
const isTaskModalOpen = ref(false);
const editTaskData = ref<any>(null);

const editingColumnId = ref<number | null>(null);
const editColumnName = ref("");

const newTaskForms = ref<Record<number, { title: string, priority: string, show: boolean }>>({});

const initTaskForms = () => {
  if (fullKanban.value?.columns) {
    fullKanban.value.columns.forEach((col: any) => {
      if (!newTaskForms.value[col.id]) {
        newTaskForms.value[col.id] = { title: '', priority: 'medium', show: false };
      }
    });
  }
};

// Filtres locaux (zero requete supplementaire)
const filters = ref({ search: '', priority: '', overdue: false, assignee: '' });

// Board filtre cote client
const filteredKanban = computed(() => {
  if (!fullKanban.value) return null;
  const f = filters.value;
  const filteredBoard: Record<string | number, any[]> = {};

  for (const colId in fullKanban.value.board) {
    filteredBoard[colId] = fullKanban.value.board[colId].filter((task: any) => {
      if (f.priority && task.priority !== f.priority) return false;
      if (f.search && !task.title.toLowerCase().includes(f.search.toLowerCase())) return false;
      if (f.assignee && task.assigned_to !== parseInt(f.assignee)) return false;
      if (f.overdue) {
        if (!task.due_date) return false;
        if (new Date(task.due_date) >= new Date()) return false;
        const col = fullKanban.value.columns.find((c: any) => c.id === Number(colId));
        if (col?.name?.toLowerCase() === 'done') return false;
      }
      return true;
    });
  }

  return { columns: fullKanban.value.columns, board: filteredBoard };
});

const fetchKanban = async () => {
  try {
    const res = await getProjectKanban(projectId.value);
    fullKanban.value = res.data;
    initTaskForms();
  } catch {
    error.value = "Impossible de charger le board";
  } finally {
    loading.value = false;
  }
};

const connectWebSocket = () => {
  if (ws) ws.close();
  ws = new WebSocket(`ws://localhost:8000/ws/kanban/${projectId.value}/`);
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'update_board' && data.board_data) {
      fullKanban.value = data.board_data;
      initTaskForms();
    }
  };
};

onMounted(async () => {
  await fetchKanban();
  connectWebSocket();
  try {
    const res = await getUsers();
    allUsers.value = res.data;
  } catch (e) {
    console.error("Failed to load users", e);
  }
});

watch(projectId, async () => {
  loading.value = true;
  await fetchKanban();
  connectWebSocket();
});

const onChange = async (event: any, columnId: number) => {
  if (event.added) {
    const previousState = JSON.parse(JSON.stringify(fullKanban.value));
    try {
      await updateTask(event.added.element.id, { column: columnId });
    } catch {
      fullKanban.value = previousState;
    }
  }
};

const onDragEnd = async (column: any) => {
  if (!filteredKanban.value) return;
  const tasks = filteredKanban.value.board[column.id];
  if (!tasks?.length) return;
  const updatedTasks = tasks.map((t: any, i: number) => ({ id: t.id, position: i, column_id: column.id }));
  const previousState = JSON.parse(JSON.stringify(fullKanban.value));
  try {
    await reorderTasks({ tasks: updatedTasks });
  } catch {
    fullKanban.value = previousState;
  }
};

const priorityColor: Record<string, string> = {
  high: 'border-red-400 dark:border-red-500',
  medium: 'border-orange-400 dark:border-orange-500',
  low: 'border-blue-400 dark:border-blue-500',
};

const priorityBadge: Record<string, string> = {
  high: 'bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400',
  medium: 'bg-orange-100 dark:bg-orange-900/40 text-orange-600 dark:text-orange-400',
  low: 'bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400',
};

const isOverdue = (dateStr: string, colName: string) => {
  if (!dateStr || colName?.toLowerCase() === 'done') return false;
  return new Date(dateStr) < new Date();
};

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });

const submitCreateTask = async (columnId: number) => {
  const form = newTaskForms.value[columnId];
  if (!form || !form.title.trim()) return;

  try {
    await createTask({
      project: projectId.value,
      column: columnId,
      title: form.title,
      priority: form.priority
    });
    form.title = '';
    form.show = false;
  } catch (err) {
    console.error("Failed to create task", err);
  }
};

const handleDeleteTask = async (taskId: number) => {
  if (!confirm("Voulez-vous vraiment supprimer cette tâche ?")) return;
  try {
    await deleteTask(taskId);
  } catch (err) {
    console.error("Failed to delete task", err);
  }
};

const openTaskModal = (task: any) => {
  editTaskData.value = { ...task, due_date: task.due_date ? task.due_date.split('T')[0] : null };
  isTaskModalOpen.value = true;
};

const handleSaveTaskDetails = async () => {
  if (!editTaskData.value) return;
  try {
    const dataToSave = {
      title: editTaskData.value.title,
      description: editTaskData.value.description,
      priority: editTaskData.value.priority,
      due_date: editTaskData.value.due_date || null,
      assigned_to: editTaskData.value.assigned_to || null
    };
    await updateTask(editTaskData.value.id, dataToSave);
    isTaskModalOpen.value = false;
  } catch (err) {
    console.error("Failed to update task", err);
  }
};

const startEditColumn = (column: any) => {
  editingColumnId.value = column.id;
  editColumnName.value = column.name;
};

const saveColumnName = async (columnId: number) => {
  if (!editColumnName.value.trim()) {
    editingColumnId.value = null;
    return;
  }
  try {
    await updateColumn(columnId, { name: editColumnName.value });
    editingColumnId.value = null;
  } catch (err) {
    console.error("Failed to update column", err);
  }
};
</script>

<template>
  <div class="px-4 sm:px-6 lg:px-8 py-6">

    <!-- En-tête + filtres -->
    <div class="mb-6 space-y-4">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Board Kanban</h1>

      <div class="flex flex-wrap gap-3 items-center">
        <input
          v-model="filters.search"
          type="text"
          placeholder="Rechercher..."
          class="px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
        />
        <select
          v-model="filters.priority"
          class="px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
        >
          <option value="">Toutes priorités</option>
          <option value="high">Haute</option>
          <option value="medium">Moyenne</option>
          <option value="low">Basse</option>
        </select>
        <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer select-none">
          <input v-model="filters.overdue" type="checkbox" class="rounded accent-violet-600" />
          En retard uniquement
        </label>
        <button
          v-if="filters.search || filters.priority || filters.overdue || filters.assignee"
          @click="filters = { search: '', priority: '', overdue: false, assignee: '' }"
          class="text-xs text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 transition"
        >
          Réinitialiser
        </button>
      </div>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="flex gap-5 overflow-x-auto pb-4">
      <div v-for="i in 3" :key="i" class="min-w-72 h-96 rounded-2xl bg-gray-100 dark:bg-gray-800 animate-pulse shrink-0" />
    </div>

    <!-- Erreur -->
    <p v-else-if="error" class="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3">
      {{ error }}
    </p>

    <!-- Board -->
    <div v-else-if="filteredKanban" class="flex gap-5 overflow-x-auto pb-6">
      <div
        v-for="column in filteredKanban.columns"
        :key="column.id"
        class="min-w-72 w-72 shrink-0 flex flex-col bg-gray-50 dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800"
      >
        <!-- En-tête colonne -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800">
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <span
              class="w-2.5 h-2.5 rounded-full shrink-0"
              :style="{ backgroundColor: column.color || '#6366f1' }"
            />
            <div v-if="editingColumnId === column.id" class="flex-1 flex gap-1 items-center">
              <input
                v-model="editColumnName"
                @keyup.enter="saveColumnName(column.id)"
                @keyup.esc="editingColumnId = null"
                class="w-full text-sm font-semibold bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-violet-500"
                autofocus
              />
              <button @click="saveColumnName(column.id)" class="text-green-500 hover:text-green-600"><svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg></button>
              <button @click="editingColumnId = null" class="text-red-500 hover:text-red-600"><svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg></button>
            </div>
            <h3 v-else class="font-semibold text-sm text-gray-800 dark:text-gray-100 truncate flex-1 flex items-center group/title cursor-pointer" @click="startEditColumn(column)">
              {{ column.name }}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-1 text-gray-400 opacity-0 group-hover/title:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
            </h3>
          </div>
          <span class="text-xs font-medium text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">
            {{ filteredKanban.board[column.id]?.length || 0 }}
          </span>
        </div>

        <!-- Zone draggable -->
        <draggable
          v-model="filteredKanban.board[column.id]"
          group="tasks"
          item-key="id"
          @end="() => onDragEnd(column)"
          @change="(e: any) => onChange(e, column.id)"
          class="flex-1 p-3 space-y-2.5 min-h-[120px]"
        >
          <template #item="{ element }">
            <div
              @click="openTaskModal(element)"
              class="group bg-white dark:bg-gray-800 rounded-xl border-l-4 border border-gray-200 dark:border-gray-700 p-3.5 cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow"
              :class="priorityColor[element.priority] || 'border-l-gray-300'"
            >
              <!-- Titre et Actions -->
              <div class="flex justify-between items-start gap-2 mb-2">
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100 leading-snug break-words">
                  {{ element.title }}
                </p>
                <button
                  @click.stop="handleDeleteTask(element.id)"
                  class="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1 flex-shrink-0"
                  title="Supprimer la tâche"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>

              <!-- Badges en pied de carte -->
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <span
                  v-if="element.priority"
                  class="text-xs px-2 py-0.5 rounded-full font-medium capitalize"
                  :class="priorityBadge[element.priority]"
                >
                  {{ element.priority === 'high' ? 'Haute' : element.priority === 'medium' ? 'Moyenne' : 'Basse' }}
                </span>

                <span
                  v-if="element.due_date"
                  class="text-xs font-medium"
                  :class="isOverdue(element.due_date, column.name)
                    ? 'text-red-600 dark:text-red-400'
                    : 'text-gray-400 dark:text-gray-500'"
                >
                  {{ formatDate(element.due_date) }}
                  <span v-if="isOverdue(element.due_date, column.name)"> - En retard</span>
                </span>
              </div>
            </div>
          </template>
        </draggable>

        <!-- Ajouter une tâche -->
        <div class="p-3 border-t border-gray-200 dark:border-gray-800">
          <button
            v-if="newTaskForms[column.id] && !newTaskForms[column.id].show"
            @click="newTaskForms[column.id].show = true"
            class="flex items-center gap-2 text-sm text-gray-500 hover:text-violet-600 dark:text-gray-400 dark:hover:text-violet-400 transition-colors w-full p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Ajouter une tâche
          </button>
          
          <div v-else-if="newTaskForms[column.id]" class="space-y-2">
            <input
              v-model="newTaskForms[column.id].title"
              type="text"
              placeholder="Titre de la tâche..."
              class="w-full text-sm p-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
              @keyup.enter="submitCreateTask(column.id)"
            />
            <div class="flex items-center gap-2">
              <select
                v-model="newTaskForms[column.id].priority"
                class="text-xs p-1.5 rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              >
                <option value="low">Basse</option>
                <option value="medium">Moyenne</option>
                <option value="high">Haute</option>
              </select>
              <div class="flex-1"></div>
              <button
                @click="newTaskForms[column.id].show = false; newTaskForms[column.id].title = ''"
                class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                Annuler
              </button>
              <button
                @click="submitCreateTask(column.id)"
                class="text-xs bg-violet-600 hover:bg-violet-700 text-white px-3 py-1.5 rounded-lg transition-colors"
              >
                Ajouter
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modale de détails de tâche -->
    <div v-if="isTaskModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-900 rounded-2xl p-6 w-full max-w-lg shadow-xl border border-gray-200 dark:border-gray-800">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Détails de la tâche</h2>
          <button @click="isTaskModalOpen = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Titre</label>
            <input v-model="editTaskData.title" type="text" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
            <textarea v-model="editTaskData.description" rows="4" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500"></textarea>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priorité</label>
              <select v-model="editTaskData.priority" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500">
                <option value="low">Basse</option>
                <option value="medium">Moyenne</option>
                <option value="high">Haute</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date limite</label>
              <input v-model="editTaskData.due_date" type="date" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500" />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Assigné à</label>
            <select v-model="editTaskData.assigned_to" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500">
              <option :value="null">Non assigné</option>
              <option v-for="user in allUsers" :key="user.id" :value="user.id">{{ user.username }}</option>
            </select>
          </div>
        </div>
        
        <div class="mt-6 flex justify-end gap-3">
          <button @click="isTaskModalOpen = false" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">Annuler</button>
          <button @click="handleSaveTaskDetails" class="px-4 py-2 text-sm bg-violet-600 hover:bg-violet-700 text-white rounded-xl">Enregistrer</button>
        </div>
      </div>
    </div>

  </div>
</template>