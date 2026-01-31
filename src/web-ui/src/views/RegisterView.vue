<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ModeToggle from '@/components/ui/ModeToggle.vue'

type ValidationErrors = {
  username?: string
  email?: string
  password?: string
  confirmPassword?: string
  terms?: string
}

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  terms: false
})

const errors = reactive<ValidationErrors>({})
const serverErrors = reactive<Record<string, string[]>>({})
const generalError = ref('')
const isSubmitting = ref(false)

// Validation functions
const validateUsername = (value: string): string | undefined => {
  if (!value.trim()) return '用户名不能为空'
  if (value.length < 3) return '用户名至少3个字符'
  if (value.length > 20) return '用户名最多20个字符'
  if (!/^[a-zA-Z0-9_]+$/.test(value)) return '用户名只能包含字母、数字和下划线'
  return undefined
}

const validateEmail = (value: string): string | undefined => {
  if (!value.trim()) return '邮箱不能为空'
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) return '请输入有效的邮箱地址'
  return undefined
}

const validatePassword = (value: string): string | undefined => {
  if (!value) return '密码不能为空'
  if (value.length < 6) return '密码至少6个字符'
  if (value.length > 32) return '密码最多32个字符'
  if (!/[a-zA-Z]/.test(value)) return '密码必须包含字母'
  if (!/[0-9]/.test(value)) return '密码必须包含数字'
  return undefined
}

const validateConfirmPassword = (value: string): string | undefined => {
  if (!value) return '请再次输入密码'
  if (value !== form.password) return '两次输入的密码不一致'
  return undefined
}

const validateForm = (): boolean => {
  let isValid = true
  errors.username = validateUsername(form.username)
  errors.email = validateEmail(form.email)
  errors.password = validatePassword(form.password)
  errors.confirmPassword = validateConfirmPassword(form.confirmPassword)
  errors.terms = form.terms ? undefined : '请同意用户协议'

  if (errors.username || errors.email || errors.password || errors.confirmPassword || errors.terms) {
    isValid = false
  }
  return isValid
}

// Real-time validation on blur
const handleBlur = (field: keyof typeof errors) => {
  switch (field) {
    case 'username':
      errors.username = validateUsername(form.username)
      break
    case 'email':
      errors.email = validateEmail(form.email)
      break
    case 'password':
      errors.password = validatePassword(form.password)
      break
    case 'confirmPassword':
      errors.confirmPassword = validateConfirmPassword(form.confirmPassword)
      break
  }
}

const handleSubmit = async () => {
  generalError.value = ''
  Object.keys(serverErrors).forEach(key => delete serverErrors[key])

  if (!validateForm()) return

  isSubmitting.value = true

  try {
    const result = await authStore.register(
      form.username,
      form.email,
      form.password,
      form.confirmPassword
    )

    if (result.success) {
      router.push('/dashboard')
    } else {
      generalError.value = result.error || '注册失败，请稍后重试'

      // Handle field-specific server errors
      if (result.details) {
        Object.entries(result.details).forEach(([key, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            serverErrors[key] = messages
          }
        })
      }
    }
  } catch {
    generalError.value = '网络错误，请检查网络连接'
  } finally {
    isSubmitting.value = false
  }
}

const navigateToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-page">
    <header class="page-header">
      <h1 class="logo">CV Algorithm Hub</h1>
      <ModeToggle />
    </header>

    <main class="page-main">
      <div class="register-card">
        <div class="card-header">
          <h2>创建账户</h2>
          <p class="subtitle">加入算法分享社区</p>
        </div>

        <form @submit.prevent="handleSubmit" class="register-form" novalidate>
          <!-- General Error -->
          <div v-if="generalError" class="error-banner">
            {{ generalError }}
          </div>

          <!-- Username Field -->
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="3-20个字符，仅字母数字下划线"
              class="form-input"
              :class="{ 'error': errors.username || serverErrors.username }"
              @blur="handleBlur('username')"
            />
            <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
            <span v-else-if="serverErrors.username" class="field-error">{{ serverErrors.username[0] }}</span>
          </div>

          <!-- Email Field -->
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              class="form-input"
              :class="{ 'error': errors.email || serverErrors.email }"
              @blur="handleBlur('email')"
            />
            <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
            <span v-else-if="serverErrors.email" class="field-error">{{ serverErrors.email[0] }}</span>
          </div>

          <!-- Password Field -->
          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="6-32位，包含字母和数字"
              class="form-input"
              :class="{ 'error': errors.password }"
              @blur="handleBlur('password')"
            />
            <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
          </div>

          <!-- Confirm Password Field -->
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              placeholder="再次输入密码"
              class="form-input"
              :class="{ 'error': errors.confirmPassword }"
              @blur="handleBlur('confirmPassword')"
            />
            <span v-if="errors.confirmPassword" class="field-error">{{ errors.confirmPassword }}</span>
          </div>

          <!-- Terms Checkbox -->
          <div class="form-group terms-group">
            <label class="checkbox-label">
              <input
                v-model="form.terms"
                type="checkbox"
                class="checkbox-input"
              />
              <span class="checkbox-text">
                我已阅读并同意
                <a href="#" class="link">用户协议</a>
                和
                <a href="#" class="link">隐私政策</a>
              </span>
            </label>
            <span v-if="errors.terms" class="field-error">{{ errors.terms }}</span>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-btn"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="loading-spinner"></span>
            {{ isSubmitting ? '注册中...' : '注册' }}
          </button>
        </form>

        <!-- Login Link -->
        <div class="login-prompt">
          已有账号？
          <a href="#" class="link" @click.prevent="navigateToLogin">立即登录</a>
        </div>

        <!-- Divider -->
        <div class="divider">
          <span>或</span>
        </div>

        <!-- Social Login -->
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
.register-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

:global(.dark) .register-page {
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

.register-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

:global(.dark) .register-card {
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

:global(.dark) .subtitle {
  color: #9ca3af;
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

.register-form {
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

.form-input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.field-error {
  font-size: 0.8rem;
  color: #ef4444;
}

.terms-group {
  flex-direction: row;
  flex-wrap: wrap;
  align-items: flex-start;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-input {
  width: 1.125rem;
  height: 1.125rem;
  margin-top: 0.125rem;
  accent-color: #3b82f6;
  cursor: pointer;
}

.checkbox-text {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
}

:global(.dark) .checkbox-text {
  color: #9ca3af;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
}

.link:hover {
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
  margin-top: 0.5rem;
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

.login-prompt {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .login-prompt {
  color: #9ca3af;
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

.social-btn.github:hover {
  background: #f3f4f6;
  border-color: #24292f;
}

:global(.dark) .social-btn.github:hover {
  background: #2f363d;
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
