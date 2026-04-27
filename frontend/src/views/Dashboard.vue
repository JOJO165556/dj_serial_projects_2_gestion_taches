<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
  addProjectMember,
  getUsers,
} from '@/services/kanbanService'
import AppModal from '@/components/AppModal.vue'
import type { Project, InvitationCreateResult } from '@/types/kanban'
import type { User } from '@/types/auth'

const auth = useAuthStore()
const router = useRouter()

const projects = ref<Project[]>([])
const allUsers = ref<User[]>([])
const loading = ref(true)
const error = ref('')
const projectFilter = ref<'active' | 'archived' | 'all'>('active')

// Modales
const createModal = ref(false)
const editModal = ref(false)
const memberModal = ref(false)

const newProject = ref({ name: '', description: '' })
const editData = ref<Partial<Project & { id: number }> | null>(null)
const selectedProjectId = ref<number | null>(null)
const selectedUserId = ref<number | null>(null)
const inviteMessage = ref('')
const inviteLink = ref('')
const inviteResult = ref<InvitationCreateResult | null>(null)
const inviteError = ref('')
const submitting = ref(false)

const fetchProjects = async () => {
  try {
    loading.value = true
    const res = await getProjects()
    projects.value = res.data
  } catch {
    error.value = 'Impossible de charger les projets'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchProjects()
  try {
    const res = await getUsers()
    allUsers.value = res.data
  } catch (e) {
    console.error('Chargement utilisateurs', e)
  }
})

const filteredProjects = computed(() => {
  if (projectFilter.value === 'all') return projects.value
  if (projectFilter.value === 'archived') return projects.value.filter((project) => !project.is_active)
  return projects.value.filter((project) => project.is_active)
})

const handleCreate = async () => {
  if (!newProject.value.name.trim()) return
  submitting.value = true
  try {
    await createProject(newProject.value)
    createModal.value = false
    newProject.value = { name: '', description: '' }
    await fetchProjects()
  } finally {
    submitting.value = false
  }
}

const handleEdit = async () => {
  if (!editData.value?.id || !editData.value.name?.trim()) return
  submitting.value = true
  try {
    await updateProject(editData.value.id, {
      name: editData.value.name,
      description: editData.value.description,
    })
    editModal.value = false
    await fetchProjects()
  } finally {
    submitting.value = false
  }
}

const permError = ref(false)

const handleDelete = async (id: number, ownerId: number) => {
  if (auth.user?.id !== ownerId) {
    permError.value = true
    setTimeout(() => { permError.value = false }, 3000)
    return
  }
  if (!confirm('Supprimer ce projet définitivement ?')) return
  await deleteProject(id)
  await fetchProjects()
}

const handleAddMember = async () => {
  if (!selectedProjectId.value || !selectedUserId.value) return
  submitting.value = true
  inviteError.value = ''
  try {
    const res = await addProjectMember(selectedProjectId.value, {
      userId: selectedUserId.value,
      message: inviteMessage.value.trim(),
    })
    inviteResult.value = res.data
    if (res.data?.token) {
      inviteLink.value = `${window.location.origin}/invite/${res.data.token}`
    }
    await fetchProjects()
  } catch (e: any) {
    inviteError.value = e.response?.data?.error ?? "Impossible de créer l'invitation."
  } finally {
    submitting.value = false
  }
}

const openEditModal = (p: Project) => {
  editData.value = { ...p }
  editModal.value = true
}

const openMemberModal = (id: number) => {
  selectedProjectId.value = id
  selectedUserId.value = null
  inviteMessage.value = ''
  inviteLink.value = ''
  inviteResult.value = null
  inviteError.value = ''
  memberModal.value = true
}

const toggleArchive = async (project: Project) => {
  submitting.value = true
  try {
    await updateProject(project.id, { is_active: !project.is_active } as Partial<Project & { is_active: boolean }>)
    await fetchProjects()
  } finally {
    submitting.value = false
  }
}

const copiedToast = ref(false)
const copyToClipboard = (text: string) => navigator.clipboard.writeText(text)
const copyWithFeedback = async (text: string) => {
  await copyToClipboard(text)
  copiedToast.value = true
  setTimeout(() => { copiedToast.value = false }, 2500)
}

const closeMemberModal = () => {
  memberModal.value = false
  inviteLink.value = ''
  selectedUserId.value = null
  inviteMessage.value = ''
  inviteResult.value = null
  inviteError.value = ''
}

// Couleur de bande par projet (déterministe)
const bandColors = [
  'from-violet-500 to-indigo-500',
  'from-blue-500 to-cyan-500',
  'from-emerald-500 to-teal-500',
  'from-orange-500 to-amber-500',
  'from-rose-500 to-pink-500',
  'from-purple-500 to-violet-500',
]
const getBandColor = (id: number) => bandColors[id % bandColors.length]
</script>

<template>
  <div class="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

    <!-- En-tête -->
    <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
      <div class="min-w-0">
        <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1 truncate">
          {{ auth.user?.username }}
        </p>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
          Mes Projets
        </h1>
      </div>
      <div class="flex flex-col sm:flex-row gap-2 sm:items-center self-start sm:self-auto w-full sm:w-auto">
        <div class="grid grid-cols-3 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden bg-white dark:bg-gray-900">
          <button
            @click="projectFilter = 'active'"
            class="px-3 py-2 text-xs font-medium transition-colors"
            :class="projectFilter === 'active' ? 'bg-violet-600 text-white' : 'text-gray-600 dark:text-gray-300'"
          >
            Actifs
          </button>
          <button
            @click="projectFilter = 'archived'"
            class="px-3 py-2 text-xs font-medium transition-colors"
            :class="projectFilter === 'archived' ? 'bg-violet-600 text-white' : 'text-gray-600 dark:text-gray-300'"
          >
            Archives
          </button>
          <button
            @click="projectFilter = 'all'"
            class="px-3 py-2 text-xs font-medium transition-colors"
            :class="projectFilter === 'all' ? 'bg-violet-600 text-white' : 'text-gray-600 dark:text-gray-300'"
          >
            Tous
          </button>
        </div>
        <button
          @click="createModal = true"
          class="flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-700 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-colors shadow-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Nouveau projet
        </button>
      </div>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <div v-for="i in 3" :key="i" class="h-44 rounded-2xl bg-gray-100 dark:bg-gray-800/60 animate-pulse" />
    </div>

    <!-- Erreur -->
    <div v-else-if="error" class="text-center py-16">
      <p class="text-sm text-red-500 dark:text-red-400 mb-3">{{ error }}</p>
      <button @click="fetchProjects" class="text-xs text-violet-600 dark:text-violet-400 hover:underline">Réessayer</button>
    </div>

    <!-- Vide -->
    <div v-else-if="!filteredProjects.length" class="flex flex-col items-center justify-center py-24 text-center">
      <div class="w-16 h-16 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-gray-300 dark:text-gray-600">
          <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
        </svg>
      </div>
      <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Aucun projet dans ce filtre</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mb-4">Ajustez le filtre ou créez un nouveau projet</p>
      <button
        @click="createModal = true"
        class="text-sm font-medium text-violet-600 dark:text-violet-400 hover:underline"
      >
        Créer un projet
      </button>
    </div>

    <!-- Grille projets -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <div
        v-for="project in filteredProjects"
        :key="project.id"
        @click="router.push(`/kanban/${project.id}`)"
        class="group relative flex flex-col bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden cursor-pointer hover:border-violet-200 dark:hover:border-violet-800 hover:shadow-card-hover transition-all duration-200"
        :class="project.is_active ? '' : 'opacity-85'"
      >
        <!-- Bande de couleur -->
        <div class="h-1 bg-gradient-to-r" :class="getBandColor(project.id)" />

        <div class="p-5 flex flex-col flex-1">
          <!-- En-tête -->
          <div class="flex items-start justify-between gap-2 mb-3">
            <h2 class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors leading-tight line-clamp-2 flex-1">
              {{ project.name }}
            </h2>
            <span
              class="shrink-0 text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-md"
              :class="project.is_active
                ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-400'"
            >
              {{ project.is_active ? 'Actif' : 'Archivé' }}
            </span>
          </div>

          <!-- Description -->
          <p v-if="project.description" class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 flex-1 leading-relaxed">
            {{ project.description }}
          </p>
          <div v-else class="flex-1" />

          <!-- Footer carte -->
          <div class="flex items-center justify-between gap-3 mt-4 pt-3 border-t border-gray-100 dark:border-gray-800">
            <!-- Avatars membres -->
            <div class="flex -space-x-1.5">
              <div
                v-for="member in project.members.slice(0, 4)"
                :key="member.id"
                class="w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 text-[9px] font-bold flex items-center justify-center ring-2 ring-white dark:ring-gray-900"
                :title="member.username"
              >
                {{ member.username.slice(0, 2).toUpperCase() }}
              </div>
              <div
                v-if="project.members.length > 4"
                class="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 text-[9px] font-bold flex items-center justify-center ring-2 ring-white dark:ring-gray-900"
              >
                +{{ project.members.length - 4 }}
              </div>
            </div>

            <!-- Actions propriétaire (sauf supprimer) -->
            <div v-if="project.owner.id === auth.user?.id" class="flex gap-1 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity shrink-0">
              <button
                v-if="project.is_active"
                @click.stop="openMemberModal(project.id)"
                class="p-1.5 rounded-md text-gray-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                title="Inviter un membre"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
                  <line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/>
                </svg>
              </button>
              <button
                @click.stop="openEditModal(project)"
                class="p-1.5 rounded-md text-gray-400 hover:text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                title="Modifier"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button
                @click.stop="toggleArchive(project)"
                class="p-1.5 rounded-md text-gray-400 hover:text-violet-500 hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors"
                :title="project.is_active ? 'Archiver' : 'Reactiver'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8h14v10a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V8Z"/><path d="m10 12 2 2 2-2"/>
                </svg>
              </button>
            </div>
            <!-- Bouton supprimer visible à tous les membres -->
            <button
              @click.stop="handleDelete(project.id, project.owner.id)"
              class="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors opacity-100 sm:opacity-0 sm:group-hover:opacity-100"
              title="Supprimer"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modale création -->
    <AppModal v-if="createModal" title="Nouveau projet" @close="createModal = false">
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Nom *</label>
          <input
            v-model="newProject.name"
            type="text"
            placeholder="Mon projet..."
            autofocus
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
            @keyup.enter="handleCreate"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Description</label>
          <textarea
            v-model="newProject.description"
            rows="3"
            placeholder="Description optionnelle..."
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none"
          />
        </div>
      </div>
      <template #footer>
        <button @click="createModal = false" class="w-full sm:w-auto px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">Annuler</button>
        <button @click="handleCreate" :disabled="submitting || !newProject.name.trim()" class="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors">
          {{ submitting ? 'Création...' : 'Créer' }}
        </button>
      </template>
    </AppModal>

    <!-- Modale édition -->
    <AppModal v-if="editModal && editData" title="Modifier le projet" @close="editModal = false">
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Nom</label>
          <input
            v-model="editData.name"
            type="text"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Description</label>
          <textarea
            v-model="editData.description"
            rows="3"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none"
          />
        </div>
      </div>
      <template #footer>
        <button @click="editModal = false" class="w-full sm:w-auto px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">Annuler</button>
        <button @click="handleEdit" :disabled="submitting" class="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors">
          {{ submitting ? 'Sauvegarde...' : 'Sauvegarder' }}
        </button>
      </template>
    </AppModal>

    <!-- Modale invitation -->
    <AppModal v-if="memberModal" title="Inviter un membre" @close="closeMemberModal">
      <!-- Lien généré -->
      <div v-if="inviteLink" class="space-y-4">
        <div class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
          <p class="text-sm font-medium text-green-700 dark:text-green-400 mb-2">Invitation créée</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
            {{ inviteResult?.email_sent
              ? "L'email d'invitation a bien été envoyé."
              : "Le lien est prêt. Vous pouvez le transmettre manuellement si besoin." }}
          </p>
          <div class="flex flex-col sm:flex-row gap-2">
            <input
              :value="inviteLink"
              readonly
              class="flex-1 text-xs px-2.5 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none"
            />
            <button
              @click="copyWithFeedback(inviteLink)"
              class="px-3 py-2 text-xs font-medium rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors shrink-0"
            >
              Copier
            </button>
          </div>
          <p
            v-if="inviteResult && !inviteResult.email_sent"
            class="mt-3 text-xs text-amber-700 dark:text-amber-400"
          >
            {{ inviteResult.email_error || "Aucun envoi SMTP n'a été confirmé par le serveur." }}
          </p>
        </div>
      </div>

      <!-- Formulaire -->
      <div v-else class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Utilisateur</label>
          <select
            v-model="selectedUserId"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
          >
            <option :value="null" disabled>Sélectionner un utilisateur</option>
            <option v-for="u in allUsers" :key="u.id" :value="u.id">
              {{ u.username }} — {{ u.email }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Message</label>
          <textarea
            v-model="inviteMessage"
            rows="4"
            placeholder="Ajoutez un petit contexte pour l'invitation..."
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none"
          />
        </div>
        <p
          v-if="inviteError"
          class="text-sm text-red-500 dark:text-red-400"
        >
          {{ inviteError }}
        </p>
      </div>

      <template #footer>
        <button @click="closeMemberModal" class="w-full sm:w-auto px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
          {{ inviteLink ? 'Fermer' : 'Annuler' }}
        </button>
        <button
          v-if="!inviteLink"
          @click="handleAddMember"
          :disabled="submitting || !selectedUserId"
          class="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 transition-colors"
        >
          {{ submitting ? 'Envoi...' : "Envoyer l'invitation" }}
        </button>
      </template>
    </AppModal>

  </div>

  <!-- Toast "Lien copié" -->
  <Teleport to="body">
    <Transition name="toast-slide">
      <div
        v-if="copiedToast"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2.5 px-4 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-sm font-medium rounded-xl shadow-xl"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        Lien copié dans le presse-papier !
      </div>
    </Transition>
  </Teleport>

  <!-- Toast erreur de permission -->
  <Teleport to="body">
    <Transition name="toast-slide">
      <div
        v-if="permError"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2.5 px-4 py-3 bg-red-600 text-white text-sm font-medium rounded-xl shadow-xl whitespace-nowrap"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        Seul le propriétaire du projet peut le supprimer.
      </div>
    </Transition>
  </Teleport>

</template>

