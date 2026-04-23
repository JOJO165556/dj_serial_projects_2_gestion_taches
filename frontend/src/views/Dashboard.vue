<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuthStore } from "../store/authStore";
import { getProjects, createProject, updateProject, deleteProject, addProjectMember, getUsers } from "../services/kanbanService";

const auth = useAuthStore();
const projects = ref<any[]>([]);
const loading = ref(true);
const error = ref("");

// État des fenêtres modales
const isCreateModalOpen = ref(false);
const newProject = ref({ name: "", description: "" });

const isEditModalOpen = ref(false);
const editProjectData = ref<any>(null);

const isAddMemberModalOpen = ref(false);
const selectedProjectId = ref<number | null>(null);
const allUsers = ref<any[]>([]);
const selectedUserId = ref<number | null>(null);
const generatedInviteLink = ref("");

const fetchProjects = async () => {
  try {
    loading.value = true;
    const res = await getProjects();
    projects.value = res.data;
  } catch {
    error.value = "Impossible de charger les projets";
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await fetchProjects();
  try {
    const res = await getUsers();
    allUsers.value = res.data;
  } catch (err) {
    console.error("Failed to load users", err);
  }
});

const handleCreateProject = async () => {
  if (!newProject.value.name.trim()) return;
  try {
    await createProject(newProject.value);
    isCreateModalOpen.value = false;
    newProject.value = { name: "", description: "" };
    await fetchProjects();
  } catch (err) {
    console.error(err);
  }
};

const handleEditProject = async () => {
  if (!editProjectData.value?.name.trim()) return;
  try {
    await updateProject(editProjectData.value.id, {
      name: editProjectData.value.name,
      description: editProjectData.value.description
    });
    isEditModalOpen.value = false;
    await fetchProjects();
  } catch (err) {
    console.error(err);
  }
};

const handleDeleteProject = async (id: number) => {
  if (!confirm("Voulez-vous vraiment supprimer ce projet ?")) return;
  try {
    await deleteProject(id);
    await fetchProjects();
  } catch (err) {
    console.error(err);
  }
};

const handleAddMember = async () => {
  if (!selectedProjectId.value || !selectedUserId.value) return;
  try {
    const res = await addProjectMember(selectedProjectId.value, selectedUserId.value);
    if (res.data && res.data.token) {
      const baseUrl = window.location.origin;
      generatedInviteLink.value = `${baseUrl}/invite/${res.data.token}`;
    }
    await fetchProjects();
  } catch (err: any) {
    console.error(err);
    alert(err.response?.data?.error || "Impossible de créer l'invitation.");
  }
};

const closeAddMemberModal = () => {
  isAddMemberModalOpen.value = false;
  selectedUserId.value = null;
  generatedInviteLink.value = "";
};

const openEditModal = (project: any) => {
  editProjectData.value = { ...project };
  isEditModalOpen.value = true;
};

const openAddMemberModal = (projectId: number) => {
  selectedProjectId.value = projectId;
  selectedUserId.value = null;
  isAddMemberModalOpen.value = true;
};

import { useRouter } from 'vue-router';

const router = useRouter();

const priorityColor: Record<string, string> = {
  high: "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400",
  medium: "bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400",
  low: "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400",
};
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

    <!-- En-tête -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          Mes Projets
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1 text-sm">
          Bienvenue, {{ auth.user?.username }}
        </p>
      </div>
      <button
        @click="isCreateModalOpen = true"
        class="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
      >
        + Nouveau Projet
      </button>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="i in 3" :key="i"
        class="h-40 rounded-2xl bg-gray-100 dark:bg-gray-800 animate-pulse"
      />
    </div>

    <!-- Erreur -->
    <p v-else-if="error" class="text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3 text-sm">
      {{ error }}
    </p>

    <!-- Aucun projet -->
    <div v-else-if="!projects.length" class="text-center py-20">
      <p class="text-gray-400 dark:text-gray-500 text-lg">Aucun projet disponible</p>
    </div>

    <!-- Liste des projets -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="project in projects"
        :key="project.id"
        @click="router.push(`/kanban/${project.id}`)"
        class="group cursor-pointer flex flex-col bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 hover:border-violet-300 dark:hover:border-violet-700 hover:shadow-lg transition-all duration-200 relative"
      >
        <!-- En-tête projet -->
        <div class="flex items-start justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors line-clamp-2 pr-8">
            {{ project.name }}
          </h2>
          <span class="shrink-0 text-xs px-2 py-1 rounded-full"
            :class="project.is_active
              ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'">
            {{ project.is_active ? 'Actif' : 'Archivé' }}
          </span>
        </div>

        <!-- Description -->
        <p v-if="project.description" class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-4">
          {{ project.description }}
        </p>

        <!-- Footer -->
        <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-100 dark:border-gray-800">
          <span class="text-xs text-gray-400 dark:text-gray-500">
            {{ project.members?.length || 0 }} membre(s)
          </span>
          <div class="flex gap-2">
            <button @click.stop="openAddMemberModal(project.id)" class="text-gray-400 hover:text-blue-500 p-1" title="Ajouter membre">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
            </button>
            <button @click.stop="openEditModal(project)" class="text-gray-400 hover:text-orange-500 p-1" title="Modifier">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
            </button>
            <button @click.stop="handleDeleteProject(project.id)" class="text-gray-400 hover:text-red-500 p-1" title="Supprimer">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Fenêtres modales -->
    <!-- Modale de création -->
    <div v-if="isCreateModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-900 rounded-2xl p-6 w-full max-w-md shadow-xl border border-gray-200 dark:border-gray-800">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Nouveau Projet</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nom</label>
            <input v-model="newProject.name" type="text" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
            <textarea v-model="newProject.description" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500" rows="3"></textarea>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="isCreateModalOpen = false" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">Annuler</button>
          <button @click="handleCreateProject" class="px-4 py-2 text-sm bg-violet-600 hover:bg-violet-700 text-white rounded-xl">Créer</button>
        </div>
      </div>
    </div>

    <!-- Modale d'édition -->
    <div v-if="isEditModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-900 rounded-2xl p-6 w-full max-w-md shadow-xl border border-gray-200 dark:border-gray-800">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Modifier Projet</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nom</label>
            <input v-model="editProjectData.name" type="text" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
            <textarea v-model="editProjectData.description" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500" rows="3"></textarea>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="isEditModalOpen = false" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">Annuler</button>
          <button @click="handleEditProject" class="px-4 py-2 text-sm bg-violet-600 hover:bg-violet-700 text-white rounded-xl">Sauvegarder</button>
        </div>
      </div>
    </div>

    <!-- Modale d'ajout de membre -->
    <div v-if="isAddMemberModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-900 rounded-2xl p-6 w-full max-w-md shadow-xl border border-gray-200 dark:border-gray-800">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Inviter un Membre</h2>
        
        <div v-if="!generatedInviteLink" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Utilisateur</label>
            <select v-model="selectedUserId" class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2.5 focus:ring-2 focus:ring-violet-500">
              <option :value="null" disabled>Sélectionner un utilisateur</option>
              <option v-for="u in allUsers" :key="u.id" :value="u.id">{{ u.username }} ({{ u.email }})</option>
            </select>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button @click="closeAddMemberModal" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">Annuler</button>
            <button @click="handleAddMember" class="px-4 py-2 text-sm bg-violet-600 hover:bg-violet-700 text-white rounded-xl">Générer l'invitation</button>
          </div>
        </div>

        <div v-else class="space-y-4">
          <div class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
            <p class="text-sm text-green-800 dark:text-green-300 font-medium mb-2">Invitation créée avec succès !</p>
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">Envoyez ce lien à l'utilisateur pour qu'il puisse rejoindre le projet :</p>
            <div class="flex gap-2">
              <input type="text" :value="generatedInviteLink" readonly class="w-full text-xs p-2 rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white" />
              <button @click="navigator.clipboard.writeText(generatedInviteLink)" class="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-xs font-medium">Copier</button>
            </div>
          </div>
          <div class="mt-6 flex justify-end">
            <button @click="closeAddMemberModal" class="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-xl">Fermer</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>