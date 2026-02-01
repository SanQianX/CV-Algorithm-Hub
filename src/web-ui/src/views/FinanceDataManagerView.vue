<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ModeToggle from '@/components/ui/ModeToggle.vue'

const router = useRouter()

// API基础URL
const API_BASE = ''

// 状态变量
const isLoading = ref(false)
const isRefreshing = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// 筛选状态
const filterType = ref<'all' | 'stock' | 'fund'>('all')
const searchKeyword = ref('')

// 数据统计
const stats = ref({
  total: 0,
  stockCount: 0,
  fundCount: 0
})

// 金融数据列表
const financeData = ref<Array<{
  id: string
  name: string
  code: string
  type: 'stock' | 'fund'
  dateRange: string
  startDate: string
  endDate: string
  lastUpdate: string
  memorySize: string
  memorySizeBytes: number
}>>([])

// 显示消息
const showMessage = (msg: string, type: 'success' | 'error') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

// 获取认证头
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

// 获取类型标签文本
const getTypeLabel = (type: string) => {
  return type === 'stock' ? '股票' : '基金'
}

// 获取类型标签类名
const getTypeClass = (type: string) => {
  return type === 'stock' ? 'stock-tag' : 'fund-tag'
}

// 筛选后的数据
const filteredData = ref<typeof financeData.value>([])

// 筛选数据
const applyFilter = () => {
  let result = [...financeData.value]

  // 类型筛选
  if (filterType.value !== 'all') {
    result = result.filter(item => item.type === filterType.value)
  }

  // 搜索筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    result = result.filter(item =>
      item.name.toLowerCase().includes(keyword) ||
      item.code.toLowerCase().includes(keyword)
    )
  }

  filteredData.value = result
}

// 刷新数据
const refreshData = async () => {
  isRefreshing.value = true
  await fetchData()
  isRefreshing.value = false
}

// 获取数据
const fetchData = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/db-manager/finance/all`, {
      headers: getAuthHeaders()
    })

    if (res.ok) {
      const data = await res.json()
      financeData.value = data.items || []
      filteredData.value = [...financeData.value]

      // 更新统计数据
      stats.value.total = data.total || 0
      stats.value.stockCount = data.stockCount || 0
      stats.value.fundCount = data.fundCount || 0

      showMessage('数据加载成功', 'success')
    } else {
      const err = await res.json()
      showMessage(err.detail || '加载数据失败', 'error')
      financeData.value = []
      filteredData.value = []
    }
  } catch (e) {
    console.error('加载数据失败:', e)
    showMessage('加载数据失败', 'error')
    financeData.value = []
    filteredData.value = []
  } finally {
    isLoading.value = false
  }
}

// 页面加载
onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="finance-manager-page">
    <header class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/dashboard')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          返回
        </button>
        <h1 class="logo">金融数据管理</h1>
      </div>
      <div class="header-right">
        <ModeToggle />
      </div>
    </header>

    <main class="page-main">
      <div class="container">
        <!-- 消息提示 -->
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>

        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon blue">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total }}</span>
              <span class="stat-label">总数量</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon green">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.stockCount }}</span>
              <span class="stat-label">股票数量</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon purple">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 7.125C2.25 6.504 2.754 6 3.375 6h6c.621 0 1.125.504 1.125 1.125v3.75c0 .621-.504 1.125-1.125 1.125h-6a1.125 1.125 0 01-1.125-1.125v-3.75zM14.25 8.625c0-.621.504-1.125 1.125-1.125h5.25c.621 0 1.125.504 1.125 1.125v8.25c0 .621-.504 1.125-1.125 1.125h-5.25a1.125 1.125 0 01-1.125-1.125v-8.25zM3.75 16.125c0-.621.504-1.125 1.125-1.125h5.25c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125h-5.25a1.125 1.125 0 01-1.125-1.125v-2.25zM13.5 8.25v4.5m0-4.5h4.5m-4.5 0L18 12" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.fundCount }}</span>
              <span class="stat-label">基金数量</span>
            </div>
          </div>
        </div>

        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <div class="filter-group">
              <label>类型：</label>
              <button
                v-for="type in [
                  { key: 'all', label: '全部' },
                  { key: 'stock', label: '股票' },
                  { key: 'fund', label: '基金' }
                ]"
                :key="type.key"
                :class="['filter-btn', { active: filterType === type.key }]"
                @click="filterType = type.key as any; applyFilter()"
              >
                {{ type.label }}
              </button>
            </div>

            <div class="search-box">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <input
                v-model="searchKeyword"
                @input="applyFilter"
                type="text"
                placeholder="搜索名称或编码..."
              />
            </div>
          </div>

          <div class="toolbar-right">
            <button class="refresh-btn" @click="refreshData" :disabled="isRefreshing">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              {{ isRefreshing ? '刷新中...' : '刷新' }}
            </button>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>名称</th>
                <th>编码</th>
                <th>类型</th>
                <th>时间范围</th>
                <th>更新时间</th>
                <th>内存占用</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!isLoading && filteredData.length === 0">
                <td colspan="6" class="empty-state">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125m-3.75 0v7.5c0 .621.504 1.125 1.125 1.125m3.75-3.75C9.496 8.25 10 7.746 10 7.125m-3.75 0v3.75c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M9 12.75h3.75M9 12.75V5.625m0 7.5h3.75M9 12.75V5.625m0 7.5H6m0 7.5v7.5c0 .621.504 1.125 1.125 1.125m3.75-7.5h-3.75m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125m-3.75 0v7.5c0 .621.504 1.125 1.125 1.125m3.75-3.75C9.496 8.25 10 7.746 10 7.125m-3.75 0v3.75c0 .621.504 1.125 1.125 1.125m0 0h1.5" />
                  </svg>
                  <p>暂无数据</p>
                </td>
              </tr>
              <tr v-else-if="isLoading">
                <td colspan="6" class="loading-state">
                  <div class="spinner"></div>
                  <p>加载中...</p>
                </td>
              </tr>
              <tr v-for="item in filteredData" :key="item.id">
                <td class="name-cell">{{ item.name }}</td>
                <td class="code-cell">{{ item.code }}</td>
                <td class="type-cell">
                  <span :class="['type-tag', getTypeClass(item.type)]">
                    {{ getTypeLabel(item.type) }}
                  </span>
                </td>
                <td class="date-range-cell">{{ item.dateRange }}</td>
                <td class="update-time-cell">{{ item.lastUpdate }}</td>
                <td class="memory-cell">
                  <div class="memory-bar">
                    <div class="memory-fill" :style="{ width: Math.min(100, (item.memorySizeBytes / (1024 * 1024 * 100)) * 100) + '%' }"></div>
                  </div>
                  <span class="memory-size">{{ item.memorySize }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.finance-manager-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

:global(.dark) .finance-manager-page {
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
}

:global(.dark) .back-btn {
  color: #9ca3af;
  border-color: #4b5563;
}

.back-btn:hover {
  background: #f3f4f6;
}

:global(.dark) .back-btn:hover {
  background: #374151;
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

.page-main {
  flex: 1;
  padding: 2rem;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
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

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
}

.stat-icon svg {
  width: 1.5rem;
  height: 1.5rem;
}

.stat-icon.blue {
  background: #eff6ff;
  color: #3b82f6;
}

:global(.dark) .stat-icon.blue {
  background: #1e3a5f;
  color: #60a5fa;
}

.stat-icon.green {
  background: #ecfdf5;
  color: #10b981;
}

:global(.dark) .stat-icon.green {
  background: #064e3b;
  color: #34d399;
}

.stat-icon.purple {
  background: #f5f3ff;
  color: #8b5cf6;
}

:global(.dark) .stat-icon.purple {
  background: #4c1d95;
  color: #a78bfa;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
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

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

:global(.dark) .toolbar {
  background: #1f2937;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .filter-group label {
  color: #9ca3af;
}

.filter-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #6b7280;
  background: transparent;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

:global(.dark) .filter-btn {
  color: #9ca3af;
  border-color: #4b5563;
}

.filter-btn:hover {
  background: #f3f4f6;
}

:global(.dark) .filter-btn:hover {
  background: #374151;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
}

:global(.dark) .search-box {
  background: #374151;
  border-color: #4b5563;
}

.search-box svg {
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
}

.search-box input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.875rem;
  color: #1f2937;
  width: 200px;
}

:global(.dark) .search-box input {
  color: #f3f4f6;
}

.search-box input::placeholder {
  color: #9ca3af;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: white;
  background: #3b82f6;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #2563eb;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn svg {
  width: 1rem;
  height: 1rem;
}

/* 数据表格 */
.table-container {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

:global(.dark) .table-container {
  background: #1f2937;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

:global(.dark) .data-table th,
:global(.dark) .data-table td {
  border-color: #374151;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

:global(.dark) .data-table th {
  background: #374151;
  color: #f3f4f6;
}

.data-table td {
  color: #1f2937;
}

:global(.dark) .data-table td {
  color: #f3f4f6;
}

.name-cell {
  font-weight: 500;
  color: #1f2937;
}

:global(.dark) .name-cell {
  color: #f3f4f6;
}

.code-cell {
  font-family: 'Monaco', 'Consolas', monospace;
  color: #3b82f6;
}

.type-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 0.25rem;
}

.stock-tag {
  background: #ecfdf5;
  color: #059669;
}

:global(.dark) .stock-tag {
  background: #064e3b;
  color: #34d399;
}

.fund-tag {
  background: #fef3c7;
  color: #92400e;
}

:global(.dark) .fund-tag {
  background: #78350f;
  color: #fef3c7;
}

.date-range-cell {
  color: #6b7280;
}

:global(.dark) .date-range-cell {
  color: #9ca3af;
}

.update-time-cell {
  color: #6b7280;
}

:global(.dark) .update-time-cell {
  color: #9ca3af;
}

.memory-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.memory-bar {
  width: 80px;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

:global(.dark) .memory-bar {
  background: #374151;
}

.memory-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.memory-size {
  font-size: 0.75rem;
  color: #6b7280;
  min-width: 60px;
}

:global(.dark) .memory-size {
  color: #9ca3af;
}

.empty-state,
.loading-state {
  padding: 3rem;
  text-align: center;
  color: #9ca3af;
}

.empty-state svg,
.loading-state svg {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 1rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  margin: 0 auto 1rem;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box input {
    width: 100%;
  }

  .data-table {
    font-size: 0.75rem;
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
  }
}
</style>
