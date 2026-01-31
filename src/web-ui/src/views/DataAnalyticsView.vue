<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMonitorStore } from '@/stores/monitor'

// Chart.js imports
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
} from 'chart.js'
import { Line, Bar } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
)

const router = useRouter()
const authStore = useAuthStore()
const monitorStore = useMonitorStore()

// Time range options
const timeRangeOptions = [
  { value: 7, label: '7天' },
  { value: 30, label: '30天' },
  { value: 90, label: '90天' },
  { value: 180, label: '180天' },
  { value: 365, label: '1年' }
]

// Indicator options
const indicatorOptions = [
  { value: 'ma5', label: 'MA5', color: '#FF6384' },
  { value: 'ma10', label: 'MA10', color: '#36A2EB' },
  { value: 'ma20', label: 'MA20', color: '#FFCE56' },
  { value: 'rsi', label: 'RSI', color: '#4BC0C0' },
  { value: 'macd', label: 'MACD', color: '#9966FF' },
  { value: 'boll', label: 'BOLL', color: '#FF9F40' }
]

// Chart type options
const chartTypeOptions = [
  { value: 'line', label: '折线图' },
  { value: 'area', label: '面积图' }
]

// State
const selectedListId = ref<string | null>(null)
const selectedItem = ref<any | null>(null)
const timeRange = ref(90)
const selectedIndicators = ref<string[]>(['ma5', 'ma10', 'ma20'])
const chartType = ref('line')
const isLoading = ref(false)
const error = ref<string | null>(null)
const fundDetailData = ref<any>(null)

// 数据库状态
const dbDataStatus = ref<{
  hasLocalData: boolean
  lastUpdated: string | null
  dataAge: number // days
} | null>(null)
const isUpdating = ref(false)

// Date slider state
const dateSliderStart = ref(0)
const dateSliderEnd = ref(100)

// Data
const historicalData = ref<any>(null)
const indicatorsData = ref<any>(null)
const summaryData = ref<any>(null)

// Computed
const stockLists = computed(() => monitorStore.getListsByType('stock'))
const fundLists = computed(() => monitorStore.getListsByType('fund'))
const allItems = computed(() => {
  const items: any[] = []
  const lists = [...stockLists.value, ...fundLists.value]
  for (const list of lists) {
    if (list.items) {
      for (const item of list.items) {
        items.push({
          ...item,
          listName: list.name,
          listId: list.id
        })
      }
    }
  }
  return items
})

const selectedList = computed(() =>
  monitorStore.getListById(selectedListId.value || '')
)

// Filtered data for chart based on slider
const filteredDates = computed(() => {
  if (!historicalData.value?.dates) return []
  const startIdx = Math.floor((dateSliderStart.value / 100) * historicalData.value.dates.length)
  const endIdx = Math.floor((dateSliderEnd.value / 100) * historicalData.value.dates.length)
  return historicalData.value.dates.slice(startIdx, endIdx + 1)
})

const filteredPrices = computed(() => {
  if (!historicalData.value?.prices) return []
  const startIdx = Math.floor((dateSliderStart.value / 100) * historicalData.value.prices.length)
  const endIdx = Math.floor((dateSliderEnd.value / 100) * historicalData.value.prices.length)
  return historicalData.value.prices.slice(startIdx, endIdx + 1)
})

const filteredIndicators = computed(() => {
  if (!indicatorsData.value?.indicators) return {}
  const result: any = {}
  const startIdx = Math.floor((dateSliderStart.value / 100) * indicatorsData.value.dates.length)
  const endIdx = Math.floor((dateSliderEnd.value / 100) * indicatorsData.value.dates.length)

  for (const [key, value] of Object.entries(indicatorsData.value.indicators)) {
    if (Array.isArray(value)) {
      result[key] = value.slice(startIdx, endIdx + 1)
    } else if (typeof value === 'object' && value !== null) {
      // For MACD and BOLL which are objects
      result[key] = {}
      for (const [subKey, subValue] of Object.entries(value as object)) {
        if (Array.isArray(subValue)) {
          result[key][subKey] = subValue.slice(startIdx, endIdx + 1)
        }
      }
    }
  }
  return result
})

// Chart data - 使用过滤后的数据
const priceChartData = computed(() => {
  if (!historicalData.value || filteredPrices.value.length === 0) return null

  const labels = filteredDates.value
  const prices = filteredPrices.value

  const datasets: any[] = [
    {
      label: '价格',
      data: prices,
      borderColor: '#10B981',
      backgroundColor: chartType.value === 'area'
        ? 'rgba(16, 185, 129, 0.2)'
        : 'transparent',
      fill: chartType.value === 'area',
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 5,
      borderWidth: 2
    }
  ]

  // Add indicators using filtered data
  const inds = filteredIndicators.value

  if (selectedIndicators.value.includes('ma5') && inds.ma5) {
    datasets.push({
      label: 'MA5',
      data: inds.ma5,
      borderColor: '#FF6384',
      backgroundColor: 'transparent',
      borderWidth: 1.5,
      tension: 0.4,
      pointRadius: 0
    })
  }

  if (selectedIndicators.value.includes('ma10') && inds.ma10) {
    datasets.push({
      label: 'MA10',
      data: inds.ma10,
      borderColor: '#36A2EB',
      backgroundColor: 'transparent',
      borderWidth: 1.5,
      tension: 0.4,
      pointRadius: 0
    })
  }

  if (selectedIndicators.value.includes('ma20') && inds.ma20) {
    datasets.push({
      label: 'MA20',
      data: inds.ma20,
      borderColor: '#FFCE56',
      backgroundColor: 'transparent',
      borderWidth: 1.5,
      tension: 0.4,
      pointRadius: 0
    })
  }

  return { labels, datasets }
})

const rsiChartData = computed(() => {
  const inds = filteredIndicators.value
  if (!inds?.rsi || inds.rsi.length === 0) return null

  const labels = filteredDates.value
  const rsi = inds.rsi

  return {
    labels,
    datasets: [
      {
        label: 'RSI(14)',
        data: rsi,
        borderColor: '#4BC0C0',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.4,
        pointRadius: 0
      }
    ]
  }
})

const macdChartData = computed(() => {
  const inds = filteredIndicators.value
  if (!inds?.macd?.histogram) return null

  const labels = filteredDates.value
  const histogram = inds.macd.histogram

  return {
    labels,
    datasets: [
      {
        label: 'MACD',
        data: histogram,
        backgroundColor: histogram.map((v: number) =>
          v >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'
        ),
        type: 'bar' as const
      }
    ]
  }
})

// Net value chart data (for funds)
const navChartData = computed(() => {
  if (!historicalData.value?.data || historicalData.value.data.length === 0) return null

  const labels = filteredDates.value
  const navData = historicalData.value.data
    .slice(
      Math.floor((dateSliderStart.value / 100) * historicalData.value.data.length),
      Math.floor((dateSliderEnd.value / 100) * historicalData.value.data.length) + 1
    )
    .map((d: any) => d.close)

  return {
    labels,
    datasets: [
      {
        label: '单位净值',
        data: navData,
        borderColor: '#10B981',
        backgroundColor: chartType.value === 'area'
          ? 'rgba(16, 185, 129, 0.2)'
          : 'transparent',
        fill: chartType.value === 'area',
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 5,
        borderWidth: 2
      }
    ]
  }
})

// Daily change percentage chart
const dailyChangeChartData = computed(() => {
  if (!historicalData.value?.data || historicalData.value.data.length === 0) return null

  const dataSlice = historicalData.value.data
    .slice(
      Math.floor((dateSliderStart.value / 100) * historicalData.value.data.length),
      Math.floor((dateSliderEnd.value / 100) * historicalData.value.data.length) + 1
    )

  const labels = dataSlice.map((d: any) => d.date)
  const changes = dataSlice.map((d: any) => d.change_percent)

  return {
    labels,
    datasets: [
      {
        label: '日涨幅(%)',
        data: changes,
        backgroundColor: changes.map((v: number) =>
          v >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'
        ),
        type: 'bar' as const,
        borderRadius: 4
      }
    ]
  }
})

// Historical returns comparison
const returnsChartData = computed(() => {
  if (!summaryData.value) return null

  const periods = ['7d', '30d', '90d', '180d', '365d']
  const values = [
    summaryData.value.summary_7d?.change_percent || 0,
    summaryData.value.summary_30d?.change_percent || 0,
    summaryData.value.summary_90d?.change_percent || 0,
    summaryData.value.summary_180d?.change_percent || 0,
    summaryData.value.summary_365d?.change_percent || 0
  ]

  const labels = ['7日', '30日', '90日', '180日', '1年']

  return {
    labels,
    datasets: [
      {
        label: '历史业绩(%)',
        data: values,
        backgroundColor: values.map(v =>
          v >= 0 ? 'rgba(16, 185, 129, 0.8)' : 'rgba(239, 68, 68, 0.8)'
        ),
        borderRadius: 6
      }
    ]
  }
})

// Chart options
const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false
  },
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        usePointStyle: true,
        padding: 20
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      titleFont: { size: 14 },
      bodyFont: { size: 13 }
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      },
      ticks: {
        maxTicksLimit: 10
      }
    },
    y: {
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      }
    }
  }
}

// Methods
const fetchAnalyticsData = async () => {
  if (!selectedItem.value) return

  isLoading.value = true
  error.value = null

  // Reset slider when fetching new data
  dateSliderStart.value = 0
  dateSliderEnd.value = 100

  try {
    const token = localStorage.getItem('token')
    // Use empty baseUrl for relative URLs (nginx will proxy /api/ to backend)
    const baseUrl = ''
    const itemType = selectedItem.value.item_type || 'fund'
    const code = selectedItem.value.code
    const days = timeRange.value

    // Fetch historical data
    const histRes = await fetch(
      `${baseUrl}/api/v1/monitor/analytics/historical?code=${code}&item_type=${itemType}&days=${days}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    if (histRes.ok) {
      historicalData.value = await histRes.json()
    }

    // Fetch indicators
    const indRes = await fetch(
      `${baseUrl}/api/v1/monitor/analytics/indicators?code=${code}&item_type=${itemType}&days=${days}&indicators=${selectedIndicators.value.join(',')}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    if (indRes.ok) {
      indicatorsData.value = await indRes.json()
    }

    // Fetch summary
    const sumRes = await fetch(
      `${baseUrl}/api/v1/monitor/analytics/summary?code=${code}&item_type=${itemType}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    if (sumRes.ok) {
      summaryData.value = await sumRes.json()
    }

    // Fetch fund detail for funds
    if (itemType === 'fund') {
      const detailRes = await fetch(
        `${baseUrl}/api/v1/monitor/fund/fund-detail?code=${code}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      if (detailRes.ok) {
        fundDetailData.value = await detailRes.json()
      }
    } else {
      fundDetailData.value = null
    }
  } catch (e: any) {
    error.value = `获取数据失败: ${e.message}`
    console.error('Analytics fetch error:', e)
  } finally {
    isLoading.value = false
    // 检查数据库状态
    if (selectedItem.value) {
      await checkDbStatus(selectedItem.value.code, selectedItem.value.item_type)
    }
  }
}

const selectItem = (item: any) => {
  selectedItem.value = item
}

const toggleIndicator = (indicator: string) => {
  const idx = selectedIndicators.value.indexOf(indicator)
  if (idx === -1) {
    selectedIndicators.value.push(indicator)
  } else {
    selectedIndicators.value.splice(idx, 1)
  }
  // Refetch if we already have selected item
  if (selectedItem.value) {
    fetchAnalyticsData()
  }
}

const formatNumber = (num: number, decimals: number = 2) => {
  return num.toFixed(decimals)
}

const formatPercent = (num: number) => {
  const sign = num >= 0 ? '+' : ''
  return `${sign}${num.toFixed(2)}%`
}

// 检查数据库状态
const checkDbStatus = async (code: string, itemType: string) => {
  try {
    const baseUrl = ''  // Use relative URL (nginx will proxy /api/ to backend)
    const token = authStore.token

    const res = await fetch(
      `${baseUrl}/api/v1/monitor/analytics/data-status?code=${code}&item_type=${itemType}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    )

    if (res.ok) {
      dbDataStatus.value = await res.json()
    } else {
      dbDataStatus.value = null
    }
  } catch (e) {
    console.error('检查数据库状态失败:', e)
    dbDataStatus.value = null
  }
}

// 手动更新数据
const updateData = async () => {
  if (!selectedItem.value || isUpdating.value) return

  isUpdating.value = true
  error.value = null

  try {
    const baseUrl = ''  // Use relative URL
    const token = authStore.token
    const code = selectedItem.value.code
    const itemType = selectedItem.value.item_type

    const res = await fetch(
      `${baseUrl}/api/v1/monitor/analytics/update-data?code=${code}&item_type=${itemType}`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (res.ok) {
      const result = await res.json()
      // 重新获取数据
      await fetchAnalyticsData()
      await checkDbStatus(code, itemType)
      error.value = null
    } else {
      const err = await res.json()
      error.value = `更新失败: ${err.detail || '未知错误'}`
    }
  } catch (e: any) {
    error.value = `更新失败: ${e.message}`
    console.error('更新数据失败:', e)
  } finally {
    isUpdating.value = false
  }
}

// Watchers
watch([selectedItem, timeRange, selectedIndicators, chartType], () => {
  if (selectedItem.value) {
    fetchAnalyticsData()
  }
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await authStore.initAuth()
  await monitorStore.fetchLists()

  // Check for query parameters (from fund monitor navigation)
  const routeCode = router.currentRoute.value.query.code as string
  const routeType = router.currentRoute.value.query.type as string

  if (routeCode) {
    selectedItem.value = {
      code: routeCode,
      name: routeCode,
      item_type: routeType || 'fund',
      id: routeCode
    }
  } else {
    // Auto-select first list
    if (stockLists.value.length > 0) {
      selectedListId.value = stockLists.value[0].id
    } else if (fundLists.value.length > 0) {
      selectedListId.value = fundLists.value[0].id
    }
  }
})
</script>

<template>
  <div class="analytics-page">
    <!-- 模块切换导航 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="logo">数据分析</h1>
      </div>
      <div class="module-nav">
        <button
          v-for="module in [
            { id: 'stock-monitor', name: '股票监视', icon: '📊' },
            { id: 'fund-monitor', name: '基金监视', icon: '💰' },
            { id: 'analytics', name: '数据分析', icon: '📈' },
            { id: 'alerts', name: '预警中心', icon: '🔔' }
          ]"
          :key="module.id"
          :class="['module-btn', { active: module.id === 'analytics' }]"
          @click="router.push(`/${module.id}`)"
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
      <div class="analytics-container">
        <!-- 左侧：标的选择 -->
        <aside class="sidebar">
          <!-- 股票池 -->
          <div v-if="stockLists.length > 0" class="list-section">
            <div class="section-header">
              <h3>股票池</h3>
            </div>
            <div class="item-list">
              <div
                v-for="item in allItems.filter(i => i.item_type === 'stock')"
                :key="item.id"
                :class="['item-entry', { active: selectedItem?.id === item.id }]"
                @click="selectItem(item)"
              >
                <div class="item-info">
                  <span class="item-code">{{ item.code }}</span>
                  <span class="item-name">{{ item.name }}</span>
                </div>
                <span class="item-list-name">{{ item.listName }}</span>
              </div>
              <div v-if="allItems.filter(i => i.item_type === 'stock').length === 0" class="empty-tip">
                暂无股票
              </div>
            </div>
          </div>

          <!-- 基金池 -->
          <div v-if="fundLists.length > 0" class="list-section">
            <div class="section-header">
              <h3>基金池</h3>
            </div>
            <div class="item-list">
              <div
                v-for="item in allItems.filter(i => i.item_type === 'fund')"
                :key="item.id"
                :class="['item-entry', { active: selectedItem?.id === item.id }]"
                @click="selectItem(item)"
              >
                <div class="item-info">
                  <span class="item-code">{{ item.code }}</span>
                  <span class="item-name">{{ item.name }}</span>
                </div>
                <span class="item-list-name">{{ item.listName }}</span>
              </div>
              <div v-if="allItems.filter(i => i.item_type === 'fund').length === 0" class="empty-tip">
                暂无基金
              </div>
            </div>
          </div>

          <!-- 预设热门标的 -->
          <div class="list-section popular-section">
            <div class="section-header">
              <h3>热门标的</h3>
            </div>
            <div class="item-list">
              <div
                v-for="fund in [
                  { code: '018043', name: '华安纳斯达克100ETF', type: 'fund' },
                  { code: '510300', name: '华夏沪深300ETF', type: 'stock' },
                  { code: '159915', name: '华宝标普500ETF', type: 'fund' },
                  { code: '513050', name: '华夏上证50ETF', type: 'stock' }
                ]"
                :key="fund.code"
                :class="['item-entry', { active: selectedItem?.code === fund.code }]"
                @click="selectItem({ ...fund, id: fund.code })"
              >
                <div class="item-info">
                  <span class="item-code">{{ fund.code }}</span>
                  <span class="item-name">{{ fund.name }}</span>
                </div>
                <span class="item-type">{{ fund.type === 'fund' ? '基金' : '股票' }}</span>
              </div>
            </div>
          </div>
        </aside>

        <!-- 中间：图表区域 -->
        <section class="main-content">
          <div v-if="!selectedItem" class="no-selection">
            <div class="empty-icon">📈</div>
            <h3>选择一个标的进行分析</h3>
            <p>从左侧选择股票或基金查看数据分析</p>
          </div>

          <template v-else>
            <!-- 标的信息头部 -->
            <div class="header-section">
              <div class="symbol-info">
                <h2>{{ selectedItem.code }}</h2>
                <p>{{ selectedItem.name }}</p>
              </div>

              <!-- 数据库状态指示器 -->
              <div v-if="dbDataStatus" class="db-status-indicator">
                <span v-if="dbDataStatus.hasLocalData" class="status-badge synced">
                  <span class="status-dot"></span>
                  已存储 ({{ dbDataStatus.lastUpdated }})
                </span>
                <span v-else class="status-badge unsynced">
                  <span class="status-dot"></span>
                  未存储
                </span>
              </div>

              <!-- 更新按钮 -->
              <button
                class="update-btn"
                :class="{ loading: isUpdating }"
                :disabled="isUpdating"
                @click="updateData"
                title="从API更新数据到本地数据库"
              >
                <span v-if="isUpdating" class="spinner-sm"></span>
                <span v-else>🔄</span>
                {{ isUpdating ? '更新中...' : '更新数据' }}
              </button>

              <div class="header-controls">
                <div class="control-group">
                  <label>时间范围</label>
                  <select v-model="timeRange">
                    <option v-for="opt in timeRangeOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
                <div class="control-group">
                  <label>图表类型</label>
                  <select v-model="chartType">
                    <option v-for="opt in chartTypeOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- 日期范围滑块 -->
            <div class="date-slider-section">
              <div class="slider-header">
                <label>日期范围</label>
                <span class="date-range">
                  {{ filteredDates[0] || '' }} ~ {{ filteredDates[filteredDates.length - 1] || '' }}
                </span>
              </div>
              <div class="date-slider">
                <input
                  type="range"
                  v-model.number="dateSliderStart"
                  min="0"
                  max="100"
                  step="1"
                  class="slider-input"
                />
                <input
                  type="range"
                  v-model.number="dateSliderEnd"
                  min="0"
                  max="100"
                  step="1"
                  class="slider-input slider-end"
                />
                <div class="slider-track">
                  <div
                    class="slider-range"
                    :style="{
                      left: dateSliderStart + '%',
                      right: (100 - dateSliderEnd) + '%'
                    }"
                  ></div>
                </div>
              </div>
              <div class="slider-labels">
                <span>最早</span>
                <span>最晚</span>
              </div>
            </div>

            <!-- 基金详情信息 -->
            <div v-if="fundDetailData && selectedItem?.item_type === 'fund'" class="fund-detail-section">
              <div class="fund-detail-header">
                <div class="fund-name">
                  <h3>{{ fundDetailData.name || selectedItem.name }}</h3>
                  <span class="fund-code">{{ fundDetailData.code }}</span>
                </div>
                <div class="fund-meta">
                  <span v-if="fundDetailData.full_name" class="meta-item">{{ fundDetailData.full_name }}</span>
                  <span v-if="fundDetailData.fund_type" class="meta-item">{{ fundDetailData.fund_type }}</span>
                </div>
              </div>
              <div class="fund-stats">
                <div class="stat-item">
                  <span class="stat-label">单位净值</span>
                  <span class="stat-value">{{ fundDetailData.nav ? formatNumber(fundDetailData.nav, 4) : '--' }}</span>
                  <span class="stat-date">{{ fundDetailData.nav_date || '' }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">累计净值</span>
                  <span class="stat-value">{{ fundDetailData.acc_nav ? formatNumber(fundDetailData.acc_nav, 4) : '--' }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">估算净值</span>
                  <span class="stat-value" :class="fundDetailData.estimated_nav_change_percent >= 0 ? 'positive' : 'negative'">
                    {{ fundDetailData.estimated_nav ? formatNumber(fundDetailData.estimated_nav, 4) : '--' }}
                    <small v-if="fundDetailData.estimated_nav_change_percent">({{ formatPercent(fundDetailData.estimated_nav_change_percent) }})</small>
                  </span>
                </div>
                <div class="stat-item" v-if="fundDetailData.tracking_target">
                  <span class="stat-label">跟踪标的</span>
                  <span class="stat-value">{{ fundDetailData.tracking_target }}</span>
                </div>
              </div>
            </div>

            <!-- 分析摘要 - 历史业绩 -->
            <div v-if="summaryData" class="summary-cards">
              <div class="summary-card highlight">
                <div class="card-label">当前净值</div>
                <div class="card-value">{{ formatNumber(summaryData.current_price) }}</div>
              </div>
              <div class="summary-card">
                <div class="card-label">7日涨跌</div>
                <div class="card-value" :class="summaryData.summary_7d?.change_percent >= 0 ? 'positive' : 'negative'">
                  {{ summaryData.summary_7d ? formatPercent(summaryData.summary_7d.change_percent) : '--' }}
                </div>
              </div>
              <div class="summary-card">
                <div class="card-label">30日涨跌</div>
                <div class="card-value" :class="summaryData.summary_30d?.change_percent >= 0 ? 'positive' : 'negative'">
                  {{ summaryData.summary_30d ? formatPercent(summaryData.summary_30d.change_percent) : '--' }}
                </div>
              </div>
              <div class="summary-card">
                <div class="card-label">90日涨跌</div>
                <div class="card-value" :class="summaryData.summary_90d?.change_percent >= 0 ? 'positive' : 'negative'">
                  {{ summaryData.summary_90d ? formatPercent(summaryData.summary_90d.change_percent) : '--' }}
                </div>
              </div>
              <div class="summary-card">
                <div class="card-label">180日涨跌</div>
                <div class="card-value" :class="summaryData.summary_180d?.change_percent >= 0 ? 'positive' : 'negative'">
                  {{ summaryData.summary_180d ? formatPercent(summaryData.summary_180d.change_percent) : '--' }}
                </div>
              </div>
              <div class="summary-card">
                <div class="card-label">1年涨跌</div>
                <div class="card-value" :class="summaryData.summary_365d?.change_percent >= 0 ? 'positive' : 'negative'">
                  {{ summaryData.summary_365d ? formatPercent(summaryData.summary_365d.change_percent) : '--' }}
                </div>
              </div>
              <div class="summary-card">
                <div class="card-label">近90日波动</div>
                <div class="card-value">{{ summaryData.summary_90d ? formatPercent(summaryData.summary_90d.volatility) : '--' }}</div>
              </div>
              <div class="summary-card">
                <div class="card-label">90日最高</div>
                <div class="card-value">{{ summaryData.summary_90d ? formatNumber(summaryData.summary_90d.high) : '--' }}</div>
              </div>
              <div class="summary-card">
                <div class="card-label">90日最低</div>
                <div class="card-value">{{ summaryData.summary_90d ? formatNumber(summaryData.summary_90d.low) : '--' }}</div>
              </div>
            </div>

            <!-- 加载状态 -->
            <div v-if="isLoading" class="loading-state">
              <div class="spinner"></div>
              <span>加载数据中...</span>
            </div>

            <!-- 错误提示 -->
            <div v-if="error" class="error-state">
              {{ error }}
            </div>

            <!-- 主价格/净值图表 -->
            <div v-if="priceChartData" class="chart-section">
              <h3>{{ selectedItem?.item_type === 'fund' ? '净值走势' : '价格走势' }}</h3>
              <div class="chart-container">
                <Line :data="priceChartData" :options="lineChartOptions" />
              </div>
            </div>

            <!-- 日涨幅图表 -->
            <div v-if="dailyChangeChartData" class="chart-section">
              <h3>日涨幅</h3>
              <div class="chart-container small">
                <Bar :data="dailyChangeChartData" :options="lineChartOptions" />
              </div>
            </div>

            <!-- 历史业绩对比图 -->
            <div v-if="returnsChartData" class="chart-section">
              <h3>历史业绩</h3>
              <div class="chart-container small">
                <Bar :data="returnsChartData" :options="lineChartOptions" />
              </div>
            </div>

            <!-- 技术指标选择 -->
            <div class="indicators-selector">
              <label
                v-for="ind in indicatorOptions"
                :key="ind.value"
                :class="['indicator-btn', { active: selectedIndicators.includes(ind.value) }]"
                :style="{ '--indicator-color': ind.color }"
                @click="toggleIndicator(ind.value)"
              >
                {{ ind.label }}
              </label>
            </div>

            <!-- RSI 图表 -->
            <div v-if="rsiChartData" class="chart-section">
              <h3>RSI 相对强弱指标</h3>
              <div class="chart-container small">
                <Line :data="rsiChartData" :options="lineChartOptions" />
              </div>
            </div>

            <!-- MACD 图表 -->
            <div v-if="macdChartData" class="chart-section">
              <h3>MACD 指数平滑移动平均线</h3>
              <div class="chart-container small">
                <Bar :data="macdChartData" :options="lineChartOptions" />
              </div>
            </div>
          </template>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background: #f3f4f6;
}

:global(.dark) .analytics-page {
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
.analytics-container {
  display: flex;
  height: calc(100vh - 64px);
  gap: 1px;
  background: #e5e7eb;
}

:global(.dark) .analytics-container {
  background: #374151;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background: white;
  overflow-y: auto;
}

:global(.dark) .sidebar {
  background: #1f2937;
}

.list-section {
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .list-section {
  border-color: #374151;
}

.section-header {
  padding: 1rem;
  background: #f9fafb;
}

:global(.dark) .section-header {
  background: #1f2937;
}

.section-header h3 {
  margin: 0;
  font-size: 0.9rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:global(.dark) .section-header h3 {
  color: #9ca3af;
}

.item-list {
  padding: 0.5rem;
}

.item-entry {
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.25rem;
}

.item-entry:hover {
  background: #f3f4f6;
}

:global(.dark) .item-entry:hover {
  background: #374151;
}

.item-entry.active {
  background: #d1fae5;
}

:global(.dark) .item-entry.active {
  background: #064e3b;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-code {
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .item-code {
  color: #f3f4f6;
}

.item-name {
  font-size: 0.85rem;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:global(.dark) .item-name {
  color: #9ca3af;
}

.item-list-name,
.item-type {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.empty-tip {
  padding: 1rem;
  text-align: center;
  color: #9ca3af;
  font-size: 0.9rem;
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

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #6b7280;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-selection h3 {
  margin: 0 0 0.5rem;
  color: #374151;
}

:global(.dark) .no-selection h3 {
  color: #f3f4f6;
}

/* 头部信息 */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.symbol-info h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
}

:global(.dark) .symbol-info h2 {
  color: #f3f4f6;
}

.symbol-info p {
  margin: 0.25rem 0 0;
  color: #6b7280;
}

:global(.dark) .symbol-info p {
  color: #9ca3af;
}

.header-controls {
  display: flex;
  gap: 1rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.control-group label {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .control-group label {
  color: #9ca3af;
}

.control-group select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  color: #1f2937;
  cursor: pointer;
}

:global(.dark) .control-group select {
  background: #1f2937;
  border-color: #374151;
}

/* 数据库状态指示器 */
.db-status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.synced {
  background: #dcfce7;
  color: #166534;
}

:global(.dark) .status-badge.synced {
  background: #14532d;
  color: #86efac;
}

.status-badge.unsynced {
  background: #fef3c7;
  color: #92400e;
}

:global(.dark) .status-badge.unsynced {
  background: #78350f;
  color: #fcd34d;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.status-badge.synced .status-dot {
  background: #22c55e;
}

.status-badge.unsynced .status-dot {
  background: #f59e0b;
}

/* 更新按钮 */
.update-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #dbeafe;
  color: #2563eb;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.update-btn:hover:not(:disabled) {
  background: #bfdbfe;
}

.update-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

:global(.dark) .update-btn {
  background: #1e40af;
  color: #93c5fd;
}

:global(.dark) .update-btn:hover:not(:disabled) {
  background: #2563eb;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 摘要卡片 */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .summary-card {
  background: #1f2937;
}

.card-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

:global(.dark) .card-label {
  color: #9ca3af;
}

.card-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .card-value {
  color: #f3f4f6;
}

.card-value.positive {
  color: #dc2626;
}

.card-value.negative {
  color: #16a34a;
}

.summary-card.highlight {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.summary-card.highlight .card-label {
  color: rgba(255, 255, 255, 0.9);
}

.summary-card.highlight .card-value {
  color: white;
  font-size: 1.5rem;
}

/* 基金详情样式 */
.fund-detail-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .fund-detail-section {
  background: #1f2937;
}

.fund-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .fund-detail-header {
  border-color: #374151;
}

.fund-name {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.fund-name h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
}

:global(.dark) .fund-name h3 {
  color: #f3f4f6;
}

.fund-code {
  background: #e5e7eb;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-family: monospace;
}

:global(.dark) .fund-code {
  background: #374151;
  color: #9ca3af;
}

.fund-meta {
  display: flex;
  gap: 0.5rem;
}

.meta-item {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
}

:global(.dark) .meta-item {
  background: #374151;
  color: #9ca3af;
}

.fund-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .stat-label {
  color: #9ca3af;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .stat-value {
  color: #f3f4f6;
}

.stat-date {
  font-size: 0.7rem;
  color: #9ca3af;
}

.stat-value.positive {
  color: #dc2626;
}

.stat-value.negative {
  color: #16a34a;
}

.stat-value small {
  font-size: 0.75rem;
  font-weight: normal;
}

/* 加载状态 */
.loading-state {
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

.error-state {
  padding: 1rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

:global(.dark) .error-state {
  background: #7f1d1d;
  color: #f87171;
}

/* 图表区域 */
.chart-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .chart-section {
  background: #1f2937;
}

.chart-section h3 {
  margin: 0 0 1rem;
  color: #1f2937;
  font-size: 1rem;
}

:global(.dark) .chart-section h3 {
  color: #f3f4f6;
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-container.small {
  height: 200px;
}

/* 技术指标选择 */
.indicators-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.indicator-btn {
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  border: 2px solid #e5e7eb;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

:global(.dark) .indicator-btn {
  border-color: #374151;
  color: #9ca3af;
}

.indicator-btn:hover {
  border-color: var(--indicator-color);
  color: var(--indicator-color);
}

.indicator-btn.active {
  background: var(--indicator-color);
  border-color: var(--indicator-color);
  color: white;
}

/* 日期范围滑块 */
.date-slider-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .date-slider-section {
  background: #1f2937;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.slider-header label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .slider-header label {
  color: #f3f4f6;
}

.date-range {
  font-size: 0.85rem;
  color: #6b7280;
}

:global(.dark) .date-range {
  color: #9ca3af;
}

.date-slider {
  position: relative;
  height: 6px;
  margin: 1rem 0;
}

.slider-input {
  position: absolute;
  width: 100%;
  height: 6px;
  background: transparent;
  pointer-events: none;
  -webkit-appearance: none;
  appearance: none;
  z-index: 2;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: #10b981;
  border-radius: 50%;
  cursor: pointer;
  pointer-events: auto;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider-input::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: #10b981;
  border-radius: 50%;
  cursor: pointer;
  pointer-events: auto;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider-end::-webkit-slider-thumb {
  background: #3b82f6;
}

.slider-end::-moz-range-thumb {
  background: #3b82f6;
}

.slider-track {
  position: absolute;
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  top: 0;
}

:global(.dark) .slider-track {
  background: #374151;
}

.slider-range {
  position: absolute;
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
  border-radius: 3px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.5rem;
}

/* 按钮样式 */
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

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .page-header {
  background: #1f2937;
  border-color: #374151;
}

.logo {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

:global(.dark) .logo {
  color: #f3f4f6;
}

.header-left,
.header-right {
  min-width: 150px;
}

.page-main {
  height: calc(100vh - 64px);
  overflow: hidden;
}
</style>
