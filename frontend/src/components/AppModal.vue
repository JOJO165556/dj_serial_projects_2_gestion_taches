<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  title?: string
  maxWidth?: string
}>()

const emit = defineEmits<{ close: [] }>()

const onKey = (e: KeyboardEvent) => {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))

watch(
  () => props.title,
  () => {
    requestAnimationFrame(() => {
      const el = document.querySelector(
        '.fixed.inset-0 input:not([type="hidden"]), .fixed.inset-0 textarea, .fixed.inset-0 select'
      ) as HTMLElement | null
      el?.scrollIntoView({ block: 'nearest' })
    })
  },
  { immediate: true }
)
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-end sm:items-center justify-center p-3 sm:p-4 z-50"
      @click.self="emit('close')"
    >
      <div
        class="bg-white dark:bg-gray-900 rounded-t-2xl sm:rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 w-full flex flex-col max-h-[92vh] sm:max-h-[90vh]"
        :class="maxWidth ?? 'max-w-lg'"
      >
        <!-- Header -->
        <div class="flex items-center gap-3 px-4 sm:px-6 py-4 border-b border-gray-100 dark:border-gray-800 shrink-0">
          <slot name="title">
            <h2 v-if="title" class="text-base font-semibold text-gray-900 dark:text-white flex-1">
              {{ title }}
            </h2>
          </slot>
          <button
            @click="emit('close')"
            class="ml-auto p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Fermer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6 6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="px-4 sm:px-6 py-4 sm:py-5 overflow-y-auto flex-1 scrollbar-thin">
          <slot />
        </div>

        <!-- Footer -->
        <div v-if="$slots.footer" class="px-4 sm:px-6 py-4 border-t border-gray-100 dark:border-gray-800 flex flex-col-reverse sm:flex-row justify-end gap-2.5 shrink-0">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
