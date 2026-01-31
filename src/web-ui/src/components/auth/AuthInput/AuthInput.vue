<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'

// ==================== Types ====================
type InputType = 'text' | 'password' | 'email' | 'number' | 'tel'
type InputSize = 'sm' | 'md' | 'lg'
type InputRounded = 'none' | 'sm' | 'md' | 'lg' | 'full'
type InputStatus = 'default' | 'error' | 'success'

interface ValidationRule {
  validator: RegExp | ((value: string | number) => boolean)
  message: string
  trigger?: 'input' | 'blur' | 'change'
}

interface Props {
  // 基础属性
  modelValue?: string | number
  type?: InputType
  name?: string
  placeholder?: string
  label?: string
  helperText?: string

  // 状态控制
  disabled?: boolean
  readonly?: boolean
  required?: boolean

  // 验证相关
  rules?: ValidationRule[]
  validateOn?: 'input' | 'blur' | 'submit'
  error?: string
  status?: InputStatus

  // 图标相关
  prefixIcon?: string
  suffixIcon?: string
  showPasswordToggle?: boolean
  showClear?: boolean

  // 尺寸和样式
  size?: InputSize
  rounded?: InputRounded
  block?: boolean

  // 功能限制
  maxlength?: number
  minlength?: number
  min?: number
  max?: number
  step?: number
  autocomplete?: string
  autocapitalize?: 'off' | 'none' | 'on' | 'sentences' | 'words' | 'characters'
}

// ==================== Props & Emits ====================
const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  name: '',
  placeholder: '',
  label: '',
  helperText: '',
  disabled: false,
  readonly: false,
  required: false,
  validateOn: 'blur',
  status: 'default',
  showPasswordToggle: false,
  showClear: false,
  size: 'md',
  rounded: 'md',
  block: false,
  autocomplete: 'off'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  'update:error': [value: string]
  'update:status': [value: InputStatus]
  'focus': [event: FocusEvent]
  'blur': [event: FocusEvent]
  'input': [event: InputEvent]
  'change': [value: string | number]
  'clear': []
  'keydown': [event: KeyboardEvent]
}>()

// ==================== Refs ====================
const inputRef = ref<HTMLInputElement | null>(null)
const inputValue = ref(props.modelValue)
const isFocused = ref(false)
const errorMessage = ref(props.error)
const inputStatus = ref<InputStatus>(props.status)

// ==================== Computed ====================
const inputType = computed(() => {
  if (props.type === 'password' && showPassword.value) {
    return 'text'
  }
  return props.type
})

const showPassword = ref(false)

const showClearButton = computed(() => {
  if (!props.showClear || props.disabled || props.readonly) return false
  return !!inputValue.value
})

const characterCount = computed(() => {
  const value = String(inputValue.value)
  return {
    current: value.length,
    max: props.maxlength,
    percentage: props.maxlength ? (value.length / props.maxlength) * 100 : 0
  }
})

const isInvalid = computed(() => {
  return inputStatus.value === 'error' || !!errorMessage.value
})

const isSuccess = computed(() => {
  return inputStatus.value === 'success'
})

const containerClasses = computed(() => [
  'auth-input-container',
  `auth-input-container--${props.size}`,
  `auth-input-container--rounded-${props.rounded}`,
  `auth-input-container--${inputStatus.value}`,
  {
    'auth-input-container--focused': isFocused.value,
    'auth-input-container--disabled': props.disabled,
    'auth-input-container--readonly': props.readonly,
    'auth-input-container--block': props.block,
    'auth-input-container--has-prefix': !!props.prefixIcon,
    'auth-input-container--has-suffix': !!(props.suffixIcon || showClearButton.value || (props.type === 'password' && props.showPasswordToggle))
  }
])

// ==================== Validation ====================
const validateField = (trigger: 'input' | 'blur' | 'change'): string | null => {
  if (!props.rules || props.rules.length === 0) return null

  const value = inputValue.value
  const applicableRules = props.rules.filter(rule => !rule.trigger || rule.trigger === trigger)

  for (const rule of applicableRules) {
    let isValid: boolean
    if (rule.validator instanceof RegExp) {
      isValid = rule.validator.test(String(value))
    } else if (typeof rule.validator === 'function') {
      isValid = rule.validator(value)
    } else {
      isValid = true
    }

    if (!isValid) {
      return rule.message
    }
  }

  return null
}

const runValidation = () => {
  const trigger = props.validateOn as 'input' | 'blur' | 'change'
  const error = validateField(trigger)

  if (error) {
    errorMessage.value = error
    inputStatus.value = 'error'
    emit('update:error', error)
    emit('update:status', 'error')
  } else if (isFocused.value) {
    inputStatus.value = 'default'
  } else if (String(inputValue.value)) {
    inputStatus.value = 'success'
    emit('update:status', 'success')
  }
}

// ==================== Event Handlers ====================
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  inputValue.value = target.value
  emit('update:modelValue', inputValue.value)
  emit('input', event)
  emit('change', inputValue.value)

  if (props.validateOn === 'input') {
    nextTick(() => runValidation())
  }

  if (props.maxlength) {
    if (String(inputValue.value).length > props.maxlength) {
      inputValue.value = String(inputValue.value).slice(0, props.maxlength)
      emit('update:modelValue', inputValue.value)
    }
  }
}

const handleFocus = (event: FocusEvent) => {
  if (props.disabled || props.readonly) return
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
  if (props.validateOn === 'blur') {
    runValidation()
  }
}

const handleClear = () => {
  inputValue.value = ''
  emit('update:modelValue', '')
  emit('clear')
  errorMessage.value = ''
  inputStatus.value = 'default'
  emit('update:error', '')
  emit('update:status', 'default')
  nextTick(() => inputRef.value?.focus())
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

// ==================== Expose ====================
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
  validate: runValidation,
  clear: handleClear,
  $el: inputRef
})

// ==================== Watchers ====================
watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
})

watch(() => props.error, (newError) => {
  errorMessage.value = newError || ''
  if (newError) {
    inputStatus.value = 'error'
  }
})

watch(() => props.status, (newStatus) => {
  inputStatus.value = newStatus || 'default'
})

// ==================== Lifecycle ====================
onMounted(() => {
  if (props.validateOn === 'submit') {
    const form = inputRef.value?.closest('form')
    if (form) {
      form.addEventListener('submit', runValidation)
    }
  }
})
</script>

<template>
  <div :class="containerClasses" class="auth-input-wrapper">
    <!-- Label -->
    <label v-if="label" :for="name" class="auth-input-label">
      {{ label }}
      <span v-if="required" class="auth-input-required">*</span>
    </label>

    <!-- Input Container -->
    <div class="auth-input-inner">
      <!-- Prefix Icon -->
      <span v-if="prefixIcon" class="auth-input-prefix">
        <img v-if="prefixIcon.startsWith('http')" :src="prefixIcon" alt="" />
        <span v-else class="icon-placeholder">{{ prefixIcon }}</span>
      </span>

      <!-- Input Field -->
      <input
        ref="inputRef"
        :id="name"
        :name="name"
        :type="inputType"
        :value="inputValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :maxlength="maxlength"
        :minlength="minlength"
        :min="min"
        :max="max"
        :step="step"
        :autocomplete="autocomplete"
        :autocapitalize="autocapitalize"
        class="auth-input"
        :aria-invalid="isInvalid"
        :aria-describedby="errorMessage ? `${name}-error` : helperText ? `${name}-helper` : undefined"
        :aria-required="required"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />

      <!-- Suffix Icons -->
      <div class="auth-input-suffix">
        <!-- Clear Button -->
        <button
          v-if="showClearButton"
          type="button"
          class="auth-input-clear"
          :aria-label="'Clear ' + label"
          @click="handleClear"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        </button>

        <!-- Password Toggle -->
        <button
          v-if="type === 'password' && showPasswordToggle"
          type="button"
          class="auth-input-toggle"
          :aria-label="showPassword ? 'Hide password' : 'Show password'"
          @click="togglePassword"
        >
          <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon">
            <path fill-rule="evenodd" d="M3.28 2.22a.75.75 0 00-1.06 1.06l18 18a.75.75 0 001.06-1.06l-18-18zM10.65 5.05a7.5 7.5 0 00-4.82 6.65 1.5 1.5 0 01-1.11 2.54l-2.38 1.19a.75.75 0 00-.22.53V17a.75.75 0 001.5 0v-.63l1.38-.69a.75.75 0 00.22-.53 1.5 1.5 0 011.11-2.54 7.5 7.5 0 003.5-5.35.75.75 0 00-.65-.75z" clip-rule="evenodd" />
          </svg>
        </button>

        <!-- Suffix Icon -->
        <span v-if="suffixIcon && !showClearButton && !(type === 'password' && showPasswordToggle)" class="auth-input-suffix-icon">
          <img v-if="suffixIcon.startsWith('http')" :src="suffixIcon" alt="" />
          <span v-else class="icon-placeholder">{{ suffixIcon }}</span>
        </span>

        <!-- Status Icon -->
        <span v-if="isSuccess" class="auth-input-status auth-input-status--success">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
          </svg>
        </span>
        <span v-else-if="isInvalid" class="auth-input-status auth-input-status--error">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
          </svg>
        </span>
      </div>
    </div>

    <!-- Helper Text -->
    <p v-if="helperText && !errorMessage" :id="`${name}-helper`" class="auth-input-helper">
      {{ helperText }}
    </p>

    <!-- Error Message -->
    <p v-if="errorMessage" :id="`${name}-error`" class="auth-input-error" role="alert">
      {{ errorMessage }}
    </p>

    <!-- Character Count -->
    <div v-if="maxlength" class="auth-input-count">
      <span :class="{ 'auth-input-count--warning': characterCount.percentage >= 80 }">
        {{ characterCount.current }}/{{ characterCount.max }}
      </span>
    </div>
  </div>
</template>

<style scoped>
/* ==================== CSS Variables ==================== */
.auth-input-wrapper {
  --input-height-sm: 32px;
  --input-height-md: 40px;
  --input-height-lg: 48px;
  --input-padding-x: 12px;
  --input-icon-spacing: 8px;
  --input-border-radius: 8px;

  --input-border-default: #D1D5DB;
  --input-border-focus: #3B82F6;
  --input-border-error: #EF4444;
  --input-border-success: #10B981;

  --input-bg-default: #FFFFFF;
  --input-bg-disabled: #F9FAFB;

  --input-text-default: #1F2937;
  --input-text-placeholder: #9CA3AF;
  --input-text-disabled: #6B7280;

  --input-icon-default: #6B7280;
  --input-icon-focus: #3B82F6;
  --input-icon-error: #EF4444;
  --input-icon-success: #10B981;

  --input-error-text: #EF4444;
  --input-helper-text: #6B7280;

  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  width: 100%;
}

/* ==================== Label ==================== */
.auth-input-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--input-text-default);
}

.auth-input-required {
  color: var(--input-border-error);
  margin-left: 0.25rem;
}

/* ==================== Inner Container ==================== */
.auth-input-inner {
  position: relative;
  display: flex;
  align-items: center;
  background-color: var(--input-bg-default);
  border: 2px solid var(--input-border-default);
  border-radius: var(--input-border-radius);
  transition: all 0.2s ease;
}

.auth-input-wrapper:hover .auth-input-inner:not(.auth-input-container--disabled) {
  border-color: var(--input-border-focus);
}

.auth-input-container--focused .auth-input-inner {
  border-color: var(--input-border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.auth-input-container--error .auth-input-inner {
  border-color: var(--input-border-error);
}

.auth-input-container--error.auth-input-container--focused .auth-input-inner {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.auth-input-container--success .auth-input-inner {
  border-color: var(--input-border-success);
}

.auth-input-container--disabled .auth-input-inner {
  background-color: var(--input-bg-disabled);
  cursor: not-allowed;
}

.auth-input-container--readonly .auth-input-inner {
  background-color: var(--input-bg-disabled);
}

/* ==================== Sizes ==================== */
.auth-input-container--sm .auth-input-inner {
  height: var(--input-height-sm);
  border-radius: calc(var(--input-border-radius) - 2px);
}

.auth-input-container--md .auth-input-inner {
  height: var(--input-height-md);
}

.auth-input-container--lg .auth-input-inner {
  height: var(--input-height-lg);
  border-radius: calc(var(--input-border-radius) + 2px);
}

/* ==================== Rounded ==================== */
.auth-input-container--rounded-none .auth-input-inner {
  border-radius: 0;
}

.auth-input-container--rounded-sm .auth-input-inner {
  border-radius: calc(var(--input-border-radius) - 4px);
}

.auth-input-container--rounded-md .auth-input-inner {
  border-radius: var(--input-border-radius);
}

.auth-input-container--rounded-lg .auth-input-inner {
  border-radius: calc(var(--input-border-radius) + 4px);
}

.auth-input-container--rounded-full .auth-input-inner {
  border-radius: 9999px;
}

/* ==================== Block ==================== */
.auth-input-container--block {
  display: block;
}

/* ==================== Prefix & Suffix ==================== */
.auth-input-prefix,
.auth-input-suffix {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.auth-input-prefix {
  padding-left: var(--input-padding-x);
}

.auth-input-suffix {
  padding-right: var(--input-padding-x);
  gap: 4px;
}

.auth-input-container--has-prefix .auth-input {
  padding-left: calc(var(--input-padding-x) + var(--input-icon-spacing));
}

.auth-input-container--has-suffix .auth-input {
  padding-right: calc(var(--input-padding-x) + var(--input-icon-spacing));
}

.auth-input-prefix img,
.auth-input-suffix-icon img {
  width: 1.25rem;
  height: 1.25rem;
}

.icon-placeholder {
  font-size: 1rem;
  color: var(--input-icon-default);
}

/* ==================== Input Field ==================== */
.auth-input {
  flex: 1;
  width: 100%;
  height: 100%;
  padding: 0 var(--input-padding-x);
  font-size: 0.9375rem;
  color: var(--input-text-default);
  background: transparent;
  border: none;
  outline: none;
}

.auth-input::placeholder {
  color: var(--input-text-placeholder);
}

.auth-input:disabled {
  cursor: not-allowed;
  color: var(--input-text-disabled);
}

.auth-input:read-only {
  cursor: default;
}

/* ==================== Icons ==================== */
.auth-input-suffix .icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--input-icon-default);
  transition: color 0.2s ease;
}

.auth-input-suffix .auth-input-toggle:hover .icon,
.auth-input-suffix .auth-input-clear:hover .icon {
  color: var(--input-text-default);
}

.auth-input-status {
  display: flex;
  align-items: center;
}

.auth-input-status .icon {
  width: 1.25rem;
  height: 1.25rem;
}

.auth-input-status--success .icon {
  color: var(--input-icon-success);
}

.auth-input-status--error .icon {
  color: var(--input-icon-error);
}

.auth-input-clear,
.auth-input-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.auth-input-clear:hover,
.auth-input-toggle:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

/* ==================== Helper & Error ==================== */
.auth-input-helper,
.auth-input-error {
  font-size: 0.75rem;
  line-height: 1.4;
}

.auth-input-helper {
  color: var(--input-helper-text);
}

.auth-input-error {
  color: var(--input-error-text);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.auth-input-error .icon {
  width: 0.875rem;
  height: 0.875rem;
  flex-shrink: 0;
}

/* ==================== Character Count ==================== */
.auth-input-count {
  display: flex;
  justify-content: flex-end;
  font-size: 0.75rem;
  color: var(--input-text-placeholder);
}

.auth-input-count--warning {
  color: #F59E0B;
}

/* ==================== Block Width ==================== */
.auth-input-container--block {
  display: flex;
}

/* ==================== Dark Mode ==================== */
:global(.dark) .auth-input-wrapper {
  --input-text-default: #F3F4F6;
  --input-text-placeholder: #6B7280;
  --input-text-disabled: #4B5563;
  --input-bg-default: #1F2937;
  --input-bg-disabled: #374151;
  --input-border-default: #4B5563;
  --input-icon-default: #9CA3AF;
  --input-icon-focus: #60A5FA;
  --input-helper-text: #9CA3AF;
}

:global(.dark) .auth-input-suffix .auth-input-toggle:hover .icon,
:global(.dark) .auth-input-suffix .auth-input-clear:hover .icon {
  color: #F3F4F6;
}

:global(.dark) .auth-input-clear:hover,
:global(.dark) .auth-input-toggle:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
</style>
