<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/authStore'
import { updateProfile } from '@/services/userService'

const auth = useAuthStore()
const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = ref({
  username: '',
  first_name: '',
  last_name: ''
})

onMounted(() => {
  if (auth.user) {
    form.value.username = auth.user.username
    form.value.first_name = auth.user.first_name || ''
    form.value.last_name = auth.user.last_name || ''
  }
})

const saveProfile = async () => {
  if (!auth.user) return
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  
  try {
    const updated = await updateProfile(auth.user.id, form.value)
    // Update local user state
    if (auth.user) {
      auth.user.username = updated.username
      auth.user.first_name = updated.first_name
      auth.user.last_name = updated.last_name
    }
    successMsg.value = 'Profil mis à jour avec succès.'
  } catch (e: any) {
    errorMsg.value = e.response?.data?.detail || 'Erreur lors de la mise à jour.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 w-full max-w-md">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Mon Profil</h1>
      
      <form @submit.prevent="saveProfile" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nom d'utilisateur</label>
          <input 
            v-model="form.username" 
            type="text" 
            required
            class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Prénom</label>
            <input 
              v-model="form.first_name" 
              type="text" 
              class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nom</label>
            <input 
              v-model="form.last_name" 
              type="text" 
              class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>

        <div v-if="auth.user?.email" class="pt-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email (Non modifiable)</label>
          <input 
            :value="auth.user.email" 
            type="text" 
            disabled
            class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed"
          />
        </div>

        <div v-if="successMsg" class="text-sm text-green-600 bg-green-50 p-2 rounded">{{ successMsg }}</div>
        <div v-if="errorMsg" class="text-sm text-red-600 bg-red-50 p-2 rounded">{{ errorMsg }}</div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full mt-4 bg-violet-600 hover:bg-violet-700 text-white font-medium py-2 px-4 rounded-lg transition"
        >
          {{ loading ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
      </form>
    </div>
  </div>
</template>
