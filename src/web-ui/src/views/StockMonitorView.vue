<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

// API基础URL - 从环境变量读取
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

// 获取认证头
const getAuthHeaders = () => {
  const token = authStore.token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// 当前激活的模块（默认股票监视系统）
const activeModule = ref('stock-monitor')

// 模块配置
const modules = [
  { id: 'stock-monitor', name: '股票监视', icon: '📊' },
  { id: 'fund-monitor', name: '基金监视', icon: '💰' },
  { id: 'analytics', name: '数据分析', icon: '📈' },
  { id: 'alerts', name: '预警中心', icon: '🔔' }
]

// ========== 监控列表管理 ==========
interface MonitorList {
  id: string
  name: string
  description: string
  created_at: Date
  updated_at: Date
  list_type: string
  items: StockItem[]
}

interface StockItem {
  id: string
  code: string
  name: string
  item_type: 'stock' | 'fund'
  market: string
  sync_frequency: string
  sync_history: boolean
  history_range: string
  indicators: string[]
  alerts: any[]
  tags: string[]
  extra_data: any
  created_at: Date
  updated_at: Date
}

interface AlertRule {
  type: 'price' | 'change' | 'volume'
  condition: 'above' | 'below' | 'cross'
  value: number
  enabled: boolean
}

// 监控列表数据
const monitorLists = ref<MonitorList[]>([])
const isLoading = ref(false)
const errorMessage = ref('')

// 从API获取监控列表
const fetchMonitorLists = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await axios.get(`${API_URL}${API_BASE_URL}/monitor/lists`, {
      params: { list_type: 'stock' },
      headers: getAuthHeaders()
    })
    monitorLists.value = response.data.map((list: any) => ({
      ...list,
      created_at: new Date(list.created_at),
      updated_at: new Date(list.updated_at),
      items: list.items.map((item: any) => ({
        ...item,
        created_at: new Date(item.created_at),
        updated_at: new Date(item.updated_at)
      }))
    }))
    console.log('监控列表加载成功:', monitorLists.value)
  } catch (error: any) {
    console.error('获取监控列表失败:', error)
    errorMessage.value = error.response?.data?.detail || '获取监控列表失败'
    // 如果API失败，使用空数组
    monitorLists.value = []
  } finally {
    isLoading.value = false
  }
}

const currentListId = ref<string | null>(null)
const editingList = ref<MonitorList | null>(null)
const showListModal = ref(false)

// ========== 股票搜索 ==========
const searchQuery = ref('')
const searchResults = ref<StockItem[]>([])
const isSearching = ref(false)
const showSearchPanel = ref(false)

// ========== 添加/编辑股票 ==========
const addingStock = ref<Partial<StockItem> | null>(null)
const showAddStockModal = ref(false)
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
  { value: 'MA60', label: 'MA60' },
  { value: 'RSI', label: 'RSI' },
  { value: 'MACD', label: 'MACD' },
  { value: 'KDJ', label: 'KDJ' },
  { value: 'BOLL', label: 'BOLL' }
]

const tagOptions = [
  '科技股', '蓝筹', 'ETF', '新能源', '医药', '消费', '银行', '地产', '军工'
]

// 计算属性
const currentList = computed(() =>
  monitorLists.value.find(l => l.id === currentListId.value) || null
)

const currentListStocks = computed(() =>
  currentList.value?.items || []
)

// 搜索股票
const searchStocks = async () => {
  if (!searchQuery.value.trim()) return

  isSearching.value = true
  showSearchPanel.value = true

  // 模拟搜索结果
  setTimeout(() => {
    searchResults.value = [
      { id: '1', code: '000001', name: '平安银行', type: 'stock', market: 'sh', syncFrequency: 'daily', syncHistory: false, historyRange: '30', indicators: [], alerts: [], tags: [] },
      { id: '2', code: '600036', name: '招商银行', type: 'stock', market: 'sh', syncFrequency: 'daily', syncHistory: false, historyRange: '30', indicators: [], alerts: [], tags: [] },
      { id: '3', code: '000002', name: '万科A', type: 'stock', market: 'sz', syncFrequency: 'daily', syncHistory: false, historyRange: '30', indicators: [], alerts: [], tags: [] },
      { id: '4', code: '600519', name: '贵州茅台', type: 'stock', market: 'sh', syncFrequency: 'daily', syncHistory: false, historyRange: '30', indicators: [], alerts: [], tags: [] },
      { id: '5', code: '510300', name: '沪深300ETF', type: 'fund', market: 'sh', syncFrequency: 'daily', syncHistory: false, historyRange: '30', indicators: [], alerts: [], tags: [] }
    ].filter(s =>
      s.code.includes(searchQuery.value) ||
      s.name.includes(searchQuery.value)
    )
    isSearching.value = false
  }, 500)
}

// 创建新列表
const createList = () => {
  editingList.value = {
    id: '',
    name: '',
    description: '',
    created_at: new Date(),
    updated_at: new Date(),
    list_type: 'stock',
    items: []
  }
  showListModal.value = true
}

// 编辑列表
const editList = (list: MonitorList) => {
  editingList.value = { ...list }
  showListModal.value = true
}

// 保存列表（创建或更新）
const saveList = async () => {
  if (!editingList.value) return

  try {
    if (editingList.value.id) {
      // 更新现有列表
      const response = await axios.put(
        `${API_URL}${API_BASE_URL}/monitor/lists/${editingList.value.id}`,
        {
          name: editingList.value.name,
          description: editingList.value.description
        },
        { headers: getAuthHeaders() }
      )
      // 更新本地数据
      const index = monitorLists.value.findIndex(l => l.id === editingList.value!.id)
      if (index !== -1) {
        monitorLists.value[index] = {
          ...monitorLists.value[index],
          name: response.data.name,
          description: response.data.description,
          updated_at: new Date(response.data.updated_at)
        }
      }
    } else {
      // 创建新列表
      const response = await axios.post(
        `${API_URL}${API_BASE_URL}/monitor/lists`,
        {
          name: editingList.value.name,
          description: editingList.value.description,
          list_type: 'stock'
        },
        { headers: getAuthHeaders() }
      )
      const newList: MonitorList = {
        ...response.data,
        created_at: new Date(response.data.created_at),
        updated_at: new Date(response.data.updated_at),
        items: []
      }
      monitorLists.value.unshift(newList)
      currentListId.value = newList.id
    }
  } catch (error: any) {
    console.error('保存列表失败:', error)
    alert(error.response?.data?.detail || '保存列表失败')
    return
  }

  showListModal.value = false
  editingList.value = null
}

// 删除列表
const deleteList = async (listId: string) => {
  if (!confirm('确定要删除这个监控列表吗？')) return

  try {
    await axios.delete(
      `${API_URL}${API_BASE_URL}/monitor/lists/${listId}`,
      { headers: getAuthHeaders() }
    )
    // 从本地移除
    monitorLists.value = monitorLists.value.filter(l => l.id !== listId)
    if (currentListId.value === listId) {
      currentListId.value = monitorLists.value[0]?.id || null
    }
  } catch (error: any) {
    console.error('删除列表失败:', error)
    alert(error.response?.data?.detail || '删除列表失败')
  }
}

// 选择要添加的列表
const selectListForAdd = (listId: string) => {
  selectedListForAdd.value = listId
  showSearchPanel.value = true
}

// 添加股票到列表
const addStockToList = (stock: StockItem) => {
  addingStock.value = {
    ...stock,
    sync_frequency: 'daily',
    sync_history: true,
    history_range: '90',
    indicators: [],
    alerts: [],
    tags: []
  }
  showSearchPanel.value = false
  showAddStockModal.value = true
}

// 保存股票配置（调用API添加）
const saveStockConfig = async () => {
  if (!addingStock.value || !selectedListForAdd.value) return

  try {
    const response = await axios.post(
      `${API_URL}${API_BASE_URL}/monitor/lists/${selectedListForAdd.value}/items`,
      {
        code: addingStock.value.code,
        name: addingStock.value.name,
        item_type: addingStock.value.item_type,
        market: addingStock.value.market,
        sync_frequency: addingStock.value.sync_frequency,
        sync_history: addingStock.value.sync_history,
        history_range: addingStock.value.history_range,
        indicators: addingStock.value.indicators,
        alerts: addingStock.value.alerts,
        tags: addingStock.value.tags
      },
      { headers: getAuthHeaders() }
    )

    // 更新本地数据
    const list = monitorLists.value.find(l => l.id === selectedListForAdd.value)
    if (list) {
      list.items.push({
        ...response.data,
        created_at: new Date(response.data.created_at),
        updated_at: new Date(response.data.updated_at)
      })
    }
  } catch (error: any) {
    console.error('添加股票失败:', error)
    alert(error.response?.data?.detail || '添加股票失败')
    return
  }

  showAddStockModal.value = false
  addingStock.value = null
}

// 删除股票（调用API删除）
const removeStock = async (stockId: string) => {
  if (!confirm('确定要从列表中移除该标的吗？')) return

  try {
    await axios.delete(
      `${API_URL}${API_BASE_URL}/monitor/items/${stockId}`,
      { headers: getAuthHeaders() }
    )

    // 从本地移除
    if (currentList.value) {
      currentList.value.items = currentList.value.items.filter(s => s.id !== stockId)
    }
  } catch (error: any) {
    console.error('删除股票失败:', error)
    alert(error.response?.data?.detail || '删除股票失败')
  }
}

// 切换模块
const switchModule = (moduleId: string) => {
  activeModule.value = moduleId
  if (moduleId === 'fund-monitor') {
    router.push('/fund-monitor')
  } else if (moduleId === 'analytics') {
    router.push('/analytics')
  } else if (moduleId === 'alerts') {
    router.push('/alerts')
  }
}

onMounted(async () => {
  authStore.initAuth()
  await fetchMonitorLists()
  if (monitorLists.value.length > 0) {
    currentListId.value = monitorLists.value[0].id
  }
})
</script>

<template>
  <div class="stock-monitor-page">
    <!-- 模块切换导航 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="logo">股票基金个人监视系统</h1>
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
            <h3>监控列表</h3>
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
                <span class="list-count">{{ list.items.length }} 个标的</span>
              </div>
              <div class="list-actions">
                <button class="action-btn" @click.stop="editList(list)">编辑</button>
                <button class="action-btn delete" @click.stop="deleteList(list.id)">删除</button>
              </div>
            </div>
          </div>

          <div class="sidebar-footer">
            <button class="add-list-btn" @click="createList">
              <span>+</span> 新建监控列表
            </button>
          </div>
        </aside>

        <!-- 中间：监控列表内容 -->
        <section class="main-content">
          <!-- 加载状态 -->
          <div v-if="isLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载监控列表...</p>
          </div>

          <!-- 错误消息 -->
          <div v-else-if="errorMessage" class="error-state">
            <div class="error-icon">⚠️</div>
            <h3>加载失败</h3>
            <p>{{ errorMessage }}</p>
            <button class="btn-primary" @click="fetchMonitorLists">重试</button>
          </div>

          <div v-else-if="currentList" class="list-content">
            <div class="content-header">
              <div class="list-title">
                <h2>{{ currentList.name }}</h2>
                <p>{{ currentList.description }}</p>
              </div>
              <button class="add-stock-btn" @click="selectListForAdd(currentList.id)">
                <span>+</span> 添加标的
              </button>
            </div>

            <!-- 搜索框（快速添加） -->
            <div class="quick-search">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="输入代码或名称搜索..."
                @keyup.enter="searchStocks"
              />
              <button class="search-btn" @click="searchStocks">搜索</button>
            </div>

            <!-- 股票列表 -->
            <div class="stock-list">
              <div v-if="currentListStocks.length === 0" class="empty-state">
                <div class="empty-icon">📋</div>
                <h3>暂无监控标的</h3>
                <p>点击上方按钮添加股票或基金进行监控</p>
              </div>

              <div
                v-for="stock in currentListStocks"
                :key="stock.id"
                class="stock-card"
              >
                <div class="stock-header">
                  <div class="stock-info">
                    <span class="stock-code">{{ stock.code }}</span>
                    <span class="stock-name">{{ stock.name }}</span>
                    <span :class="['stock-type', stock.item_type]">{{ stock.item_type === 'stock' ? '股票' : '基金' }}</span>
                  </div>
                  <div class="stock-tags">
                    <span v-for="tag in stock.tags" :key="tag" class="tag">{{ tag }}</span>
                  </div>
                </div>

                <div class="stock-config">
                  <div class="config-item">
                    <label>同步频率</label>
                    <span>{{ syncFrequencyOptions.find(o => o.value === stock.sync_frequency)?.label }}</span>
                  </div>
                  <div class="config-item">
                    <label>历史数据</label>
                    <span>{{ historyRangeOptions.find(o => o.value === stock.history_range)?.label }}</span>
                  </div>
                  <div class="config-item">
                    <label>指标</label>
                    <span>{{ stock.indicators.length > 0 ? stock.indicators.join(', ') : '未配置' }}</span>
                  </div>
                </div>

                <div class="stock-actions">
                  <button class="stock-btn" @click="removeStock(stock.id)">移除</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="no-list-selected">
            <div class="empty-icon">📊</div>
            <h3>选择一个监控列表</h3>
            <p>从左侧选择一个列表，或创建一个新的监控列表</p>
          </div>
        </section>
      </div>
    </main>

    <!-- 搜索结果面板 -->
    <Transition name="slide">
      <div v-if="showSearchPanel" class="search-panel">
        <div class="search-panel-header">
          <h3>搜索结果</h3>
          <button class="close-btn" @click="showSearchPanel = false">×</button>
        </div>

        <div class="search-results">
          <div v-if="isSearching" class="loading">搜索中...</div>

          <div
            v-for="result in searchResults"
            :key="result.id"
            class="search-result-item"
            @click="addStockToList(result)"
          >
            <div class="result-info">
              <span class="result-code">{{ result.code }}</span>
              <span class="result-name">{{ result.name }}</span>
              <span :class="['result-type', result.type]">{{ result.type === 'stock' ? '股票' : '基金' }}</span>
              <span :class="['result-market', result.market]">{{ result.market === 'sh' ? '沪市' : '深市' }}</span>
            </div>
            <button class="add-btn-small">添加</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 新建/编辑列表弹窗 -->
    <Transition name="fade">
      <div v-if="showListModal" class="modal-overlay" @click.self="showListModal = false">
        <div class="modal">
          <div class="modal-header">
            <h3>{{ editingList?.id ? '编辑监控列表' : '新建监控列表' }}</h3>
            <button class="close-btn" @click="showListModal = false">×</button>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label>列表名称</label>
              <input v-model="editingList!.name" type="text" placeholder="输入列表名称" />
            </div>
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="editingList!.description" placeholder="列表描述（可选）" rows="3"></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="showListModal = false">取消</button>
            <button class="btn-primary" @click="saveList">保存</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 添加股票配置弹窗 -->
    <Transition name="fade">
      <div v-if="showAddStockModal" class="modal-overlay" @click.self="showAddStockModal = false">
        <div class="modal modal-large">
          <div class="modal-header">
            <h3>配置监控参数</h3>
            <button class="close-btn" @click="showAddStockModal = false">×</button>
          </div>

          <div v-if="addingStock" class="modal-body">
            <div class="stock-preview">
              <span class="stock-code">{{ addingStock.code }}</span>
              <span class="stock-name">{{ addingStock.name }}</span>
            </div>

            <div class="config-section">
              <h4>同步设置</h4>
              <div class="form-row">
                <div class="form-group">
                  <label>同步频率</label>
                  <select v-model="addingStock.syncFrequency">
                    <option v-for="opt in syncFrequencyOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>历史数据范围</label>
                  <select v-model="addingStock.historyRange">
                    <option v-for="opt in historyRangeOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="form-group checkbox-group">
                <label>
                  <input type="checkbox" v-model="addingStock.syncHistory" />
                  同步历史数据
                </label>
              </div>
            </div>

            <div class="config-section">
              <h4>计算指标</h4>
              <div class="checkbox-group">
                <label v-for="opt in indicatorOptions" :key="opt.value" class="checkbox-item">
                  <input type="checkbox" :value="opt.value" v-model="addingStock.indicators" />
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
                  :class="['tag-option', { selected: addingStock.tags?.includes(tag) }]"
                >
                  <input
                    type="checkbox"
                    :value="tag"
                    v-model="addingStock.tags"
                    hidden
                  />
                  {{ tag }}
                </label>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="showAddStockModal = false">取消</button>
            <button class="btn-primary" @click="saveStockConfig">保存配置</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.stock-monitor-page {
  min-height: 100vh;
  background: #f3f4f6;
}

:global(.dark) .stock-monitor-page {
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
  background: #3b82f6;
  border-color: #3b82f6;
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
  background: #3b82f6;
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
  background: #eff6ff;
}

:global(.dark) .list-item.active {
  background: #1e3a5f;
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

.add-stock-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.add-stock-btn:hover {
  background: #2563eb;
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

/* 股票列表 */
.stock-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stock-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .stock-card {
  background: #1f2937;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stock-code {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

:global(.dark) .stock-code {
  color: #f3f4f6;
}

.stock-name {
  color: #374151;
  font-size: 1rem;
}

:global(.dark) .stock-name {
  color: #d1d5db;
}

.stock-type {
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.stock-type.stock {
  background: #dbeafe;
  color: #1d4ed8;
}

.stock-type.fund {
  background: #d1fae5;
  color: #059669;
}

.stock-tags {
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

.stock-config {
  display: flex;
  gap: 2rem;
  padding: 1rem 0;
  border-top: 1px solid #f3f4f6;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 1rem;
}

:global(.dark) .stock-config {
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

.stock-actions {
  display: flex;
  justify-content: flex-end;
}

.stock-btn {
  padding: 0.5rem 1rem;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

:global(.dark) .stock-btn {
  background: #7f1d1d;
  color: #f87171;
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

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 4rem 2rem;
  color: #6b7280;
}

:global(.dark) .loading-state {
  color: #9ca3af;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

:global(.dark) .loading-spinner {
  border-color: #374151;
  border-top-color: #3b82f6;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #6b7280;
  text-align: center;
}

:global(.dark) .error-state {
  color: #9ca3af;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  margin: 0 0 0.5rem;
  color: #dc2626;
}

:global(.dark) .error-state h3 {
  color: #f87171;
}

.error-state p {
  margin: 0 0 1.5rem;
  color: #6b7280;
}

:global(.dark) .error-state p {
  color: #9ca3af;
}


/* 搜索面板 */
.search-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
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

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.search-results {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.loading {
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
}

:global(.dark) .result-name {
  color: #d1d5db;
}

.result-type {
  padding: 0.15rem 0.4rem;
  border-radius: 0.2rem;
  font-size: 0.7rem;
}

.result-type.stock {
  background: #dbeafe;
  color: #1d4ed8;
}

.result-type.fund {
  background: #d1fae5;
  color: #059669;
}

.result-market {
  font-size: 0.75rem;
  color: #6b7280;
}

.add-btn-small {
  padding: 0.4rem 0.75rem;
  background: #3b82f6;
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

.stock-preview {
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

:global(.dark) .stock-preview {
  background: #374151;
}

.stock-preview .stock-code {
  font-weight: 600;
  margin-right: 0.75rem;
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
  background: #3b82f6;
  color: white;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
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
