<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Project } from '@/types/kanban'
import { useAuthStore } from '@/store/authStore'

// Propriétés reçues (Props)
const props = defineProps<{
  project: Project
}>()

// Événements envoyés (Emits)
const emit = defineEmits<{
  (e: 'edit', project: Project): void
  (e: 'invite', id: number): void
  (e: 'archive', project: Project): void
  (e: 'delete', id: number, ownerId: number): void
}>()

const router = useRouter()
const auth = useAuthStore() // Pour vérifier si on est propriétaire

// Couleurs de bande par projet 
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
  <div
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

        <!-- Actions propriétaire -->
        <div v-if="project.owner.id === auth.user?.id" class="flex gap-1 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity shrink-0">
          <button
            v-if="project.is_active"
            @click.stop="emit('invite', project.id)"
            class="p-1.5 rounded-md text-gray-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
            title="Inviter un membre"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
              <line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/>
            </svg>
          </button>
          <button
            @click.stop="emit('edit', project)"
            class="p-1.5 rounded-md text-gray-400 hover:text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
            title="Modifier"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          <button
            @click.stop="emit('archive', project)"
            class="p-1.5 rounded-md text-gray-400 hover:text-violet-500 hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors"
            :title="project.is_active ? 'Archiver' : 'Réactiver'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8h14v10a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V8Z"/><path d="m10 12 2 2 2-2"/>
            </svg>
          </button>
          <button
            @click.stop="emit('delete', project.id, project.owner.id)"
            class="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
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
</template>
