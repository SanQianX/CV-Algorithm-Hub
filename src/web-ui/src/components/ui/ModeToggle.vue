<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

type ThemeMode = 'light' | 'dark' | 'system'

const props = withDefaults(defineProps<{
  showLabels?: boolean
  size?: 'sm' | 'md' | 'lg'
}>(), {
  showLabels: false,
  size: 'md'
})

const emit = defineEmits<{
  'update:modelValue': [value: ThemeMode]
  'theme-change': [value: ThemeMode]
}>()

const currentTheme = ref<ThemeMode>('light')

const icons = {
  sun: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
  </svg>`,
  moon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
  </svg>`,
  system: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
  </svg>`
}

const getSystemTheme = (): 'light' | 'dark' => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const getEffectiveTheme = (): 'light' | 'dark' => {
  if (currentTheme.value === 'system') {
    return getSystemTheme()
  }
  return currentTheme.value
}

const applyTheme = (theme: 'light' | 'dark') => {
  document.documentElement.classList.toggle('dark', theme === 'dark')
  localStorage.setItem('theme', theme)
}

const cycleTheme = () => {
  const modes: ThemeMode[] = ['light', 'dark', 'system']
  const currentIndex = modes.indexOf(currentTheme.value)
  const nextIndex = (currentIndex + 1) % modes.length
  const newMode = modes[nextIndex]

  currentTheme.value = newMode
  emit('update:modelValue', newMode)
  emit('theme-change', newMode)

  if (newMode !== 'system') {
    applyTheme(newMode)
  } else {
    applyTheme(getSystemTheme())
  }
}

const setTheme = (theme: ThemeMode) => {
  currentTheme.value = theme
  emit('update:modelValue', theme)
  emit('theme-change', theme)

  if (theme !== 'system') {
    applyTheme(theme)
  } else {
    applyTheme(getSystemTheme())
  }
}

onMounted(() => {
  // Load saved theme or use system preference
  const savedTheme = localStorage.getItem('theme') as ThemeMode | null
  if (savedTheme) {
    setTheme(savedTheme)
  } else {
    setTheme('light')
  }
})

// Listen for system theme changes when in system mode
onMounted(() => {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (currentTheme.value === 'system') {
      applyTheme(getSystemTheme())
    }
  })
})

const sizeClasses = {
  sm: 'mode-toggle--sm',
  md: 'mode-toggle--md',
  lg: 'mode-toggle--lg'
}
</script>

<template>
  <div class="mode-toggle-wrapper">
    <button
      type="button"
      :class="['mode-toggle', sizeClasses[size]]"
      :title="`Current: ${currentTheme}. Click to cycle.`"
      @click="cycleTheme"
    >
      <span v-if="currentTheme === 'light'" class="icon" v-html="icons.sun"></span>
      <span v-else-if="currentTheme === 'dark'" class="icon" v-html="icons.moon"></span>
      <span v-else class="icon" v-html="icons.system"></span>
    </button>
  </div>
</template>

<style scoped>
.mode-toggle-wrapper {
  display: inline-flex;
}

.mode-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s ease;
  color: #6b7280;
}

.mode-toggle:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #1f2937;
}

:global(.dark) .mode-toggle:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #f3f4f6;
}

.mode-toggle:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.4);
}

.icon {
  display: flex;
}

.icon :deep(svg) {
  width: 100%;
  height: 100%;
}

/* Sizes */
.mode-toggle--sm {
  width: 2rem;
  height: 2rem;
}

.mode-toggle--sm .icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.mode-toggle--md {
  width: 2.5rem;
  height: 2.5rem;
}

.mode-toggle--md .icon :deep(svg) {
  width: 1.25rem;
  height: 1.25rem;
}

.mode-toggle--lg {
  width: 3rem;
  height: 3rem;
}

.mode-toggle--lg .icon :deep(svg) {
  width: 1.5rem;
  height: 1.5rem;
}
</style>
