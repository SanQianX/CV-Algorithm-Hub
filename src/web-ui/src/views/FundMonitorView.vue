<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMonitorStore } from '@/stores/monitor'

const router = useRouter()
const authStore = useAuthStore()
const monitorStore = useMonitorStore()

// 当前激活的模块（默认股票监视系统）
const activeModule = ref('fund-monitor')

// 模块配置
const modules = [
  { id: 'stock-monitor', name: '股票监视', icon: '📊' },
  { id: 'fund-monitor', name: '基金监视', icon: '💰' },
  { id: 'analytics', name: '数据分析', icon: '📈' },
  { id: 'alerts', name: '预警中心', icon: '🔔' }
]

// ========== 监控列表管理 ==========
interface FundItem {
  id: string
  code: string
  name: string
  item_type: string
  nav?: number
  change?: number
  change_percent?: number
  sync_frequency: string
  sync_history: boolean
  history_range: string
  indicators: string[]
  alerts: any[]
  tags: string[]
  extra_data?: any
}

// 计算属性
const monitorLists = computed(() => monitorStore.getListsByType('fund'))
const currentListId = ref<string | null>(null)
const editingList = ref<any>(null)
const showListModal = ref(false)

// ========== 基金搜索 ==========
const searchQuery = ref('')
const searchResults = ref<FundItem[]>([])
const isSearching = ref(false)
const showSearchPanel = ref(false)
const searchStatus = ref<'idle' | 'loading' | 'success' | 'error'>('idle')
const searchMessage = ref('')
const useMockData = ref(false) // 调试开关：true=使用模拟数据，false=使用API

// ========== 添加/编辑基金 ==========
const addingFund = ref<Partial<FundItem> | null>(null)
const showAddFundModal = ref(false)
const selectedListForAdd = ref<string | null>(null)

// ========== 同步频率选项 ==========
const syncFrequencyOptions = [
  { value: 'realtime', label: '实时' },
  { value: 'daily', label: '每日' },
  { value: 'weekly', label: '每周' },
  { value: 'manual', label: '手动' }
]

const historyRangeOptions = [
  { value: '30', label: '30天' },
  { value: '90', label: '90天' },
  { value: '180', label: '180天' },
  { value: '365', label: '365天' },
  { value: 'all', label: '全部' }
]

const indicatorOptions = [
  { value: 'MA5', label: 'MA5' },
  { value: 'MA10', label: 'MA10' },
  { value: 'MA20', label: 'MA20' },
  { value: 'RSI', label: 'RSI' },
  { value: 'MACD', label: 'MACD' }
]

const tagOptions = [
  '指数基金', '混合基金', '股票基金', '债券基金', 'QDII', 'ETF', 'LOF'
]

// 计算属性
const currentList = computed(() =>
  monitorLists.value.find(l => l.id === currentListId.value) || null
)

const currentListFunds = computed(() =>
  currentList.value?.items || []
)

// 从东方财富API搜索基金
const searchFunds = async () => {
  if (!searchQuery.value.trim()) return

  isSearching.value = true
  searchStatus.value = 'loading'
  searchMessage.value = ''
  showSearchPanel.value = true

  try {
    if (useMockData.value) {
      // 使用模拟数据
      searchMessage.value = '使用模拟数据模式'
      searchResults.value = getMockFunds(searchQuery.value)
      searchStatus.value = 'success'
    } else {
      // 使用后端代理API绕过CORS
      const token = localStorage.getItem('token')
      const proxyUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/api/v1/monitor/proxy/fund-search?key=${encodeURIComponent(searchQuery.value)}&pageSize=20`
      console.log(`[基金搜索] 请求后端代理: ${proxyUrl}`)

      const startTime = Date.now()
      const response = await fetch(proxyUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const elapsed = Date.now() - startTime

      console.log(`[基金搜索] 响应时间: ${elapsed}ms, 状态: ${response.status}`)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      console.log(`[基金搜索] API返回数据:`, data)

      if (data && data.datas && data.datas.length > 0) {
        searchResults.value = data.datas.map((item: any, index: number) => ({
          id: `api-${index}`,
          code: item.CODE || item.FCODE,
          name: item.NAME || item.SECNAME,
          item_type: 'fund',
          sync_frequency: 'daily',
          sync_history: true,
          history_range: '90',
          indicators: [],
          alerts: [],
          tags: [],
          extra_data: { nav: 0, change_percent: 0 }
        }))
        searchStatus.value = 'success'
        searchMessage.value = `✓ 成功从东方财富获取 ${searchResults.value.length} 个基金`
      } else {
        searchMessage.value = 'API返回空结果，切换到模拟数据'
        searchResults.value = getMockFunds(searchQuery.value)
        searchStatus.value = 'success'
      }
    }
  } catch (error: any) {
    console.error('[基金搜索] 失败:', error)
    searchStatus.value = 'error'
    searchMessage.value = `✗ 网络请求失败: ${error.message}，使用模拟数据`
    // 降级到模拟数据
    searchResults.value = getMockFunds(searchQuery.value)
    useMockData.value = true
  } finally {
    isSearching.value = false
  }
}

// 手动切换到模拟数据模式
const toggleMockMode = () => {
  useMockData.value = !useMockData.value
  searchMessage.value = useMockData.value ? '已切换到模拟数据模式' : '已切换到API模式'
  console.log(`[基金搜索] 模拟数据模式: ${useMockData.value}`)
}

// 模拟基金数据（当API失败时使用）
const getMockFunds = (query: string): FundItem[] => {
  const mockFunds: FundItem[] = [
    { id: '1', code: '161039', name: '富国中证新能源汽车指数', type: '指数基金', nav: 1.234, change: 0.023, changePercent: 1.87, syncFrequency: 'daily', syncHistory: true, historyRange: '90', indicators: [], alerts: [], tags: [] },
    { id: '2', code: '161032', name: '富国中证煤炭指数', type: '指数基金', nav: 2.345, change: -0.012, changePercent: -0.51, syncFrequency: 'daily', syncHistory: true, historyRange: '90', indicators: [], alerts: [], tags: [] },
    { id: '3', code: '110022', name: '易方达消费行业股票', type: '股票基金', nav: 3.456, change: 0.045, changePercent: 1.32, syncFrequency: 'daily', syncHistory: true, historyRange: '90', indicators: [], alerts: [], tags: [] },
    { id: '4', code: '000015', name: '华夏红利混合', type: '混合基金', nav: 1.567, change: 0.008, changePercent: 0.51, syncFrequency: 'daily', syncHistory: true, historyRange: '90', indicators: [], alerts: [], tags: [] },
    { id: '5', code: '000001', name: '华夏成长混合', type: '混合基金', nav: 1.123, change: -0.005, changePercent: -0.44, syncFrequency: 'daily', syncHistory: true, historyRange: '90', indicators: [], alerts: [], tags: [] }
  ]

  return mockFunds.filter(f =>
    f.code.includes(query) ||
    f.name.includes(query)
  )
}

// 获取基金实时数据（从东方财富）
const fetchFundDetail = async (fundCode: string): Promise<FundItem | null> => {
  try {
    const response = await fetch(
      `https://fund.eastmoney.com/pingzhongdata/${fundCode}.js`
    )
    const text = await response.text()

    // 解析JS数据
    const navMatch = text.match(/NAV\s*=\s*([\d.]+)/)
    const accNavMatch = text.match(/ACCNAV\s*=\s*([\d.]+)/)
    const changeMatch = text.match(/NAVCHG_PCT\s*=\s*([-\d.]+)/)
    const nameMatch = text.match(/fundShortName\s*=\s*"([^"]+)"/)

    return {
      id: Date.now().toString(),
      code: fundCode,
      name: nameMatch ? nameMatch[1] : fundCode,
      type: '基金',
      nav: navMatch ? parseFloat(navMatch[1]) : 0,
      change: 0,
      changePercent: changeMatch ? parseFloat(changeMatch[1]) : 0,
      syncFrequency: 'daily',
      syncHistory: true,
      historyRange: '90',
      indicators: [],
      alerts: [],
      tags: []
    }
  } catch (error) {
    console.error('获取基金详情失败:', error)
    return null
  }
}

// 创建新列表
const createList = () => {
  editingList.value = { id: '', name: '', description: '', list_type: 'fund' }
  showListModal.value = true
}

// 编辑列表
const editList = (list: any) => {
  editingList.value = { ...list }
  showListModal.value = true
}

// 保存列表
const saveList = async () => {
  if (!editingList.value) return

  if (editingList.value.id) {
    // 编辑
    await monitorStore.updateList(editingList.value.id, editingList.value.name, editingList.value.description)
  } else {
    // 新建
    const newList = await monitorStore.createList(editingList.value.name, editingList.value.description, 'fund')
    if (newList) {
      currentListId.value = newList.id
    }
  }

  showListModal.value = false
  editingList.value = null
}

// 删除列表
const deleteList = async (listId: string) => {
  if (confirm('确定要删除这个监控列表吗？')) {
    await monitorStore.deleteList(listId)
    if (currentListId.value === listId) {
      currentListId.value = monitorLists.value[0]?.id || null
    }
  }
}

// 选择要添加的列表
const selectListForAdd = (listId: string) => {
  selectedListForAdd.value = listId
  showSearchPanel.value = true
}

// 添加基金到列表
const addFundToList = async (fund: FundItem) => {
  // 如果有当前选中的列表，直接使用
  if (currentListId.value) {
    selectedListForAdd.value = currentListId.value
  } else if (!selectedListForAdd.value) {
    alert('请先选择一个基金池（点击左侧的基金池名称）')
    return
  }

  // 获取基金实时数据（使用后端代理，不直接从浏览器访问东方财富）
  let detail = null
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/api/v1/monitor/proxy/fund-detail?code=${fund.code}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    if (response.ok) {
      detail = await response.json()
    }
  } catch (e) {
    console.warn('获取基金详情失败，使用搜索数据', e)
  }

  const finalFund = detail || fund

  addingFund.value = {
    id: finalFund.id || '',
    code: finalFund.code,
    name: finalFund.name,
    item_type: 'fund',
    nav: finalFund.nav || 0,
    change: finalFund.nav_change || 0,
    change_percent: finalFund.nav_change_percent || 0,
    sync_frequency: 'daily',
    sync_history: true,
    history_range: '90',
    indicators: [],
    alerts: [],
    tags: [],
    extra_data: {
      nav: finalFund.nav || 0,
      change_percent: finalFund.nav_change_percent || 0,
      nav_date: finalFund.nav_date || '',
      update_time: finalFund.update_time || ''
    }
  }
  showSearchPanel.value = false
  showAddFundModal.value = true
}

// 保存基金配置
const saveFundConfig = async () => {
  if (!addingFund.value || !selectedListForAdd.value) return

  await monitorStore.addItem(selectedListForAdd.value, {
    code: addingFund.value.code,
    name: addingFund.value.name,
    item_type: 'fund',
    sync_frequency: addingFund.value.sync_frequency,
    sync_history: addingFund.value.sync_history,
    history_range: addingFund.value.history_range,
    indicators: addingFund.value.indicators,
    alerts: addingFund.value.alerts,
    tags: addingFund.value.tags,
    extra_data: addingFund.value.extra_data
  })

  showAddFundModal.value = false
  addingFund.value = null
}

// 删除基金
const removeFund = async (fundId: string) => {
  if (!confirm('确定要从列表中移除该基金吗？')) return
  await monitorStore.deleteItem(fundId)
}

// 切换模块
const switchModule = (moduleId: string) => {
  activeModule.value = moduleId
  if (moduleId === 'stock-monitor') {
    router.push('/stock-monitor')
  } else if (moduleId === 'analytics') {
    router.push('/analytics')
  } else if (moduleId === 'alerts') {
    router.push('/alerts')
  }
}

// 跳转到数据分析页面
const navigateToAnalytics = (fund: FundItem) => {
  router.push({
    path: '/analytics',
    query: {
      code: fund.code,
      type: 'fund'
    }
  })
}

onMounted(async () => {
  await authStore.initAuth()
  await monitorStore.fetchLists('fund')
  if (monitorLists.value.length > 0) {
    currentListId.value = monitorLists.value[0].id
  }
})
</script>

<template>
  <div class="fund-monitor-page">
    <!-- 模块切换导航 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="logo">基金监视系统</h1>
      </div>
      <div class="module-nav">
        <button
          v-for="module in modules"
          :key="module.id"
          :class="['module-btn', { active: activeModule === module.id }]"
          @click="switchModule(module.id)"
        >
          <span class="module-icon">{{ module.icon }}</span>
          <span class="module-name">{{ module.name }}</span>
        </button>
      </div>
      <div class="header-right">
        <button class="back-btn" @click="router.push('/dashboard')">
          返回仪表盘
        </button>
      </div>
    </header>

    <main class="page-main">
      <div class="monitor-container">
        <!-- 左侧：监控列表管理 -->
        <aside class="sidebar">
          <div class="sidebar-header">
            <h3>我的基金池</h3>
            <button class="add-btn" @click="createList">+</button>
          </div>

          <div class="list-group">
            <div
              v-for="list in monitorLists"
              :key="list.id"
              :class="['list-item', { active: currentListId === list.id }]"
              @click="currentListId = list.id"
            >
              <div class="list-info">
                <span class="list-name">{{ list.name }}</span>
                <span class="list-count">{{ list.items?.length || 0 }} 只基金</span>
              </div>
              <div class="list-actions">
                <button class="action-btn" @click.stop="editList(list)">编辑</button>
                <button class="action-btn delete" @click.stop="deleteList(list.id)">删除</button>
              </div>
            </div>
          </div>

          <div class="sidebar-footer">
            <button class="add-list-btn" @click="createList">
              <span>+</span> 新建基金池
            </button>
          </div>
        </aside>

        <!-- 中间：监控列表内容 -->
        <section class="main-content">
          <div v-if="currentList" class="list-content">
            <div class="content-header">
              <div class="list-title">
                <h2>{{ currentList.name }}</h2>
                <p>{{ currentList.description }}</p>
              </div>
              <button class="add-fund-btn" @click="selectListForAdd(currentList.id)">
                <span>+</span> 添加基金
              </button>
            </div>

            <!-- 搜索框（快速添加） -->
            <div class="quick-search">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="输入基金代码或名称搜索..."
                @keyup.enter="searchFunds"
              />
              <button class="search-btn" @click="searchFunds">搜索基金</button>
            </div>

            <!-- 基金列表 -->
            <div class="fund-list">
              <div v-if="currentListFunds.length === 0" class="empty-state">
                <div class="empty-icon">💰</div>
                <h3>暂无监控基金</h3>
                <p>点击上方按钮添加基金进行监控</p>
              </div>

              <div
                v-for="fund in currentListFunds"
                :key="fund.id"
                class="fund-card"
                @click="navigateToAnalytics(fund)"
              >
                <div class="fund-header">
                  <div class="fund-info">
                    <span class="fund-code">{{ fund.code }}</span>
                    <span class="fund-name">{{ fund.name }}</span>
                    <span class="fund-type">{{ fund.type }}</span>
                  </div>
                  <div class="fund-tags">
                    <span v-for="tag in fund.tags" :key="tag" class="tag">{{ tag }}</span>
                  </div>
                </div>

                <div class="fund-data">
                  <div class="nav-display">
                    <span class="nav-label">净值</span>
                    <span class="nav-value">{{ (fund.extra_data?.nav || fund.nav || 0).toFixed(4) }}</span>
                  </div>
                  <div class="change-display">
                    <span class="change-value" :class="(fund.extra_data?.change_percent || fund.change_percent || 0) >= 0 ? 'positive' : 'negative'">
                      {{ (fund.extra_data?.change_percent || fund.change_percent || 0) >= 0 ? '+' : '' }}{{ (fund.extra_data?.change_percent || fund.change_percent || 0).toFixed(2) }}%
                    </span>
                    <span class="change-label">日涨幅</span>
                  </div>
                </div>

                <div class="fund-config">
                  <div class="config-item">
                    <label>同步频率</label>
                    <span>{{ syncFrequencyOptions.find(o => o.value === fund.sync_frequency)?.label }}</span>
                  </div>
                  <div class="config-item">
                    <label>历史数据</label>
                    <span>{{ historyRangeOptions.find(o => o.value === fund.history_range)?.label }}</span>
                  </div>
                  <div class="config-item">
                    <label>指标</label>
                    <span>{{ fund.indicators?.length > 0 ? fund.indicators.join(', ') : '未配置' }}</span>
                  </div>
                </div>

                <div class="fund-actions" @click.stop>
                  <button class="fund-btn analyze-btn" @click="navigateToAnalytics(fund)">分析</button>
                  <button class="fund-btn" @click="removeFund(fund.id)">移除</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="no-list-selected">
            <div class="empty-icon">💰</div>
            <h3>选择一个基金池</h3>
            <p>从左侧选择一个基金池，或创建一个新的监控列表</p>
          </div>
        </section>
      </div>
    </main>

    <!-- 搜索结果面板 -->
    <Transition name="slide">
      <div v-if="showSearchPanel" class="search-panel">
        <div class="search-panel-header">
          <h3>基金搜索结果</h3>
          <button class="close-btn" @click="showSearchPanel = false">×</button>
        </div>

        <div class="search-tips">
          <p>💡 提示：可直接输入基金代码如 <code>161039</code> 或基金名称关键词搜索</p>
        </div>

        <!-- 搜索状态显示 -->
        <div class="search-status" :class="searchStatus">
          <div v-if="searchMessage" class="status-message">{{ searchMessage }}</div>
          <button class="debug-toggle" @click="toggleMockMode">
            {{ useMockData ? '🔧 使用模拟数据' : '🌐 使用网络API' }}
          </button>
        </div>

        <div class="search-results">
          <div v-if="isSearching" class="loading">
            <div class="spinner"></div>
            <span>搜索中...</span>
          </div>

          <div
            v-for="result in searchResults"
            :key="result.id"
            class="search-result-item"
            @click="addFundToList(result)"
          >
            <div class="result-info">
              <span class="result-code">{{ result.code }}</span>
              <span class="result-name">{{ result.name }}</span>
              <span class="result-type">{{ result.type }}</span>
            </div>
            <button class="add-btn-small">添加</button>
          </div>

          <div v-if="!isSearching && searchResults.length === 0 && showSearchPanel" class="no-results">
            <p>未找到相关基金，请尝试其他关键词</p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 新建/编辑列表弹窗 -->
    <Transition name="fade">
      <div v-if="showListModal" class="modal-overlay" @click.self="showListModal = false">
        <div class="modal">
          <div class="modal-header">
            <h3>{{ editingList?.id ? '编辑基金池' : '新建基金池' }}</h3>
            <button class="close-btn" @click="showListModal = false">×</button>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label>基金池名称</label>
              <input v-model="editingList!.name" type="text" placeholder="输入基金池名称" />
            </div>
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="editingList!.description" placeholder="描述（可选）" rows="3"></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="showListModal = false">取消</button>
            <button class="btn-primary" @click="saveList">保存</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 添加基金配置弹窗 -->
    <Transition name="fade">
      <div v-if="showAddFundModal" class="modal-overlay" @click.self="showAddFundModal = false">
        <div class="modal modal-large">
          <div class="modal-header">
            <h3>配置监控参数</h3>
            <button class="close-btn" @click="showAddFundModal = false">×</button>
          </div>

          <div v-if="addingFund" class="modal-body">
            <div class="fund-preview">
              <div class="preview-main">
                <span class="preview-code">{{ addingFund.code }}</span>
                <span class="preview-name">{{ addingFund.name }}</span>
              </div>
              <span class="preview-type">{{ addingFund.item_type }}</span>
            </div>

            <div class="config-section">
              <h4>同步设置</h4>
              <div class="form-row">
                <div class="form-group">
                  <label>同步频率</label>
                  <select v-model="addingFund.sync_frequency">
                    <option v-for="opt in syncFrequencyOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>历史数据范围</label>
                  <select v-model="addingFund.history_range">
                    <option v-for="opt in historyRangeOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="form-group checkbox-group">
                <label>
                  <input type="checkbox" v-model="addingFund.sync_history" />
                  同步历史净值数据
                </label>
              </div>
            </div>

            <div class="config-section">
              <h4>计算指标</h4>
              <div class="checkbox-group">
                <label v-for="opt in indicatorOptions" :key="opt.value" class="checkbox-item">
                  <input type="checkbox" :value="opt.value" v-model="addingFund.indicators" />
                  {{ opt.label }}
                </label>
              </div>
            </div>

            <div class="config-section">
              <h4>自定义标签</h4>
              <div class="tag-selector">
                <label
                  v-for="tag in tagOptions"
                  :key="tag"
                  :class="['tag-option', { selected: addingFund.tags?.includes(tag) }]"
                >
                  <input
                    type="checkbox"
                    :value="tag"
                    v-model="addingFund.tags"
                    hidden
                  />
                  {{ tag }}
                </label>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="showAddFundModal = false">取消</button>
            <button class="btn-primary" @click="saveFundConfig">保存配置</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fund-monitor-page {
  min-height: 100vh;
  background: #f3f4f6;
}

:global(.dark) .fund-monitor-page {
  background: #111827;
}

/* 模块导航 */
.module-nav {
  display: flex;
  gap: 0.5rem;
}

.module-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

:global(.dark) .module-btn {
  border-color: #374151;
  color: #9ca3af;
}

.module-btn:hover {
  background: #f3f4f6;
}

:global(.dark) .module-btn:hover {
  background: #1f2937;
}

.module-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.module-icon {
  font-size: 1.1rem;
}

/* 主容器 */
.monitor-container {
  display: flex;
  height: calc(100vh - 64px);
  gap: 1px;
  background: #e5e7eb;
}

:global(.dark) .monitor-container {
  background: #374151;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background: white;
  display: flex;
  flex-direction: column;
}

:global(.dark) .sidebar {
  background: #1f2937;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .sidebar-header {
  border-color: #374151;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}

:global(.dark) .sidebar-header h3 {
  color: #f3f4f6;
}

.add-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #10b981;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.list-group {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.list-item {
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.25rem;
}

.list-item:hover {
  background: #f3f4f6;
}

:global(.dark) .list-item:hover {
  background: #374151;
}

.list-item.active {
  background: #d1fae5;
}

:global(.dark) .list-item.active {
  background: #064e3b;
}

.list-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.list-name {
  font-weight: 500;
  color: #1f2937;
}

:global(.dark) .list-name {
  color: #f3f4f6;
}

.list-count {
  font-size: 0.8rem;
  color: #6b7280;
}

:global(.dark) .list-count {
  color: #9ca3af;
}

.list-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.action-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border: 1px solid #e5e7eb;
  background: transparent;
  border-radius: 0.25rem;
  cursor: pointer;
  color: #6b7280;
}

:global(.dark) .action-btn {
  border-color: #374151;
  color: #9ca3af;
}

.action-btn:hover {
  background: #f3f4f6;
}

:global(.dark) .action-btn:hover {
  background: #374151;
}

.action-btn.delete:hover {
  color: #dc2626;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

:global(.dark) .sidebar-footer {
  border-color: #374151;
}

.add-list-btn {
  width: 100%;
  padding: 0.75rem;
  background: #f3f4f6;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

:global(.dark) .add-list-btn {
  background: #1f2937;
  border-color: #374151;
  color: #9ca3af;
}

.add-list-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* 主内容区 */
.main-content {
  flex: 1;
  background: #f9fafb;
  overflow-y: auto;
  padding: 1.5rem;
}

:global(.dark) .main-content {
  background: #111827;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.list-title h2 {
  margin: 0;
  color: #1f2937;
}

:global(.dark) .list-title h2 {
  color: #f3f4f6;
}

.list-title p {
  margin: 0.25rem 0 0;
  color: #6b7280;
  font-size: 0.9rem;
}

:global(.dark) .list-title p {
  color: #9ca3af;
}

.add-fund-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.add-fund-btn:hover {
  background: #059669;
}

/* 快速搜索 */
.quick-search {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.quick-search input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  background: white;
}

:global(.dark) .quick-search input {
  background: #1f2937;
  border-color: #374151;
  color: #f3f4f6;
}

.search-btn {
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

/* 基金列表 */
.fund-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fund-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

:global(.dark) .fund-card {
  background: #1f2937;
}

.fund-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

:global(.dark) .fund-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.fund-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.fund-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.fund-code {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

:global(.dark) .fund-code {
  color: #f3f4f6;
}

.fund-name {
  color: #374151;
  font-size: 1rem;
}

:global(.dark) .fund-name {
  color: #d1d5db;
}

.fund-type {
  padding: 0.2rem 0.5rem;
  background: #d1fae5;
  color: #059669;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.fund-tags {
  display: flex;
  gap: 0.5rem;
}

.tag {
  padding: 0.2rem 0.5rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .tag {
  background: #374151;
  color: #9ca3af;
}

/* 基金净值展示 */
.fund-data {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

:global(.dark) .fund-data {
  background: #374151;
}

.nav-display {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-label {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .nav-label {
  color: #9ca3af;
}

.nav-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .nav-value {
  color: #f3f4f6;
}

.change-display {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.change-value {
  font-size: 1.25rem;
  font-weight: 600;
}

.change-value.positive {
  color: #dc2626;
}

.change-value.negative {
  color: #16a34a;
}

.change-label {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .change-label {
  color: #9ca3af;
}

.fund-config {
  display: flex;
  gap: 2rem;
  padding: 1rem 0;
  border-top: 1px solid #f3f4f6;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 1rem;
}

:global(.dark) .fund-config {
  border-color: #374151;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.config-item label {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .config-item label {
  color: #9ca3af;
}

.config-item span {
  font-size: 0.9rem;
  color: #1f2937;
}

:global(.dark) .config-item span {
  color: #f3f4f6;
}

.fund-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.fund-btn {
  padding: 0.5rem 1rem;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

:global(.dark) .fund-btn {
  background: #7f1d1d;
  color: #f87171;
}

.fund-btn.analyze-btn {
  background: #dbeafe;
  color: #2563eb;
}

:global(.dark) .fund-btn.analyze-btn {
  background: #1e40af;
  color: #93c5fd;
}

.fund-btn.analyze-btn:hover {
  background: #bfdbfe;
}

:global(.dark) .fund-btn.analyze-btn:hover {
  background: #2563eb;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

:global(.dark) .empty-state {
  color: #9ca3af;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: #374151;
}

:global(.dark) .empty-state h3 {
  color: #f3f4f6;
}

.no-list-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #6b7280;
}

:global(.dark) .no-list-selected {
  color: #9ca3af;
}

/* 搜索面板 */
.search-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 450px;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

:global(.dark) .search-panel {
  background: #1f2937;
}

.search-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .search-panel-header {
  border-color: #374151;
}

.search-panel-header h3 {
  margin: 0;
  color: #1f2937;
}

:global(.dark) .search-panel-header h3 {
  color: #f3f4f6;
}

.search-tips {
  padding: 0.75rem 1.25rem;
  background: #f0fdf4;
  border-bottom: 1px solid #d1fae5;
}

:global(.dark) .search-tips {
  background: #064e3b;
  border-color: #047857;
}

.search-tips p {
  margin: 0;
  font-size: 0.85rem;
  color: #166534;
}

:global(.dark) .search-tips p {
  color: #a7f3d0;
}

.search-tips code {
  background: #d1fae5;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  font-family: monospace;
}

/* 搜索状态显示 */
.search-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .search-status {
  border-color: #374151;
}

.status-message {
  font-size: 0.85rem;
  color: #6b7280;
}

.search-status.success .status-message {
  color: #059669;
}

.search-status.error .status-message {
  color: #dc2626;
}

.debug-toggle {
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background: #f3f4f6;
  cursor: pointer;
  color: #374151;
}

:global(.dark) .debug-toggle {
  background: #374151;
  border-color: #4b5563;
  color: #f3f4f6;
}

.debug-toggle:hover {
  background: #e5e7eb;
}

:global(.dark) .debug-toggle:hover {
  background: #4b5563;
}

.search-results {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #6b7280;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.search-result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

:global(.dark) .search-result-item {
  background: #374151;
}

.search-result-item:hover {
  background: #e5e7eb;
}

:global(.dark) .search-result-item:hover {
  background: #4b5563;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.result-code {
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .result-code {
  color: #f3f4f6;
}

.result-name {
  color: #374151;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:global(.dark) .result-name {
  color: #d1d5db;
}

.result-type {
  font-size: 0.75rem;
  padding: 0.15rem 0.4rem;
  background: #d1fae5;
  color: #059669;
  border-radius: 0.2rem;
}

.add-btn-small {
  padding: 0.4rem 0.75rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.8rem;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  width: 480px;
  background: white;
  border-radius: 1rem;
  overflow: hidden;
}

:global(.dark) .modal {
  background: #1f2937;
}

.modal-large {
  width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .modal-header {
  border-color: #374151;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
}

:global(.dark) .modal-header h3 {
  color: #f3f4f6;
}

.modal-body {
  padding: 1.25rem;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
}

:global(.dark) .modal-footer {
  border-color: #374151;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

:global(.dark) .form-group label {
  color: #d1d5db;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  background: white;
}

:global(.dark) .form-group input,
:global(.dark) .form-group select,
:global(.dark) .form-group textarea {
  background: #374151;
  border-color: #4b5563;
  color: #f3f4f6;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.fund-preview {
  padding: 1rem;
  background: #f0fdf4;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

:global(.dark) .fund-preview {
  background: #064e3b;
}

.preview-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.preview-code {
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .preview-code {
  color: #f3f4f6;
}

.preview-name {
  color: #374151;
}

:global(.dark) .preview-name {
  color: #d1d5db;
}

.preview-type {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: #10b981;
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.config-section {
  margin-bottom: 1.5rem;
}

.config-section h4 {
  margin: 0 0 1rem;
  color: #1f2937;
  font-size: 1rem;
}

:global(.dark) .config-section h4 {
  color: #f3f4f6;
}

.tag-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-option {
  padding: 0.4rem 0.75rem;
  background: #f3f4f6;
  border-radius: 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #6b7280;
  transition: all 0.2s ease;
}

:global(.dark) .tag-option {
  background: #374151;
  color: #9ca3af;
}

.tag-option:hover {
  background: #e5e7eb;
}

:global(.dark) .tag-option:hover {
  background: #4b5563;
}

.tag-option.selected {
  background: #10b981;
  color: white;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
}

:global(.dark) .btn-secondary {
  background: #374151;
  color: #f3f4f6;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  color: #6b7280;
}

:global(.dark) .back-btn {
  border-color: #374151;
  color: #9ca3af;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
