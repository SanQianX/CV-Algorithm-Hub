import { ref, reactive, computed } from 'vue'

// ==================== Types ====================
export type ThemeMode = 'light' | 'dark' | 'system'

export interface UseFormOptions {
  validateOnChange?: boolean
  validateOnBlur?: boolean
}

// ==================== useTheme ====================
export function useTheme() {
  const theme = ref<ThemeMode>('light')
  const isDark = ref(false)
  let mediaQuery: MediaQueryList | null = null

  const getSystemTheme = (): 'light' | 'dark' => {
    if (typeof window === 'undefined') return 'light'
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  const applyTheme = (mode: ThemeMode) => {
    if (typeof document === 'undefined') return

    const effectiveTheme = mode === 'system' ? getSystemTheme() : mode
    isDark.value = effectiveTheme === 'dark'
    document.documentElement.classList.toggle('dark', isDark.value)
    localStorage.setItem('theme', mode)
  }

  const setTheme = (newTheme: ThemeMode) => {
    theme.value = newTheme
    applyTheme(newTheme)
  }

  const toggleTheme = () => {
    const modes: ThemeMode[] = ['light', 'dark', 'system']
    const currentIndex = modes.indexOf(theme.value)
    const nextIndex = (currentIndex + 1) % modes.length
    setTheme(modes[nextIndex])
  }

  const handleSystemThemeChange = () => {
    if (theme.value === 'system') {
      applyTheme('system')
    }
  }

  const initTheme = () => {
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme') as ThemeMode | null
      const initialTheme = savedTheme || 'light'
      setTheme(initialTheme)

      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', handleSystemThemeChange)
    }
  }

  const cleanupTheme = () => {
    if (mediaQuery) {
      mediaQuery.removeEventListener('change', handleSystemThemeChange)
    }
  }

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    initTheme,
    cleanupTheme
  }
}

// ==================== useForm ====================
export function useForm<T extends Record<string, unknown>>(
  initialValues: T,
  options: UseFormOptions = {}
) {
  const { validateOnChange = true, validateOnBlur = true } = options

  const values = reactive<T>({ ...initialValues }) as T & Record<string, unknown>
  const errors = reactive<Record<string, string>>({})
  const touched = reactive<Record<string, boolean>>({})
  const dirty = reactive<Record<string, boolean>>({})

  Object.keys(initialValues).forEach((key) => {
    errors[key] = ''
    touched[key] = false
    dirty[key] = false
  })

  const isSubmitting = ref(false)

  const isValid = computed(() => {
    return Object.values(errors).every((e) => !e)
  })

  const fields = computed(() => {
    const result: Record<string, { value: unknown; error: string; touched: boolean; dirty: boolean }> = {}
    Object.keys(values).forEach((key) => {
      result[key] = {
        value: values[key],
        error: errors[key] || '',
        touched: touched[key] || false,
        dirty: dirty[key] || false
      }
    })
    return result
  })

  const setFieldValue = (key: string, value: unknown) => {
    ;(values as Record<string, unknown>)[key] = value
    dirty[key] = true

    if (validateOnChange && touched[key]) {
      validateField(key)
    }
  }

  const setFieldError = (key: string, error: string) => {
    errors[key] = error
  }

  const setFieldTouched = (key: string, isTouched = true) => {
    touched[key] = isTouched
    if (isTouched && validateOnBlur) {
      validateField(key)
    }
  }

  const validateField = (_key: string): string | null => {
    const key = _key
    if (errors[key]) {
      errors[key] = ''
    }
    return null
  }

  const validateAll = (): boolean => {
    let isFormValid = true
    Object.keys(values).forEach((key) => {
      const error = validateField(key)
      if (error) {
        isFormValid = false
      }
    })
    return isFormValid
  }

  const reset = () => {
    Object.assign(values, { ...initialValues })
    Object.keys(initialValues).forEach((key) => {
      errors[key] = ''
      touched[key] = false
      dirty[key] = false
    })
  }

  const handleSubmit = (callback: (values: T) => Promise<void> | void) => {
    return async (e: Event) => {
      e.preventDefault()

      Object.keys(values).forEach((key) => {
        touched[key] = true
      })

      const isFormValid = validateAll()
      if (!isFormValid) return

      isSubmitting.value = true
      try {
        await callback(values as T)
      } finally {
        isSubmitting.value = false
      }
    }
  }

  return {
    values,
    errors,
    touched,
    dirty,
    fields,
    isSubmitting,
    isValid,
    setFieldValue,
    setFieldError,
    setFieldTouched,
    validateField,
    validateAll,
    reset,
    handleSubmit
  }
}

// ==================== useField ====================
export function useField(
  initialValue: unknown = '',
  validators: Array<(value: unknown) => string | null> = []
) {
  const value = ref(initialValue)
  const error = ref('')
  const touched = ref(false)
  const dirty = ref(false)

  const validate = (): string | null => {
    for (const validator of validators) {
      const result = validator(value.value)
      if (result) {
        error.value = result
        return result
      }
    }
    error.value = ''
    return null
  }

  const onInput = () => {
    dirty.value = true
    if (touched.value) {
      validate()
    }
  }

  const onBlur = () => {
    touched.value = true
    validate()
  }

  const reset = () => {
    value.value = initialValue
    error.value = ''
    touched.value = false
    dirty.value = false
  }

  return {
    value,
    error,
    touched,
    dirty,
    validate,
    onInput,
    onBlur,
    reset
  }
}
