<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ModeToggle from '@/components/ui/ModeToggle.vue'

const authStore = useAuthStore()
const router = useRouter()

const activeTab = ref('profile')
const isLoading = ref(false)
const isSaving = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// Profile form
const profileForm = reactive({
  username: '',
  email: ''
})

// Password form
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loadUserData = () => {
  if (authStore.user) {
    profileForm.username = authStore.user.username || ''
    profileForm.email = authStore.user.email || ''
  }
}

onMounted(() => {
  authStore.initAuth()
  loadUserData()
})

const showMessage = (msg: string, type: 'success' | 'error') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

const handleUpdateProfile = async () => {
  if (!profileForm.username || !profileForm.email) {
    showMessage('请填写完整信息', 'error')
    return
  }

  isSaving.value = true
  try {
    const success = await authStore.updateProfile({
      username: profileForm.username,
      email: profileForm.email
    })
    if (success) {
      showMessage('个人信息更新成功', 'success')
    } else {
      showMessage(authStore.error || '更新失败', 'error')
    }
  } catch (error) {
    showMessage('更新失败，请稍后重试', 'error')
  } finally {
    isSaving.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    showMessage('请填写完整信息', 'error')
    return
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    showMessage('新密码与确认密码不一致', 'error')
    return
  }

  if (passwordForm.newPassword.length < 6) {
    showMessage('新密码长度至少为6位', 'error')
    return
  }

  isSaving.value = true
  try {
    const success = await authStore.changePassword(
      passwordForm.currentPassword,
      passwordForm.newPassword
    )
    if (success) {
      showMessage('密码修改成功', 'success')
      passwordForm.currentPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } else {
      showMessage(authStore.error || '密码修改失败', 'error')
    }
  } catch (error) {
    showMessage('密码修改失败，请稍后重试', 'error')
  } finally {
    isSaving.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="settings-page">
    <header class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/dashboard')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          返回
        </button>
        <h1 class="logo">CV Algorithm Hub</h1>
      </div>
      <div class="header-right">
        <ModeToggle />
      </div>
    </header>

    <main class="page-main">
      <div class="settings-container">
        <div class="settings-sidebar">
          <div class="user-card">
            <div class="user-avatar">
              {{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
            </div>
            <div class="user-info">
              <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
              <span class="user-email">{{ authStore.user?.email || '' }}</span>
            </div>
          </div>
          <nav class="settings-nav">
            <button
              :class="['nav-item', { active: activeTab === 'profile' }]"
              @click="activeTab = 'profile'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
              个人信息
            </button>
            <button
              :class="['nav-item', { active: activeTab === 'security' }]"
              @click="activeTab = 'security'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
              安全设置
            </button>
            <button class="nav-item logout" @click="handleLogout">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
              </svg>
              退出登录
            </button>
          </nav>
        </div>

        <div class="settings-content">
          <div v-if="message" :class="['message', messageType]">
            {{ message }}
          </div>

          <!-- Profile Tab -->
          <div v-if="activeTab === 'profile'" class="settings-section">
            <h2>个人信息</h2>
            <p class="section-desc">管理您的账户信息</p>

            <form @submit.prevent="handleUpdateProfile" class="settings-form">
              <div class="form-group">
                <label for="username">用户名</label>
                <input
                  id="username"
                  v-model="profileForm.username"
                  type="text"
                  placeholder="请输入用户名"
                />
              </div>

              <div class="form-group">
                <label for="email">邮箱地址</label>
                <input
                  id="email"
                  v-model="profileForm.email"
                  type="email"
                  placeholder="请输入邮箱地址"
                />
              </div>

              <div class="form-group">
                <label>账户创建时间</label>
                <input
                  type="text"
                  :value="authStore.user?.created_at || '未知'"
                  disabled
                />
              </div>

              <button type="submit" class="submit-btn" :disabled="isSaving">
                {{ isSaving ? '保存中...' : '保存修改' }}
              </button>
            </form>
          </div>

          <!-- Security Tab -->
          <div v-if="activeTab === 'security'" class="settings-section">
            <h2>安全设置</h2>
            <p class="section-desc">修改您的账户密码</p>

            <form @submit.prevent="handleChangePassword" class="settings-form">
              <div class="form-group">
                <label for="currentPassword">当前密码</label>
                <input
                  id="currentPassword"
                  v-model="passwordForm.currentPassword"
                  type="password"
                  placeholder="请输入当前密码"
                />
              </div>

              <div class="form-group">
                <label for="newPassword">新密码</label>
                <input
                  id="newPassword"
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="请输入新密码（至少6位）"
                />
              </div>

              <div class="form-group">
                <label for="confirmPassword">确认新密码</label>
                <input
                  id="confirmPassword"
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入新密码"
                />
              </div>

              <button type="submit" class="submit-btn" :disabled="isSaving">
                {{ isSaving ? '修改中...' : '修改密码' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

:global(.dark) .settings-page {
  background: #111827;
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

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #6b7280;
  background: transparent;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

:global(.dark) .back-btn {
  color: #9ca3af;
  border-color: #4b5563;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

:global(.dark) .back-btn:hover {
  background: #374151;
  color: #f3f4f6;
}

.back-btn svg {
  width: 1.25rem;
  height: 1.25rem;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-main {
  flex: 1;
  padding: 2rem;
}

.settings-container {
  display: flex;
  max-width: 1000px;
  margin: 0 auto;
  gap: 2rem;
}

.settings-sidebar {
  width: 260px;
  flex-shrink: 0;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border-radius: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .user-card {
  background: #1f2937;
}

.user-avatar {
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
  border-radius: 50%;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .user-name {
  color: #f3f4f6;
}

.user-email {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .user-email {
  color: #9ca3af;
}

.settings-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  font-size: 0.95rem;
  color: #6b7280;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

:global(.dark) .nav-item {
  color: #9ca3af;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #374151;
}

:global(.dark) .nav-item:hover {
  background: #374151;
  color: #f3f4f6;
}

.nav-item.active {
  background: #eff6ff;
  color: #2563eb;
}

:global(.dark) .nav-item.active {
  background: #1e3a5f;
  color: #60a5fa;
}

.nav-item svg {
  width: 1.25rem;
  height: 1.25rem;
}

.nav-item.logout {
  margin-top: 1rem;
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

:global(.dark) .nav-item.logout {
  border-color: #374151;
}

.settings-content {
  flex: 1;
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .settings-content {
  background: #1f2937;
}

.message {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.message.success {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

:global(.dark) .message.success {
  background: #064e3b;
  border-color: #34d399;
}

.message.error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

:global(.dark) .message.error {
  background: #7f1d1d;
  border-color: #f87171;
}

.settings-section h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .settings-section h2 {
  color: #f3f4f6;
}

.section-desc {
  margin: 0 0 2rem;
  font-size: 0.95rem;
  color: #6b7280;
}

:global(.dark) .section-desc {
  color: #9ca3af;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 400px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.95rem;
  font-weight: 500;
  color: #374151;
}

:global(.dark) .form-group label {
  color: #f3f4f6;
}

.form-group input {
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  color: #1f2937;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

:global(.dark) .form-group input {
  color: #f3f4f6;
  background: #374151;
  border-color: #4b5563;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn {
  padding: 0.875rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .settings-container {
    flex-direction: column;
  }

  .settings-sidebar {
    width: 100%;
  }
}
</style>
