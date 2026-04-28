<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/authStore'
import { updateProfile } from '@/services/userService'

const auth = useAuthStore()
const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

// Formulaire d'édition
const form = ref({
  username: '',
  first_name: '',
  last_name: '',
  bio: ''
})
const avatarFile = ref<File | null>(null)
const avatarPreview = ref<string | null>(null)

// Pré-remplir le formulaire avec les données actuelles
onMounted(() => {
  if (auth.user) {
    form.value.username = auth.user.username
    form.value.first_name = auth.user.first_name || ''
    form.value.last_name = auth.user.last_name || ''
    form.value.bio = auth.user.bio || ''
    avatarPreview.value = auth.user.avatar || null
  }
})

// Gérer le changement de photo
const onFileChange = (e: any) => {
  const file = e.target.files[0]
  if (file) {
    avatarFile.value = file
    avatarPreview.value = URL.createObjectURL(file)
  }
}

// Enregistrer les modifications du profil
const saveProfile = async () => {
  if (!auth.user) return
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  
  try {
    // Utilisation de FormData pour l'envoi de fichier
    const formData = new FormData()
    formData.append('username', form.value.username)
    formData.append('first_name', form.value.first_name)
    formData.append('last_name', form.value.last_name)
    formData.append('bio', form.value.bio)
    if (avatarFile.value) {
      formData.append('avatar', avatarFile.value)
    }

    const updated = await updateProfile(auth.user.id, formData as any)
    
    // Mettre à jour l'état local
    if (auth.user) {
      auth.user.username = updated.username
      auth.user.first_name = updated.first_name
      auth.user.last_name = updated.last_name
      auth.user.bio = updated.bio
      auth.user.avatar = updated.avatar
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
        <!-- Avatar Section -->
        <div class="flex flex-col items-center mb-6">
          <div class="relative group">
            <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-700 border-2 border-violet-500">
              <img v-if="avatarPreview" :src="avatarPreview" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-violet-500 text-3xl font-bold">
                {{ form.username.charAt(0).toUpperCase() }}
              </div>
            </div>
            <label class="absolute inset-0 flex items-center justify-center bg-black/40 text-white rounded-full opacity-0 group-hover:opacity-100 cursor-pointer transition">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
              <input type="file" @change="onFileChange" class="hidden" accept="image/*" />
            </label>
          </div>
          <p class="text-xs text-gray-500 mt-2">Cliquer pour changer la photo</p>
        </div>

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

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bio (Ma description)</label>
          <textarea 
            v-model="form.bio" 
            rows="3"
            class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
            placeholder="Parlez-nous de vous..."
          />
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
