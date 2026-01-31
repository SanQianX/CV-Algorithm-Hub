<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// API base URL
const API_BASE = ''

// State
const activeTab = ref('explorer')
const isLoading = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// Directory tree
const treeData = ref<any[]>([])
const expandedNodes = ref<Set<string>>(new Set())

// Directory listing
const currentPath = ref('K:/data/databases')
const directoryItems = ref<any[]>([])
const selectedDb = ref<string | null>(null)
const selectedTable = ref<string | null>(null)

// Database info
const dbInfo = ref<any>(null)
const tablePreview = ref<any>(null)
const financeSummary = ref<any>(null)

// Table data
const tableData = ref<any[]>([])
const tableColumns = ref<string[]>([])
const tablePagination = reactive({
  page: 1,
  pageSize: 50,
  total: 0,
  totalPages: 0
})

// Finance records
const financeRecords = ref<any[]>([])
const financePagination = reactive({
  page: 1,
  pageSize: 50,
  total: 0
})

// Search
const searchKeyword = ref('')
const searchResults = ref<any[]>([])

// Stats
const stats = ref<any>(null)

// Filters
const filters = reactive({
  recordType: 'fund',
  code: '',
  startDate: '',
  endDate: ''
})

// Get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

// Show message
const showMessage = (msg: string, type: 'success' | 'error') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

// Fetch directory tree
const fetchTree = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/explorer/tree?depth=3`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      treeData.value = data.tree || []
    }
  } catch (e) {
    console.error('获取目录树失败:', e)
  } finally {
    isLoading.value = false
  }
}

// Fetch directory listing
const fetchDirectory = async (path: string) => {
  isLoading.value = true
  currentPath.value = path
  try {
    const res = await fetch(`${API_BASE}/api/v1/explorer/directories?path=${encodeURIComponent(path)}`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      directoryItems.value = data || []
    }
  } catch (e) {
    showMessage('获取目录列表失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// Fetch database info
const fetchDbInfo = async (dbName: string) => {
  isLoading.value = true
  selectedDb.value = dbName
  selectedTable.value = null

  try {
    const res = await fetch(`${API_BASE}/api/v1/explorer/database/${dbName}`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      dbInfo.value = await res.json()
    }
  } catch (e) {
    showMessage('获取数据库信息失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// Fetch table preview
const fetchTablePreview = async (dbName: string, tableName: string) => {
  isLoading.value = true
  selectedTable.value = tableName

  try {
    const res = await fetch(`${API_BASE}/api/v1/explorer/database/${dbName}/tables/${tableName}/preview`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      tablePreview.value = await res.json()
    }
  } catch (e) {
    showMessage('获取表预览失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// Fetch table data
const fetchTableData = async (dbName: string, tableName: string, page = 1) => {
  isLoading.value = true
  tablePagination.page = page

  try {
    const res = await fetch(
      `${API_BASE}/api/v1/explorer/database/${dbName}/tables/${tableName}/data?page=${page}&page_size=${tablePagination.pageSize}`,
      { headers: getAuthHeaders() }
    )
    if (res.ok) {
      const data = await res.json()
      tableData.value = data.data || []
      tableColumns.value = data.columns || []
      tablePagination.total = data.total
      tablePagination.totalPages = data.total_pages
    }
  } catch (e) {
    showMessage('获取表数据失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// Fetch finance summary
const fetchFinanceSummary = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/explorer/database/finance/finance-summary`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      financeSummary.value = await res.json()
    }
  } catch (e) {
    console.error('获取金融摘要失败:', e)
  }
}

// Fetch finance records
const fetchFinanceRecords = async (page = 1) => {
  isLoading.value = true
  financePagination.page = page

  let url = `${API_BASE}/api/v1/explorer/database/finance/finance-records?page=${page}&page_size=${financePagination.pageSize}&record_type=${filters.recordType}`

  if (filters.code) url += `&code=${filters.code}`
  if (filters.startDate) url += `&start_date=${filters.startDate}`
  if (filters.endDate) url += `&end_date=${filters.endDate}`

  try {
    const res = await fetch(url, { headers: getAuthHeaders() })
    if (res.ok) {
      const data = await res.json()
      financeRecords.value = data.data || []
      financePagination.total = data.total
    }
  } catch (e) {
    showMessage('获取金融记录失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// Search
const search = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const res = await fetch(`${API_BASE}/api/v1/explorer/search?keyword=${encodeURIComponent(searchKeyword.value)}`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      searchResults.value = data.results || []
    }
  } catch (e) {
    showMessage('搜索失败', 'error')
  }
}

// Fetch stats
const fetchStats = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/explorer/stats`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      stats.value = await res.json()
    }
  } catch (e) {
    console.error('获取统计失败:', e)
  }
}

// Format file size
const formatSize = (bytes: number | null | undefined) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}

// Format date
const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

// Select database
const selectDatabase = (item: any) => {
  if (item.type === 'file' && item.name.endsWith('.db')) {
    const dbName = item.path.split('/').pop()?.replace('.db', '')
    if (dbName) {
      activeTab.value = 'database'
      fetchDbInfo(dbName)
    }
  }
}

// Select table
const selectTable = (tableName: string) => {
  if (selectedDb.value) {
    activeTab.value = 'table'
    fetchTablePreview(selectedDb.value, tableName)
    fetchTableData(selectedDb.value, tableName)
  }
}

// Navigate to table page
const goToTablePage = (page: number) => {
  if (selectedDb.value && selectedTable.value) {
    fetchTableData(selectedDb.value, selectedTable.value, page)
  }
}

// Navigate to finance page
const goToFinancePage = (page: number) => {
  fetchFinanceRecords(page)
}

// Load more finance records
const loadMoreFinance = () => {
  if (financePagination.page < Math.ceil(financePagination.total / financePagination.pageSize)) {
    goToFinancePage(financePagination.page + 1)
  }
}

// Reset filters
const resetFilters = () => {
  filters.recordType = 'fund'
  filters.code = ''
  filters.startDate = ''
  filters.endDate = ''
  fetchFinanceRecords(1)
}

// Initialize
onMounted(() => {
  fetchDirectory('K:/data/databases')
  fetchStats()
  fetchFinanceSummary()
})
</script>

<template>
  <div class="data-explorer-page">
    <header class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/dashboard')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          返回
        </button>
        <h1 class="logo">数据目录浏览器</h1>
      </div>
      <div class="header-right">
        <!-- Search -->
        <div class="search-box">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索表名、列名..."
            @keyup.enter="search"
          />
          <button v-if="searchKeyword" class="search-clear" @click="searchKeyword = ''; searchResults = []">&times;</button>
        </div>
      </div>
    </header>

    <main class="page-main">
      <div class="explorer-container">
        <!-- Message -->
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>

        <!-- Stats Cards -->
        <div v-if="stats" class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon blue">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 8.25h15m-15 4.5h15m-15 4.5h15M5.25 9v3.75m0 0h3.75m-3.75 0V9m0 3.75h3.75M9 11.25v1.5M12 9v3.75m3-6v6" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_databases || stats.databases?.length || 0 }}</span>
              <span class="stat-label">数据库</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon green">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_tables || 0 }}</span>
              <span class="stat-label">数据表</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon purple">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0z" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_records?.toLocaleString() || 0 }}</span>
              <span class="stat-label">总记录数</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon orange">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ formatSize(stats.total_size) }}</span>
              <span class="stat-label">总大小</span>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
          <button :class="['tab-btn', { active: activeTab === 'explorer' }]" @click="activeTab = 'explorer'">
            文件浏览器
          </button>
          <button :class="['tab-btn', { active: activeTab === 'database' }]" @click="activeTab = 'database'" :disabled="!selectedDb">
            数据库详情 {{ selectedDb ? `(${selectedDb})` : '' }}
          </button>
          <button :class="['tab-btn', { active: activeTab === 'table' }]" @click="activeTab = 'table'" :disabled="!selectedTable">
            表数据 {{ selectedTable ? `(${selectedTable})` : '' }}
          </button>
          <button :class="['tab-btn', { active: activeTab === 'finance' }]" @click="activeTab = 'finance'">
            金融数据
          </button>
          <button :class="['tab-btn', { active: activeTab === 'search' }]" @click="activeTab = 'search'">
            搜索结果 ({{ searchResults.length }})
          </button>
        </div>

        <!-- File Explorer Tab -->
        <div v-if="activeTab === 'explorer'" class="tab-content">
          <div class="path-bar">
            <span class="path-label">当前路径:</span>
            <span class="path-value">{{ currentPath }}</span>
          </div>

          <div class="directory-grid">
            <div
              v-for="item in directoryItems"
              :key="item.path"
              :class="['dir-item', { 'is-file': item.type === 'file' }]"
              @click="selectDatabase(item)"
            >
              <div class="item-icon">
                <svg v-if="item.type === 'directory'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
                </svg>
              </div>
              <div class="item-info">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-meta">
                  <template v-if="item.size">{{ formatSize(item.size) }}</template>
                  <template v-else>{{ item.children_count || 0 }} 项</template>
                </span>
              </div>
            </div>

            <div v-if="directoryItems.length === 0 && !isLoading" class="empty-state">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 012.012 1.244l.256.512a2.25 2.25 0 002.013 1.244h3.218a2.25 2.25 0 002.013-1.244l.256-.512a2.25 2.25 0 012.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 00-2.15-1.588H6.911a2.25 2.25 0 00-2.15 1.588L2.35 13.177a2.25 2.25 0 00-.1.661z" />
              </svg>
              <p>目录为空</p>
            </div>
          </div>
        </div>

        <!-- Database Tab -->
        <div v-if="activeTab === 'database' && dbInfo" class="tab-content">
          <div class="db-header">
            <div class="db-info">
              <h2>{{ dbInfo.name }}</h2>
              <div class="db-meta">
                <span>{{ formatSize(dbInfo.size) }}</span>
                <span>{{ dbInfo.table_count }} 个表</span>
                <span>{{ dbInfo.db_type.toUpperCase() }}</span>
              </div>
            </div>
          </div>

          <div class="tables-grid">
            <div
              v-for="table in dbInfo.tables"
              :key="table.name"
              class="table-card"
              @click="selectTable(table.name)"
            >
              <div class="table-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125m-3.75 0v7.5c0 .621.504 1.125 1.125 1.125m3.75-3.75C9.496 8.25 10 7.746 10 7.125m-3.75 0v3.75c0 .621.504 1.125 1.125 1.125m0 0h1.5" />
                </svg>
              </div>
              <div class="table-info">
                <span class="table-name">{{ table.name }}</span>
                <span class="table-count">{{ table.row_count.toLocaleString() }} 条记录</span>
              </div>
              <div class="table-columns">
                <span v-for="col in table.columns.slice(0, 3)" :key="col.name" class="col-tag">
                  {{ col.name }}
                </span>
                <span v-if="table.columns.length > 3" class="col-more">
                  +{{ table.columns.length - 3 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Table Data Tab -->
        <div v-if="activeTab === 'table' && tablePreview" class="tab-content">
          <div class="table-header">
            <div class="table-info">
              <h3>{{ selectedTable }}</h3>
              <span class="record-count">{{ tablePagination.total.toLocaleString() }} 条记录</span>
              <span v-if="tablePreview.date_range" class="date-range">
                {{ formatDate(tablePreview.date_range.start) }} - {{ formatDate(tablePreview.date_range.end) }}
              </span>
            </div>
          </div>

          <!-- Columns -->
          <div class="columns-section">
            <h4>列信息</h4>
            <div class="columns-list">
              <span v-for="col in tablePreview.columns" :key="col.name" class="column-tag">
                {{ col.name }}
                <small>{{ col.type }}</small>
              </span>
            </div>
          </div>

          <!-- Data Table -->
          <div class="data-table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="col in tableColumns" :key="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in tableData" :key="idx">
                  <td v-for="col in tableColumns" :key="col">
                    {{ row[col] !== null && row[col] !== undefined ? row[col] : '-' }}
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="tableData.length === 0 && !isLoading" class="empty-table">
              暂无数据
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="tablePagination.totalPages > 1" class="pagination">
            <button
              class="page-btn"
              :disabled="tablePagination.page === 1"
              @click="goToTablePage(tablePagination.page - 1)"
            >
              上一页
            </button>
            <span class="page-info">
              第 {{ tablePagination.page }} / {{ tablePagination.totalPages }} 页
            </span>
            <button
              class="page-btn"
              :disabled="tablePagination.page === tablePagination.totalPages"
              @click="goToTablePage(tablePagination.page + 1)"
            >
              下一页
            </button>
          </div>
        </div>

        <!-- Finance Data Tab -->
        <div v-if="activeTab === 'finance'" class="tab-content">
          <!-- Finance Summary -->
          <div v-if="financeSummary" class="finance-summary">
            <div class="summary-card">
              <h4>金融数据概览</h4>
              <div class="summary-stats">
                <div class="stat">
                  <span class="label">总记录数</span>
                  <span class="value">{{ financeSummary.total_records?.toLocaleString() || 0 }}</span>
                </div>
                <div class="stat">
                  <span class="label">基金详情</span>
                  <span class="value">{{ financeSummary.fund_details_count || 0 }}</span>
                </div>
                <div class="stat">
                  <span class="label">基金代码</span>
                  <span class="value">{{ financeSummary.fund_codes?.length || 0 }}</span>
                </div>
                <div class="stat">
                  <span class="label">股票代码</span>
                  <span class="value">{{ financeSummary.stock_codes?.length || 0 }}</span>
                </div>
              </div>
              <div v-if="financeSummary.date_range" class="date-range">
                数据时间范围: {{ formatDate(financeSummary.date_range.start) }} - {{ formatDate(financeSummary.date_range.end) }}
              </div>
            </div>
          </div>

          <!-- Filters -->
          <div class="filters-section">
            <h4>数据筛选</h4>
            <div class="filters">
              <div class="filter-group">
                <label>数据类型</label>
                <select v-model="filters.recordType">
                  <option value="fund">基金</option>
                  <option value="stock">股票</option>
                </select>
              </div>
              <div class="filter-group">
                <label>代码</label>
                <input v-model="filters.code" type="text" placeholder="基金/股票代码" />
              </div>
              <div class="filter-group">
                <label>开始日期</label>
                <input v-model="filters.startDate" type="date" />
              </div>
              <div class="filter-group">
                <label>结束日期</label>
                <input v-model="filters.endDate" type="date" />
              </div>
              <div class="filter-actions">
                <button class="btn-primary" @click="fetchFinanceRecords(1)">查询</button>
                <button class="btn-secondary" @click="resetFilters">重置</button>
              </div>
            </div>
          </div>

          <!-- Finance Data Table -->
          <div class="finance-table">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>代码</th>
                  <th>日期</th>
                  <template v-if="filters.recordType === 'fund'">
                    <th>净值</th>
                    <th>涨跌</th>
                    <th>涨跌幅</th>
                  </template>
                  <template v-else>
                    <th>开盘</th>
                    <th>最高</th>
                    <th>最低</th>
                    <th>收盘</th>
                    <th>成交量</th>
                  </template>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in financeRecords" :key="row.id">
                  <td class="id-cell">{{ row.id.slice(0, 8) }}...</td>
                  <td class="code-cell">{{ row.code }}</td>
                  <td>{{ row.date }}</td>
                  <template v-if="filters.recordType === 'fund'">
                    <td>{{ row.nav?.toFixed(4) || '-' }}</td>
                    <td :class="row.nav_change >= 0 ? 'positive' : 'negative'">
                      {{ row.nav_change?.toFixed(4) || '-' }}
                    </td>
                    <td :class="row.nav_change_percent >= 0 ? 'positive' : 'negative'">
                      {{ row.nav_change_percent?.toFixed(2) || '-' }}%
                    </td>
                  </template>
                  <template v-else>
                    <td>{{ row.open?.toFixed(2) || '-' }}</td>
                    <td>{{ row.high?.toFixed(2) || '-' }}</td>
                    <td>{{ row.low?.toFixed(2) || '-' }}</td>
                    <td>{{ row.close?.toFixed(2) || '-' }}</td>
                    <td>{{ row.volume?.toLocaleString() || '-' }}</td>
                  </template>
                </tr>
              </tbody>
            </table>

            <div v-if="financeRecords.length === 0 && !isLoading" class="empty-table">
              暂无数据
            </div>
          </div>

          <!-- Load More -->
          <div v-if="financePagination.total > financeRecords.length" class="load-more">
            <button @click="loadMoreFinance" :disabled="isLoading">
              {{ isLoading ? '加载中...' : '加载更多' }}
            </button>
          </div>
        </div>

        <!-- Search Results Tab -->
        <div v-if="activeTab === 'search'" class="tab-content">
          <div v-if="searchResults.length > 0" class="search-results">
            <div v-for="(result, idx) in searchResults" :key="idx" class="search-result-item">
              <span :class="['result-type', result.type]">{{ result.type }}</span>
              <div class="result-info">
                <template v-if="result.type === 'table'">
                  <span class="result-db">{{ result.database }}</span>
                  <span class="result-sep">/</span>
                  <span class="result-name">{{ result.table }}</span>
                  <span class="result-meta">{{ result.row_count?.toLocaleString() }} 条记录</span>
                </template>
                <template v-else>
                  <span class="result-db">{{ result.database }}</span>
                  <span class="result-sep">/</span>
                  <span class="result-name">{{ result.table }}</span>
                  <span class="result-sep">/</span>
                  <span class="result-column">{{ result.column }}</span>
                  <span class="result-meta">{{ result.column_type }}</span>
                </template>
              </div>
            </div>
          </div>
          <div v-else-if="searchKeyword && !isLoading" class="no-results">
            <p>未找到相关结果</p>
          </div>
          <div v-else class="search-hint">
            <p>输入关键词搜索表名和列名</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.data-explorer-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

:global(.dark) .data-explorer-page {
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

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
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
  width: 200px;
  color: #1f2937;
}

:global(.dark) .search-box input {
  color: #f3f4f6;
}

.search-clear {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #9ca3af;
  cursor: pointer;
}

.page-main {
  flex: 1;
  padding: 2rem;
}

.explorer-container {
  max-width: 1400px;
  margin: 0 auto;
}

.message {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.message.success {
  background: #ecfdf5;
  color: #059669;
}

.message.error {
  background: #fef2f2;
  color: #dc2626;
}

/* Stats Cards */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .stat-card {
  background: #1f2937;
}

.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
}

.stat-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.stat-icon.blue {
  background: #eff6ff;
  color: #3b82f6;
}

.stat-icon.green {
  background: #ecfdf5;
  color: #10b981;
}

.stat-icon.purple {
  background: #f5f3ff;
  color: #8b5cf6;
}

.stat-icon.orange {
  background: #fff7ed;
  color: #f97316;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
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

/* Tabs */
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  overflow-x: auto;
}

:global(.dark) .tabs {
  border-color: #374151;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  font-size: 0.95rem;
  color: #6b7280;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
}

:global(.dark) .tab-btn {
  color: #9ca3af;
}

.tab-btn:hover:not(:disabled) {
  color: #374151;
}

:global(.dark) .tab-btn:hover:not(:disabled) {
  color: #f3f4f6;
}

.tab-btn.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* File Explorer */
.path-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

:global(.dark) .path-bar {
  background: #374151;
}

.path-label {
  color: #6b7280;
  font-size: 0.875rem;
}

:global(.dark) .path-label {
  color: #9ca3af;
}

.path-value {
  color: #1f2937;
  font-family: monospace;
}

:global(.dark) .path-value {
  color: #f3f4f6;
}

.directory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.dir-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .dir-item {
  background: #1f2937;
}

.dir-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dir-item.is-file {
  cursor: pointer;
}

.item-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 0.5rem;
}

:global(.dark) .item-icon {
  background: #1e3a5f;
  color: #60a5fa;
}

.item-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  display: block;
  font-weight: 500;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:global(.dark) .item-name {
  color: #f3f4f6;
}

.item-meta {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .item-meta {
  color: #9ca3af;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #9ca3af;
}

.empty-state svg {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
}

/* Database */
.db-header {
  margin-bottom: 1.5rem;
}

.db-info h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  color: #1f2937;
}

:global(.dark) .db-info h2 {
  color: #f3f4f6;
}

.db-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .db-meta {
  color: #9ca3af;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.table-card {
  padding: 1rem;
  background: white;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .table-card {
  background: #1f2937;
}

.table-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.table-icon {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
}

:global(.dark) .table-icon {
  background: #1e3a5f;
  color: #60a5fa;
}

.table-icon svg {
  width: 1rem;
  height: 1rem;
}

.table-info {
  margin-bottom: 0.75rem;
}

.table-name {
  display: block;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .table-name {
  color: #f3f4f6;
}

.table-count {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .table-count {
  color: #9ca3af;
}

.table-columns {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.col-tag {
  padding: 0.125rem 0.375rem;
  font-size: 0.7rem;
  background: #f3f4f6;
  color: #374151;
  border-radius: 0.25rem;
}

:global(.dark) .col-tag {
  background: #374151;
  color: #9ca3af;
}

.col-more {
  font-size: 0.7rem;
  color: #9ca3af;
}

/* Table Data */
.table-header {
  margin-bottom: 1.5rem;
}

.table-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  color: #1f2937;
}

:global(.dark) .table-info h3 {
  color: #f3f4f6;
}

.record-count {
  font-size: 0.875rem;
  color: #6b7280;
  margin-right: 1rem;
}

:global(.dark) .record-count {
  color: #9ca3af;
}

.date-range {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .date-range {
  color: #9ca3af;
}

.columns-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

:global(.dark) .columns-section {
  background: #374151;
}

.columns-section h4 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .columns-section h4 {
  color: #9ca3af;
}

.columns-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.column-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  color: #374151;
}

:global(.dark) .column-tag {
  background: #1f2937;
  border-color: #4b5563;
  color: #f3f4f6;
}

.column-tag small {
  color: #9ca3af;
  font-size: 0.65rem;
}

/* Data Table */
.data-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .data-table-container {
  background: #1f2937;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

:global(.dark) .data-table th,
:global(.dark) .data-table td {
  border-color: #374151;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
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

.empty-table {
  padding: 3rem;
  text-align: center;
  color: #9ca3af;
}

.positive {
  color: #10b981 !important;
}

.negative {
  color: #ef4444 !important;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

:global(.dark) .pagination {
  border-color: #374151;
}

.page-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
}

:global(.dark) .page-btn {
  color: #f3f4f6;
  background: #1f2937;
  border-color: #4b5563;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
}

:global(.dark) .page-btn:hover:not(:disabled) {
  background: #374151;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .page-info {
  color: #9ca3af;
}

/* Finance Section */
.finance-summary {
  margin-bottom: 1.5rem;
}

.summary-card {
  padding: 1.5rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .summary-card {
  background: #1f2937;
}

.summary-card h4 {
  margin: 0 0 1rem;
  color: #1f2937;
}

:global(.dark) .summary-card h4 {
  color: #f3f4f6;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.stat .label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

:global(.dark) .stat .label {
  color: #9ca3af;
}

.stat .value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .stat .value {
  color: #f3f4f6;
}

.filters-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

:global(.dark) .filters-section {
  background: #374151;
}

.filters-section h4 {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .filters-section h4 {
  color: #9ca3af;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group label {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .filter-group label {
  color: #9ca3af;
}

.filter-group input,
.filter-group select {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #1f2937;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
}

:global(.dark) .filter-group input,
:global(.dark) .filter-group select {
  color: #f3f4f6;
  background: #1f2937;
  border-color: #4b5563;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  border-radius: 0.375rem;
  cursor: pointer;
}

.btn-primary {
  color: white;
  background: #3b82f6;
  border: none;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  color: #374151;
  background: white;
  border: 1px solid #d1d5db;
}

:global(.dark) .btn-secondary {
  color: #f3f4f6;
  background: #1f2937;
  border-color: #4b5563;
}

.finance-table {
  background: white;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .finance-table {
  background: #1f2937;
}

.id-cell {
  font-family: monospace;
  font-size: 0.75rem;
  color: #9ca3af;
}

.code-cell {
  font-weight: 500;
  color: #3b82f6;
}

.load-more {
  margin-top: 1rem;
  text-align: center;
}

.load-more button {
  padding: 0.75rem 2rem;
  font-size: 0.875rem;
  color: white;
  background: #3b82f6;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

.load-more button:hover:not(:disabled) {
  background: #2563eb;
}

.load-more button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Search Results */
.search-results {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 0.5rem;
}

:global(.dark) .search-result-item {
  background: #1f2937;
}

.result-type {
  padding: 0.25rem 0.5rem;
  font-size: 0.7rem;
  font-weight: 500;
  border-radius: 0.25rem;
  text-transform: uppercase;
}

.result-type.table {
  background: #eff6ff;
  color: #3b82f6;
}

.result-type.column {
  background: #ecfdf5;
  color: #10b981;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #374151;
}

:global(.dark) .result-info {
  color: #f3f4f6;
}

.result-sep {
  color: #9ca3af;
}

.result-meta {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .result-meta {
  color: #9ca3af;
}

.no-results,
.search-hint {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
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

  .filters {
    flex-direction: column;
  }

  .filter-actions {
    width: 100%;
  }

  .filter-actions button {
    flex: 1;
  }
}
</style>
