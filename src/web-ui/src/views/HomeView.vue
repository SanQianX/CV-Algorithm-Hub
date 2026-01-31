<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ModeToggle from '@/components/ui/ModeToggle.vue'

const router = useRouter()

const handleLogin = () => {
  router.push('/login')
}

const handleRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1>CV Algorithm Hub</h1>
      <ModeToggle />
    </header>

    <main class="app-main">
      <div class="hero-section">
        <h2>计算机视觉算法分享平台</h2>
        <p>发现、使用、分享高质量的 CV 算法</p>

        <div class="action-buttons">
          <button class="btn primary" @click="handleLogin">
            登录
          </button>
          <button class="btn secondary" @click="handleRegister">
            注册
          </button>
        </div>
      </div>

      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
          </div>
          <h3>快速部署</h3>
          <p>一键部署算法到云端 GPU</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
            </svg>
          </div>
          <h3>丰富算法库</h3>
          <p>涵盖目标检测、分割、识别等</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
            </svg>
          </div>
          <h3>社区分享</h3>
          <p>与开发者交流心得</p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

:global(.dark) .app-header {
  background: #1f2937;
  border-color: #374151;
}

.app-header h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

:global(.dark) .app-header h1 {
  color: #f3f4f6;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

:global(.dark) .app-main {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.hero-section {
  text-align: center;
  margin-bottom: 4rem;
}

.hero-section h2 {
  margin: 0 0 1rem;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
}

:global(.dark) .hero-section h2 {
  color: #f3f4f6;
}

.hero-section p {
  margin: 0 0 2rem;
  font-size: 1.25rem;
  color: #6b7280;
}

:global(.dark) .hero-section p {
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.875rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
}

.btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

.btn.secondary {
  background: white;
  color: #374151;
  border: 2px solid #e5e7eb;
}

:global(.dark) .btn.secondary {
  background: #1f2937;
  color: #f3f4f6;
  border-color: #4b5563;
}

.btn.secondary:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  width: 100%;
}

.feature-card {
  padding: 2rem;
  background: white;
  border-radius: 1rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

:global(.dark) .feature-card {
  background: #1f2937;
}

.feature-icon {
  width: 3.5rem;
  height: 3.5rem;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #dbeafe;
  border-radius: 0.75rem;
  color: #2563eb;
}

:global(.dark) .feature-icon {
  background: #1e3a5f;
  color: #60a5fa;
}

.feature-icon svg {
  width: 1.75rem;
  height: 1.75rem;
}

.feature-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .feature-card h3 {
  color: #f3f4f6;
}

.feature-card p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .feature-card p {
  color: #9ca3af;
}
</style>
