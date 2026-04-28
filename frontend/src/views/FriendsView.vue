<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { searchUsers } from '@/services/userService'
import { getFriendships, sendFriendRequest, acceptFriendRequest, declineFriendRequest } from '@/services/friendService'
import type { Friendship } from '@/services/friendService'
import { useAuthStore } from '@/store/authStore'
import type { User } from '@/types/auth'

// État réactif
const auth = useAuthStore()
const query = ref('')
const searchResults = ref<User[]>([])
const friendships = ref<Friendship[]>([])
const searching = ref(false)

// Charger la liste des amitiés au démarrage
const loadFriendships = async () => {
  try {
    friendships.value = await getFriendships()
  } catch (e) {
    console.error("Erreur de chargement des amitiés", e)
  }
}

onMounted(() => {
  loadFriendships()
})

// Rechercher des utilisateurs par username
const handleSearch = async () => {
  if (query.value.length < 2) {
    searchResults.value = []
    return
  }
  searching.value = true
  try {
    searchResults.value = await searchUsers(query.value)
  } catch (e) {
    console.error("Erreur de recherche", e)
  } finally {
    searching.value = false
  }
}

// Envoyer une demande d'ami
const sendRequest = async (userId: number) => {
  try {
    await sendFriendRequest(userId)
    await loadFriendships()
    alert('Demande envoyée !')
  } catch (e: any) {
    alert(e.response?.data?.detail || e.response?.data?.non_field_errors?.[0] || 'Erreur lors de l\'envoi de la demande.')
  }
}

// Accepter une demande
const acceptRequest = async (id: number) => {
  try {
    await acceptFriendRequest(id)
    await loadFriendships()
  } catch (e) {
    console.error(e)
  }
}

// Refuser ou annuler une demande
const declineRequest = async (id: number) => {
  try {
    await declineFriendRequest(id)
    await loadFriendships()
  } catch (e) {
    console.error(e)
  }
}

// Propriétés calculées pour filtrer les amitiés par statut
const pendingReceived = computed(() => 
  friendships.value.filter(f => f.status === 'pending' && f.receiver.id === auth.user?.id)
)

const acceptedFriends = computed(() => 
  friendships.value.filter(f => f.status === 'accepted')
)

// Récupérer le profil de l'ami (celui qui n'est pas l'utilisateur actuel)
const getFriendProfile = (f: Friendship) => {
  return f.sender.id === auth.user?.id ? f.receiver : f.sender
}
</script>

<template>
  <div class="max-w-4xl mx-auto p-4 md:p-6 space-y-8">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Mes Relations</h1>

    <!-- Recherche -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
      <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Trouver un utilisateur</h2>
      <div class="flex gap-2">
        <input 
          v-model="query" 
          @input="handleSearch"
          type="text" 
          placeholder="Rechercher par @username..." 
          class="flex-1 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div v-if="searching" class="mt-4 text-sm text-gray-500">Recherche...</div>
      
      <ul v-if="searchResults.length > 0" class="mt-4 space-y-2">
        <li v-for="u in searchResults" :key="u.id" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 flex items-center justify-center font-bold">
              {{ u.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="font-medium text-gray-900 dark:text-white">@{{ u.username }}</div>
              <div class="text-xs text-gray-500" v-if="u.first_name || u.last_name">{{ u.first_name }} {{ u.last_name }}</div>
            </div>
          </div>
          <button 
            @click="sendRequest(u.id)"
            class="px-3 py-1.5 text-sm bg-violet-100 text-violet-700 hover:bg-violet-200 dark:bg-violet-900/30 dark:text-violet-400 dark:hover:bg-violet-900/50 rounded-lg transition"
          >
            Ajouter
          </button>
        </li>
      </ul>
    </div>

    <div class="grid md:grid-cols-2 gap-6">
      <!-- Demandes reçues -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Demandes reçues ({{ pendingReceived.length }})</h2>
        <p v-if="!pendingReceived.length" class="text-sm text-gray-500">Aucune demande en attente.</p>
        <ul class="space-y-3">
          <li v-for="req in pendingReceived" :key="req.id" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-100 dark:border-gray-600">
            <div>
              <div class="font-medium text-gray-900 dark:text-white">@{{ req.sender.username }}</div>
            </div>
            <div class="flex gap-2">
              <button @click="acceptRequest(req.id)" class="p-1.5 text-green-600 hover:bg-green-50 rounded-md transition" title="Accepter">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
              </button>
              <button @click="declineRequest(req.id)" class="p-1.5 text-red-600 hover:bg-red-50 rounded-md transition" title="Refuser">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Mes amis -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Mes Amis ({{ acceptedFriends.length }})</h2>
        <p v-if="!acceptedFriends.length" class="text-sm text-gray-500">Vous n'avez pas encore de relations ajoutées.</p>
        <ul class="space-y-3">
          <li v-for="friend in acceptedFriends" :key="friend.id" class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div class="w-8 h-8 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 flex items-center justify-center font-bold">
              {{ getFriendProfile(friend).username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="font-medium text-gray-900 dark:text-white">@{{ getFriendProfile(friend).username }}</div>
              <div class="text-xs text-gray-500" v-if="getFriendProfile(friend).first_name || getFriendProfile(friend).last_name">
                {{ getFriendProfile(friend).first_name }} {{ getFriendProfile(friend).last_name }}
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
