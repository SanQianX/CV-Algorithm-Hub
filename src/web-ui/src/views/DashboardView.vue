<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ModeToggle from '@/components/ui/ModeToggle.vue'

const authStore = useAuthStore()
const router = useRouter()
const isLoggingOut = ref(false)
const showUserMenu = ref(false)

// 1. 结构化菜单配置：方便后期随时增加"管理模块"
const navMenu = ref([
  {
    title: '金融管理',
    key: 'finance',
    children: [
      { name: '股票监视系统', route: '/stock-monitor' },
      { name: '金融本地数据存储管理', route: '/db-manager/finance' },
      { name: '基金监控', route: '/fund-monitor' }
    ]
  },
  {
    title: '技术管理',
    key: 'tech',
    children: [
      { name: '技术模块 (开发中)', route: '/analytics' }
    ]
  },
  {
    title: '系统管理',
    key: 'system',
    children: [
      { name: '所有用户信息管理', route: '/db-manager/users' },
      { name: '数据库状态', route: '/database' },
      { name: '系统设置', route: '/settings' }
    ]
  }
])

const activeDropdown = ref<string | null>(null)

const navigateTo = (path: string) => {
  activeDropdown.value = null
  router.push(path)
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const handleLogout = async () => {
  isLoggingOut.value = true
  closeUserMenu()
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  authStore.initAuth()
})
</script>

<template>
  <div class="minimal-dashboard">
    <header class="nav-bar">
      <div class="nav-inner">
        <div class="logo" @click="router.push('/dashboard')">ALGO HUB</div>

        <div class="menu-group">
          <div
            v-for="menu in navMenu"
            :key="menu.key"
            class="menu-item"
            @mouseenter="activeDropdown = menu.key"
            @mouseleave="activeDropdown = null"
          >
            <div class="menu-label">
              {{ menu.title }}
              <span class="arrow"></span>
            </div>

            <Transition name="fade-slide">
              <div v-if="activeDropdown === menu.key" class="dropdown">
                <div
                  v-for="child in menu.children"
                  :key="child.name"
                  class="dropdown-link"
                  @click="navigateTo(child.route)"
                >
                  {{ child.name }}
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <div class="nav-right">
          <ModeToggle />
          <div class="user-dropdown">
            <button class="user-profile" @click="toggleUserMenu">
              <div class="avatar">{{ authStore.user?.username?.charAt(0) || 'A' }}</div>
              <span class="name">{{ authStore.user?.username || '管理员' }}</span>
              <svg class="chevron" :class="{ rotated: showUserMenu }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
            <Transition name="fade">
              <div v-if="showUserMenu" class="user-menu">
                <div class="user-menu-item logout" @click="handleLogout" :disabled="isLoggingOut">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                  </svg>
                  {{ isLoggingOut ? '退出中...' : '退出登录' }}
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </header>

    <main class="hero-stage">
      <div class="hero-text">
        <h1 class="main-title">智能化金融算法管理平台</h1>
        <p class="main-subtitle">极简设计，驱动复杂数据分析。请通过上方菜单访问各管理模块。</p>
      </div>

      <div class="quick-tiles">
        <div class="tile" @click="navigateTo('/stock-monitor')">
          <div class="tile-icon">📈</div>
          <span>进入监视系统</span>
        </div>
        <div class="tile" @click="navigateTo('/db-manager/finance')">
          <div class="tile-icon">📂</div>
          <span>数据存储管理</span>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* 极简主义设计规范 */
.minimal-dashboard {
  min-height: 100vh;
  background-color: #f9fafb;
  color: #111827;
  font-family: 'Inter', -apple-system, sans-serif;
}

:global(.dark) .minimal-dashboard {
  background-color: #111827;
  color: #f3f4f6;
}

/* 顶部导航 */
.nav-bar {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}

:global(.dark) .nav-bar {
  background: #1f2937;
  border-color: #374151;
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 2rem;
}

.logo {
  font-weight: 800;
  font-size: 1.25rem;
  letter-spacing: -0.5px;
  cursor: pointer;
  margin-right: 3rem;
  color: #2563eb;
}

:global(.dark) .logo {
  color: #60a5fa;
}

.menu-group {
  display: flex;
  gap: 2rem;
  height: 100%;
}

.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.menu-label {
  font-size: 0.95rem;
  font-weight: 500;
  color: #4b5563;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

:global(.dark) .menu-label {
  color: #9ca3af;
}

.menu-item:hover .menu-label {
  color: #2563eb;
}

:global(.dark) .menu-item:hover .menu-label {
  color: #60a5fa;
}

.arrow {
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid currentColor;
  margin-left: 0.25rem;
}

/* 下拉框 */
.dropdown {
  position: absolute;
  top: 100%;
  left: -1rem;
  width: 220px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  padding: 0.5rem;
}

:global(.dark) .dropdown {
  background: #1f2937;
  border-color: #374151;
}

.dropdown-link {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: pointer;
}

:global(.dark) .dropdown-link {
  color: #f3f4f6;
}

.dropdown-link:hover {
  background: #f3f4f6;
  color: #2563eb;
}

:global(.dark) .dropdown-link:hover {
  background: #374151;
  color: #60a5fa;
}

/* 导航右侧 */
.nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.user-dropdown {
  position: relative;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

:global(.dark) .user-profile {
  border-color: #4b5563;
}

.user-profile:hover {
  background: #f3f4f6;
}

:global(.dark) .user-profile:hover {
  background: #374151;
}

.avatar {
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 50%;
}

.name {
  font-size: 0.875rem;
  color: #374151;
}

:global(.dark) .name {
  color: #f3f4f6;
}

.chevron {
  width: 1rem;
  height: 1rem;
  color: #6b7280;
  transition: transform 0.2s;
}

:global(.dark) .chevron {
  color: #9ca3af;
}

.chevron.rotated {
  transform: rotate(180deg);
}

/* 用户菜单 */
.user-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 160px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

:global(.dark) .user-menu {
  background: #1f2937;
  border-color: #374151;
}

.user-menu-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

:global(.dark) .user-menu-item {
  color: #f3f4f6;
}

.user-menu-item:hover {
  background: #f3f4f6;
}

:global(.dark) .user-menu-item:hover {
  background: #374151;
}

.user-menu-item.logout {
  color: #dc2626;
}

:global(.dark) .user-menu-item.logout {
  color: #f87171;
}

.user-menu-item.logout:hover {
  background: #fef2f2;
}

:global(.dark) .user-menu-item.logout:hover {
  background: #7f1d1d;
}

.user-menu-item svg {
  width: 1rem;
  height: 1rem;
}

/* 主展示区 */
.hero-stage {
  padding: 120px 2rem;
  text-align: center;
}

.main-title {
  font-size: 3rem;
  font-weight: 800;
  color: #111827;
  margin-bottom: 1rem;
}

:global(.dark) .main-title {
  color: #f3f4f6;
}

.main-subtitle {
  color: #6b7280;
  font-size: 1.2rem;
  margin-bottom: 3rem;
}

:global(.dark) .main-subtitle {
  color: #9ca3af;
}

/* 快速操作磁贴 */
.quick-tiles {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
}

.tile {
  background: white;
  padding: 2rem;
  width: 200px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.3s;
}

:global(.dark) .tile {
  background: #1f2937;
  border-color: #374151;
}

.tile:hover {
  transform: translateY(-5px);
  border-color: #2563eb;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
}

:global(.dark) .tile:hover {
  border-color: #60a5fa;
}

.tile-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.tile span {
  font-size: 0.95rem;
  color: #374151;
  font-weight: 500;
}

:global(.dark) .tile span {
  color: #f3f4f6;
}

/* 动画效果 */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.2s ease;
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .main-title {
    font-size: 2rem;
  }

  .quick-tiles {
    flex-direction: column;
    align-items: center;
  }

  .menu-group {
    display: none;
  }
}
</style>
