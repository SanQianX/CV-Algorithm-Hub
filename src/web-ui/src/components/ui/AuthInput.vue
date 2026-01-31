<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
  type?: 'text' | 'email' | 'password' | 'number'
  label?: string
  placeholder?: string
  error?: string
  disabled?: boolean
  autocomplete?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  error: '',
  disabled: false,
  autocomplete: 'off'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const hasError = computed(() => !!props.error)
</script>

<template>
  <div class="auth-input-wrapper">
    <label v-if="label" class="auth-label" :for="label">
      {{ label }}
    </label>
    <div class="input-container" :class="{ 'has-error': hasError, 'is-disabled': disabled }">
      <input
        :id="label"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :autocomplete="autocomplete"
        class="auth-input"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
      <slot name="prefix" />
      <slot name="suffix" />
    </div>
    <span v-if="error" class="error-message">{{ error }}</span>
  </div>
</template>

<style scoped>
.auth-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.auth-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.auth-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  color: #1f2937;
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  outline: none;
  transition: all 0.2s ease;
}

.auth-input::placeholder {
  color: #9ca3af;
}

.auth-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-container.has-error .auth-input {
  border-color: #ef4444;
}

.input-container.has-error .auth-input:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.input-container.is-disabled .auth-input {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.error-message {
  font-size: 0.75rem;
  color: #ef4444;
}

:global(.dark) .auth-label {
  color: #d1d5db;
}

:global(.dark) .auth-input {
  color: #f3f4f6;
  background-color: #1f2937;
  border-color: #374151;
}

:global(.dark) .auth-input::placeholder {
  color: #6b7280;
}

:global(.dark) .auth-input:focus {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}

:global(.dark) .input-container.has-error .auth-input {
  border-color: #f87171;
}

:global(.dark) .input-container.has-error .auth-input:focus {
  box-shadow: 0 0 0 3px rgba(248, 113, 113, 0.1);
}

:global(.dark) .input-container.is-disabled .auth-input {
  background-color: #374151;
}
</style>
