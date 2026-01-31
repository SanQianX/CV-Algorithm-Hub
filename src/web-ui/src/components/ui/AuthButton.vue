<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  fullWidth: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => [
  'auth-button',
  `auth-button--${props.variant}`,
  `auth-button--${props.size}`,
  { 'auth-button--full-width': props.fullWidth },
  { 'auth-button--loading': props.loading },
  { 'auth-button--disabled': props.disabled }
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<template>
  <button
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="spinner"></span>
    <span :class="{ 'invisible': loading }">
      <slot />
    </span>
  </button>
</template>

<style scoped>
.auth-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 600;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.auth-button:focus-visible {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.4);
}

/* Sizes */
.auth-button--sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.auth-button--md {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

.auth-button--lg {
  padding: 1rem 2rem;
  font-size: 1.125rem;
}

/* Variants */
.auth-button--primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.auth-button--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

.auth-button--secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 2px solid #e5e7eb;
}

.auth-button--secondary:hover:not(:disabled) {
  background-color: #e5e7eb;
  border-color: #d1d5db;
}

.auth-button--danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.auth-button--danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.auth-button--ghost {
  background-color: transparent;
  color: #3b82f6;
}

.auth-button--ghost:hover:not(:disabled) {
  background-color: rgba(59, 130, 246, 0.1);
}

/* States */
.auth-button--full-width {
  width: 100%;
}

.auth-button--disabled,
.auth-button--loading {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.auth-button--disabled:hover,
.auth-button--loading:hover {
  transform: none;
  box-shadow: none;
}

/* Spinner */
.spinner {
  position: absolute;
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.invisible {
  visibility: hidden;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Dark mode */
:global(.dark) .auth-button--secondary {
  background-color: #1f2937;
  color: #d1d5db;
  border-color: #374151;
}

:global(.dark) .auth-button--secondary:hover:not(:disabled) {
  background-color: #374151;
  border-color: #4b5563;
}

:global(.dark) .auth-button--ghost {
  color: #60a5fa;
}

:global(.dark) .auth-button--ghost:hover:not(:disabled) {
  background-color: rgba(96, 165, 250, 0.1);
}
</style>
