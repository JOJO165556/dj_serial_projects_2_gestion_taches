<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/store/authStore'
import { getFriendships } from '@/services/friendService'
import type { Friendship } from '@/services/friendService'
import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
  addProjectMember,
  getReceivedInvitations,
  respondToInvitation,
} from '@/services/kanbanService'
import type { Project, InvitationCreateResult } from '@/types/kanban'

// Import des nouveaux composants modulaires
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectFormModal from '@/components/ProjectFormModal.vue'
import InviteMemberModal from '@/components/InviteMemberModal.vue'

const auth = useAuthStore()

const projects = ref<Project[]>([])
const loading = ref(true)
const error = ref('')
const projectFilter = ref<'active' | 'archived' | 'all'>('active')

// État des modales
const createModal = ref(false)
const editModal = ref(false)
const memberModal = ref(false)

const editData = ref<Project | null>(null)
const selectedProjectId = ref<number | null>(null)
const submitting = ref(false)

// Gestion des invitations envoyées
const inviteResult = ref<InvitationCreateResult | null>(null)
const inviteLink = ref('')
const inviteError = ref('')
const myFriends = ref<Friendship[]>([])

// État des invitations reçues
const receivedInvitations = ref<any[]>([])

const fetchInvitations = async () => {
  try {
    const res = await getReceivedInvitations()
    receivedInvitations.value = res.data
  } catch {}
}

const handleInvitationResponse = async (token: string, action: 'accept' | 'decline') => {
  submitting.value = true
  try {
    await respondToInvitation(token, action)
    await fetchInvitations()
    await fetchProjects()
  } catch (e) {
    console.error("Erreur réponse invitation", e)
  } finally {
    submitting.value = false
  }
}

// Chargement des données
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
  await fetchInvitations()
  getFriendships().then(res => {
    myFriends.value = res.filter(f => f.status === 'accepted')
  }).catch(() => {})
})

// Filtrage des projets
const filteredProjects = computed(() => {
  if (projectFilter.value === 'all') return projects.value
  if (projectFilter.value === 'archived') return projects.value.filter((p) => !p.is_active)
  return projects.value.filter((p) => p.is_active)
})

// --- Actions sur les projets ---

const handleCreate = async (data: { name: string, description: string }) => {
  submitting.value = true
  try {
    await createProject(data)
    createModal.value = false
    await fetchProjects()
  } finally {
    submitting.value = false
  }
}

const handleEdit = async (data: { name: string, description: string }) => {
  if (!editData.value) return
  submitting.value = true
  try {
    await updateProject(editData.value.id, data)
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

const toggleArchive = async (project: Project) => {
  submitting.value = true
  try {
    await updateProject(project.id, { is_active: !project.is_active } as any)
    await fetchProjects()
  } finally {
    submitting.value = false
  }
}

// --- Gestion des invitations ---

const openMemberModal = (id: number) => {
  selectedProjectId.value = id
  inviteLink.value = ''
  inviteResult.value = null
  inviteError.value = ''
  memberModal.value = true
}

const handleInviteSubmit = async (data: { userId: number | null, email: string, message: string }) => {
  if (!selectedProjectId.value) return
  submitting.value = true
  inviteError.value = ''
  try {
    const payload: any = { message: data.message }
    if (data.userId) payload.user_id = data.userId
    else if (data.email) payload.email = data.email
    else {
      inviteError.value = "Veuillez sélectionner un ami ou entrer une adresse email."
      return
    }

    const res = await addProjectMember(selectedProjectId.value, payload)
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

// --- Helpers UI ---

const copiedToast = ref(false)
const copyWithFeedback = async (text: string) => {
  await navigator.clipboard.writeText(text)
  copiedToast.value = true
  setTimeout(() => { copiedToast.value = false }, 2500)
}

const openEditModal = (p: Project) => {
  editData.value = { ...p }
  editModal.value = true
}

// Formater les amis pour le composant d'invitation
const formattedFriends = computed(() => {
  return myFriends.value.map(f => {
    const profile = f.sender.id === auth.user?.id ? f.receiver : f.sender
    return {
      ...f,
      sender: { ...profile }
    }
  })
})
</script>

<template>
  <div class="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

    <!-- Section Invitations Reçues -->
    <div v-if="receivedInvitations.length" class="mb-8 space-y-3">
      <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider ml-1">Invitations en attente</h3>
      <div v-for="inv in receivedInvitations" :key="inv.token" 
           class="flex items-center justify-between p-4 bg-violet-50 dark:bg-violet-900/10 border border-violet-100 dark:border-violet-800 rounded-2xl">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 rounded-full bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center text-violet-600 font-bold">
            {{ inv.owner_username.charAt(0).toUpperCase() }}
          </div>
          <div>
            <p class="text-sm font-semibold text-gray-900 dark:text-white">
              {{ inv.owner_username }} vous invite sur <span class="text-violet-600">{{ inv.project_name }}</span>
            </p>
            <p v-if="inv.message" class="text-xs text-gray-500 italic mt-0.5">"{{ inv.message }}"</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button 
            @click="handleInvitationResponse(inv.token, 'decline')"
            :disabled="submitting"
            class="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 hover:text-red-600 transition-colors"
          >
            Refuser
          </button>
          <button 
            @click="handleInvitationResponse(inv.token, 'accept')"
            :disabled="submitting"
            class="px-4 py-1.5 text-xs font-bold bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors"
          >
            Accepter
          </button>
        </div>
      </div>
    </div>

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
            v-for="filter in ['active', 'archived', 'all'] as const"
            :key="filter"
            @click="projectFilter = filter"
            class="px-3 py-2 text-xs font-medium transition-colors capitalize"
            :class="projectFilter === filter ? 'bg-violet-600 text-white' : 'text-gray-600 dark:text-gray-300'"
          >
            {{ filter === 'active' ? 'Actifs' : filter === 'archived' ? 'Archives' : 'Tous' }}
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

    <!-- États de chargement et d'erreur -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <div v-for="i in 3" :key="i" class="h-44 rounded-2xl bg-gray-100 dark:bg-gray-800/60 animate-pulse" />
    </div>
    <div v-else-if="error" class="text-center py-16">
      <p class="text-sm text-red-500 dark:text-red-400 mb-3">{{ error }}</p>
      <button @click="fetchProjects" class="text-xs text-violet-600 dark:text-violet-400 hover:underline">Réessayer</button>
    </div>

    <!-- Liste des projets -->
    <div v-else-if="!filteredProjects.length" class="flex flex-col items-center justify-center py-24 text-center">
       <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Aucun projet trouvé</p>
       <button @click="createModal = true" class="text-sm font-medium text-violet-600 dark:text-violet-400 hover:underline">Créer un projet</button>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <ProjectCard 
        v-for="project in filteredProjects" 
        :key="project.id" 
        :project="project"
        @edit="openEditModal"
        @invite="openMemberModal"
        @archive="toggleArchive"
        @delete="handleDelete"
      />
    </div>

    <!-- Modales -->
    <ProjectFormModal 
      :show="createModal" 
      title="Nouveau projet" 
      :submitting="submitting"
      @close="createModal = false" 
      @submit="handleCreate" 
    />

    <ProjectFormModal 
      :show="editModal" 
      title="Modifier le projet" 
      :initial-data="editData || undefined"
      :submitting="submitting"
      @close="editModal = false" 
      @submit="handleEdit" 
    />

    <InviteMemberModal 
      :show="memberModal"
      :project-id="selectedProjectId"
      :friends="formattedFriends"
      :submitting="submitting"
      :invite-result="inviteResult"
      :invite-link="inviteLink"
      :invite-error="inviteError"
      @close="memberModal = false"
      @submit="handleInviteSubmit"
      @copy="copyWithFeedback"
    />

    <!-- Toasts -->
    <Teleport to="body">
      <Transition name="toast-slide">
        <div v-if="copiedToast" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-3 bg-gray-900 text-white text-sm rounded-xl shadow-xl">
          Lien copié !
        </div>
      </Transition>
    </Teleport>
    <Teleport to="body">
      <Transition name="toast-slide">
        <div v-if="permError" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-3 bg-red-600 text-white text-sm rounded-xl shadow-xl">
          Seul le propriétaire peut supprimer ce projet.
        </div>
      </Transition>
    </Teleport>

  </div>
</template>
