<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ModeToggle from '@/components/ui/ModeToggle.vue'

type ValidationErrors = {
  email?: string
  password?: string
}

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: ''
})

const errors = reactive<ValidationErrors>({})
const generalError = ref('')
const isSubmitting = ref(false)

// Validation functions
const validateEmail = (value: string): string | undefined => {
  if (!value.trim()) return '邮箱不能为空'
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) return '请输入有效的邮箱地址'
  return undefined
}

const validatePassword = (value: string): string | undefined => {
  if (!value) return '密码不能为空'
  return undefined
}

const validateForm = (): boolean => {
  let isValid = true
  errors.email = validateEmail(form.email)
  errors.password = validatePassword(form.password)

  if (errors.email || errors.password) {
    isValid = false
  }
  return isValid
}

const handleBlur = (field: keyof typeof errors) => {
  switch (field) {
    case 'email':
      errors.email = validateEmail(form.email)
      break
    case 'password':
      errors.password = validatePassword(form.password)
      break
  }
}

const handleSubmit = async () => {
  generalError.value = ''

  if (!validateForm()) return

  isSubmitting.value = true

  try {
    const result = await authStore.login(form.email, form.password)

    if (result.success) {
      router.push('/dashboard')
    } else {
      generalError.value = result.error || '登录失败，请稍后重试'
    }
  } catch {
    generalError.value = '网络错误，请检查网络连接'
  } finally {
    isSubmitting.value = false
  }
}

const navigateToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="login-page">
    <header class="page-header">
      <h1 class="logo">CV Algorithm Hub</h1>
      <ModeToggle />
    </header>

    <main class="page-main">
      <div class="login-card">
        <div class="card-header">
          <h2>欢迎回来</h2>
          <p class="subtitle">登录您的账户</p>
        </div>

        <form @submit.prevent="handleSubmit" class="login-form" novalidate>
          <div v-if="generalError" class="error-banner">
            {{ generalError }}
          </div>

          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              class="form-input"
              :class="{ 'error': errors.email }"
              @blur="handleBlur('email')"
            />
            <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="输入密码"
              class="form-input"
              :class="{ 'error': errors.password }"
              @blur="handleBlur('password')"
            />
            <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
          </div>

          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" class="checkbox-input" />
              <span class="checkbox-text">记住我</span>
            </label>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="loading-spinner"></span>
            {{ isSubmitting ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="register-prompt">
          还没有账号？
          <a href="#" class="link" @click.prevent="navigateToRegister">立即注册</a>
        </div>

        <div class="divider">
          <span>或</span>
        </div>

        <div class="social-login">
          <button class="social-btn github">
            <svg class="social-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </button>
          <button class="social-btn google">
            <svg class="social-icon" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

:global(.dark) .login-page {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .page-header {
  background: #1f2937;
  border-color: #374151;
}

.logo {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

:global(.dark) .logo {
  color: #f3f4f6;
}

.page-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

:global(.dark) .login-card {
  background: #1f2937;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h2 {
  margin: 0 0 0.5rem;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .card-header h2 {
  color: #f3f4f6;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.error-banner {
  padding: 0.875rem 1rem;
  margin-bottom: 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  color: #dc2626;
  font-size: 0.875rem;
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

:global(.dark) .form-group label {
  color: #d1d5db;
}

.form-input {
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  outline: none;
  transition: all 0.2s ease;
  background: white;
  color: #1f2937;
}

:global(.dark) .form-input {
  background: #374151;
  border-color: #4b5563;
  color: #f3f4f6;
}

.form-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.form-input.error {
  border-color: #ef4444;
}

.field-error {
  font-size: 0.8rem;
  color: #ef4444;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-input {
  width: 1rem;
  height: 1rem;
  accent-color: #3b82f6;
  cursor: pointer;
}

.checkbox-text {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .checkbox-text {
  color: #9ca3af;
}

.forgot-link {
  font-size: 0.875rem;
  color: #3b82f6;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.submit-btn {
  padding: 0.875rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1.125rem;
  height: 1.125rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.register-prompt {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .register-prompt {
  color: #9ca3af;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  color: #9ca3af;
  font-size: 0.8rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e5e7eb;
}

:global(.dark) .divider::before,
:global(.dark) .divider::after {
  background: #374151;
}

.divider span {
  padding: 0 1rem;
}

.social-login {
  display: flex;
  gap: 1rem;
}

.social-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

:global(.dark) .social-btn {
  background: #374151;
  border-color: #4b5563;
  color: #f3f4f6;
}

.social-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

:global(.dark) .social-btn:hover {
  background: #4b5563;
}

.social-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.social-btn.github .social-icon {
  color: #24292f;
}

:global(.dark) .social-btn.github .social-icon {
  color: #f3f4f6;
}
</style>
