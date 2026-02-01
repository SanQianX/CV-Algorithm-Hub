<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ModeToggle from '@/components/ui/ModeToggle.vue'

const authStore = useAuthStore()
const router = useRouter()
const isLoggingOut = ref(false)
const showUserMenu = ref(false)

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const handleLogout = async () => {
  closeUserMenu()
  isLoggingOut.value = true
  authStore.logout()
  router.push('/login')
}

const goToSettings = () => {
  closeUserMenu()
  router.push('/settings')
}

const goToStockMonitor = () => {
  router.push('/stock-monitor')
}

const goToDatabaseManager = () => {
  router.push('/database')
}

const goToFinanceManager = () => {
  router.push('/db-manager/finance')
}

const goToDataExplorer = () => {
  router.push('/explorer')
}

onMounted(() => {
  authStore.initAuth()
})
</script>

<template>
  <div class="dashboard-page">
    <header class="page-header">
      <div class="header-left">
        <h1 class="logo">CV Algorithm Hub</h1>
      </div>
      <div class="header-right">
        <ModeToggle />
        <div class="user-dropdown">
          <button class="user-avatar-btn" @click="toggleUserMenu">
            <div class="user-avatar">
              {{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
            </div>
            <svg class="chevron" :class="{ rotated: showUserMenu }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          <Transition name="fade">
            <div v-if="showUserMenu" class="user-menu">
              <div class="menu-header">
                <div class="menu-user-avatar">
                  {{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
                </div>
                <div class="menu-user-info">
                  <span class="menu-user-name">{{ authStore.user?.username || '用户' }}</span>
                  <span class="menu-user-email">{{ authStore.user?.email || '' }}</span>
                </div>
              </div>
              <div class="menu-divider"></div>
              <button class="menu-item" @click="goToSettings">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                账户设置
              </button>
              <div class="menu-divider"></div>
              <button class="menu-item logout" @click="handleLogout" :disabled="isLoggingOut">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                </svg>
                {{ isLoggingOut ? '退出中...' : '退出登录' }}
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </header>

    <main class="page-main">
      <div class="dashboard-content">
        <div class="welcome-card">
          <h2>欢迎，{{ authStore.user?.username || '用户' }}!</h2>
          <p>您已成功登录到 CV Algorithm Hub</p>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon algorithms">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">0</span>
              <span class="stat-label">算法数量</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon tasks">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 11l3 3L22 4"/>
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">0</span>
              <span class="stat-label">完成任务</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon collections">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">0</span>
              <span class="stat-label">收藏夹</span>
            </div>
          </div>
        </div>

        <div class="content-grid">
          <div class="section-card">
            <h3>快捷操作</h3>
            <div class="quick-actions">
              <button class="action-btn stock-monitor" @click="goToStockMonitor">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 3v18h18"/>
                  <path d="M18 9l-5 5-4-4-3 3"/>
                </svg>
                股票监视系统
              </button>
              <button class="action-btn database" @click="goToDatabaseManager">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7c-2 0-3 1-3 3z"/>
                  <path d="M4 7h16M7 12h10M7 17h10"/>
                </svg>
                数据库管理
              </button>
              <button class="action-btn finance" @click="goToFinanceManager">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                金融数据管理
              </button>
              <button class="action-btn explorer" @click="goToDataExplorer">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                  <path d="M8 12h8M8 16h4"/>
                </svg>
                数据浏览器
              </button>
              <button class="action-btn primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 5v14M5 12h14"/>
                </svg>
                新建算法
              </button>
              <button class="action-btn secondary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                </svg>
                浏览算法
              </button>
            </div>
          </div>

          <div class="section-card">
            <h3>最近活动</h3>
            <div class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p>暂无最近活动</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

:global(.dark) .dashboard-page {
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
  gap: 1.5rem;
}

.user-dropdown {
  position: relative;
}

.user-avatar-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-avatar-btn:hover {
  background: #f3f4f6;
}

:global(.dark) .user-avatar-btn:hover {
  background: #374151;
}

.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 50%;
}

.chevron {
  width: 1rem;
  height: 1rem;
  color: #6b7280;
  transition: transform 0.2s ease;
}

:global(.dark) .chevron {
  color: #9ca3af;
}

.chevron.rotated {
  transform: rotate(180deg);
}

.user-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 260px;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  z-index: 100;
}

:global(.dark) .user-menu {
  background: #1f2937;
  border-color: #374151;
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
}

.menu-user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 50%;
}

.menu-user-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.menu-user-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:global(.dark) .menu-user-name {
  color: #f3f4f6;
}

.menu-user-email {
  font-size: 0.8rem;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:global(.dark) .menu-user-email {
  color: #9ca3af;
}

.menu-divider {
  height: 1px;
  background: #e5e7eb;
}

:global(.dark) .menu-divider {
  background: #374151;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.875rem 1rem;
  font-size: 0.95rem;
  color: #374151;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

:global(.dark) .menu-item {
  color: #f3f4f6;
}

.menu-item:hover {
  background: #f3f4f6;
}

:global(.dark) .menu-item:hover {
  background: #374151;
}

.menu-item.logout {
  color: #dc2626;
}

:global(.dark) .menu-item.logout {
  color: #f87171;
}

.menu-item.logout:hover {
  background: #fef2f2;
}

:global(.dark) .menu-item.logout:hover {
  background: #7f1d1d;
}

.menu-item svg {
  width: 1.25rem;
  height: 1.25rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-main {
  flex: 1;
  padding: 2rem;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  padding: 2rem;
  background: white;
  border-radius: 1rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .welcome-card {
  background: #1f2937;
}

.welcome-card h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .welcome-card h2 {
  color: #f3f4f6;
}

.welcome-card p {
  margin: 0;
  color: #6b7280;
}

:global(.dark) .welcome-card p {
  color: #9ca3af;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .stat-card {
  background: #1f2937;
}

.stat-icon {
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
}

.stat-icon svg {
  width: 1.75rem;
  height: 1.75rem;
}

.stat-icon.algorithms {
  background: #dbeafe;
  color: #2563eb;
}

.stat-icon.tasks {
  background: #dcfce7;
  color: #16a34a;
}

.stat-icon.collections {
  background: #fef3c7;
  color: #d97706;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
}

:global(.dark) .stat-value {
  color: #f3f4f6;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .stat-label {
  color: #9ca3af;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.section-card {
  padding: 1.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .section-card {
  background: #1f2937;
}

.section-card h3 {
  margin: 0 0 1.25rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .section-card h3 {
  color: #f3f4f6;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  font-size: 0.95rem;
  font-weight: 500;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
}

:global(.dark) .action-btn.secondary {
  background: #374151;
  color: #f3f4f6;
  border-color: #4b5563;
}

.action-btn.secondary:hover {
  background: #e5e7eb;
}

:global(.dark) .action-btn.secondary:hover {
  background: #4b5563;
}

.action-btn.stock-monitor {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.action-btn.stock-monitor:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.action-btn.database {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.action-btn.database:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.action-btn.finance {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.action-btn.finance:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.action-btn.explorer {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: white;
}

.action-btn.explorer:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: #9ca3af;
}

.empty-state svg {
  width: 3rem;
  height: 3rem;
  margin-bottom: 0.75rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}
</style>
