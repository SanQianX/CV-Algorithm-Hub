<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ModeToggle from '@/components/ui/ModeToggle.vue'

const router = useRouter()

// API基础URL
const API_BASE = ''

// 状态变量
const activeTab = ref('tables')
const isLoading = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// 数据库统计
const dbStats = ref<{
  tables: Record<string, number>
  total_records: number
  last_updated: string
} | null>(null)

// 表列表
const tables = ref<Array<{
  name: string
  record_count: number
  comment: string | null
}>>([])

// 当前选中的表
const selectedTable = ref<string | null>(null)
const tableInfo = ref<{
  table_name: string
  columns: Array<{
    name: string
    type: string
    nullable: boolean
    default: string
    primary_key: boolean
  }>
  primary_keys: string[]
  foreign_keys: Array<{
    name: string
    constrained_columns: string[]
    referred_table: string
    referred_columns: string[]
  }>
  indexes: Array<{
    name: string
    unique: boolean
    columns: string[]
  }>
  record_count: number
} | null>(null)

// 表记录
const records = ref<Array<Record<string, unknown>>([])
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 0
})

// CRUD表单
const showCrudModal = ref(false)
const crudMode = ref<'create' | 'edit'>('create')
const crudForm = reactive<Record<string, unknown>>({})
const editingRecordId = ref<string | ''>('')

// SQL查询
const sqlQuery = ref('')
const sqlResult = ref<{
  columns: string[]
  data: Array<Record<string, unknown>>
  row_count: number
} | null>(null)
const isExecutingSql = ref(false)

// 批量删除
const selectedIds = ref<string[]>([])
const showBulkDeleteConfirm = ref(false)

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

// 获取数据库统计
const fetchDbStats = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/db/stats`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      dbStats.value = await res.json()
    }
  } catch (e) {
    console.error('获取数据库统计失败:', e)
  }
}

// 获取表列表
const fetchTables = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/db/tables`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      tables.value = data.tables || []
    }
  } catch (e) {
    showMessage('获取表列表失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// 获取表信息
const fetchTableInfo = async (tableName: string) => {
  selectedTable.value = tableName
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/db/tables/${tableName}`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      tableInfo.value = await res.json()
    }
  } catch (e) {
    showMessage('获取表信息失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// 获取表记录
const fetchRecords = async (tableName: string, page = 1) => {
  isLoading.value = true
  try {
    const res = await fetch(
      `${API_BASE}/api/v1/db/tables/${tableName}/records?page=${page}&page_size=${pagination.value.page_size}`,
      { headers: getAuthHeaders() }
    )
    if (res.ok) {
      const data = await res.json()
      records.value = data.data || []
      pagination.value = {
        page: data.page,
        page_size: data.page_size,
        total: data.total,
        total_pages: data.total_pages
      }
    }
  } catch (e) {
    showMessage('获取记录失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// 选择表查看记录
const selectTable = async (tableName: string) => {
  activeTab.value = 'records'
  selectedIds.value = []
  await fetchTableInfo(tableName)
  await fetchRecords(tableName)
}

// 刷新当前表记录
const refreshRecords = async () => {
  if (selectedTable.value) {
    await fetchRecords(selectedTable.value, pagination.value.page)
  }
}

// 格式化值显示
const formatValue = (value: unknown): string => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

// 打开创建模态框
const openCreateModal = () => {
  crudMode.value = 'create'
  crudForm.value = {}
  editingRecordId.value = ''
  // 设置默认值
  if (tableInfo.value) {
    for (const col of tableInfo.value.columns) {
      if (col.default) {
        crudForm.value[col.name] = col.default.replace(/::.*/, '').replace(/'/, '')
      }
    }
  }
  showCrudModal.value = true
}

// 打开编辑模态框
const openEditModal = (record: Record<string, unknown>) => {
  crudMode.value = 'edit'
  editingRecordId.value = record.id as string
  // 复制记录数据（排除id和自动生成的字段）
  if (tableInfo.value) {
    for (const col of tableInfo.value.columns) {
      if (col.name !== 'id' && record[col.name] !== undefined) {
        crudForm.value[col.name] = record[col.name]
      }
    }
  }
  showCrudModal.value = true
}

// 关闭模态框
const closeCrudModal = () => {
  showCrudModal.value = false
  crudForm.value = {}
  editingRecordId.value = ''
}

// 保存记录（创建或更新）
const saveRecord = async () => {
  if (!selectedTable.value) return

  try {
    let res: Response
    if (crudMode.value === 'create') {
      res = await fetch(`${API_BASE}/api/v1/db/tables/${selectedTable.value}/records`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(crudForm.value)
      })
    } else {
      res = await fetch(`${API_BASE}/api/v1/db/tables/${selectedTable.value}/records/${editingRecordId.value}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(crudForm.value)
      })
    }

    if (res.ok) {
      showMessage(crudMode.value === 'create' ? '创建成功' : '更新成功', 'success')
      closeCrudModal()
      refreshRecords()
      fetchTables() // 刷新表列表
    } else {
      const err = await res.json()
      showMessage(err.detail || '操作失败', 'error')
    }
  } catch (e) {
    showMessage('操作失败', 'error')
  }
}

// 删除记录
const deleteRecord = async (id: string) => {
  if (!selectedTable.value || !confirm('确定要删除这条记录吗？')) return

  try {
    const res = await fetch(`${API_BASE}/api/v1/db/tables/${selectedTable.value}/records/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })

    if (res.ok) {
      showMessage('删除成功', 'success')
      refreshRecords()
      fetchTables()
    } else {
      showMessage('删除失败', 'error')
    }
  } catch (e) {
    showMessage('删除失败', 'error')
  }
}

// 批量删除
const bulkDelete = async () => {
  if (!selectedTable.value || selectedIds.value.length === 0) return

  try {
    const res = await fetch(`${API_BASE}/api/v1/db/tables/${selectedTable.value}/bulk-delete`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ ids: selectedIds.value })
    })

    if (res.ok) {
      const data = await res.json()
      showMessage(`成功删除 ${data.deleted_count} 条记录`, 'success')
      selectedIds.value = []
      showBulkDeleteConfirm.value = false
      refreshRecords()
      fetchTables()
    } else {
      showMessage('批量删除失败', 'error')
    }
  } catch (e) {
    showMessage('批量删除失败', 'error')
  }
}

// 执行SQL查询
const executeSql = async () => {
  if (!sqlQuery.value.trim()) return

  isExecutingSql.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/db/execute`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ query: sqlQuery.value })
    })

    if (res.ok) {
      sqlResult.value = await res.json()
    } else {
      const err = await res.json()
      showMessage(err.detail || '查询执行失败', 'error')
      sqlResult.value = null
    }
  } catch (e) {
    showMessage('查询执行失败', 'error')
    sqlResult.value = null
  } finally {
    isExecutingSql.value = false
  }
}

// 切换选择状态
const toggleSelect = (id: string) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) {
    selectedIds.value.push(id)
  } else {
    selectedIds.value.splice(idx, 1)
  }
}

// 全选/取消全选
const toggleSelectAll = () => {
  if (selectedIds.value.length === records.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = records.value.map(r => r.id as string)
  }
}

// 是否全部选中
const isAllSelected = computed(() => {
  return records.value.length > 0 && selectedIds.value.length === records.value.length
})

// 页面加载
onMounted(() => {
  fetchDbStats()
  fetchTables()
})
</script>

<template>
  <div class="db-manager-page">
    <header class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/dashboard')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          返回
        </button>
        <h1 class="logo">数据库管理</h1>
      </div>
      <div class="header-right">
        <ModeToggle />
      </div>
    </header>

    <main class="page-main">
      <div class="db-container">
        <!-- 消息提示 -->
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>

        <!-- 统计概览 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon blue">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ tables.length }}</span>
              <span class="stat-label">数据表</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon green">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ dbStats?.total_records || 0 }}</span>
              <span class="stat-label">总记录数</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon purple">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ dbStats?.last_updated?.split(' ')[1] || '-' }}</span>
              <span class="stat-label">最后更新</span>
            </div>
          </div>
        </div>

        <!-- 标签页 -->
        <div class="tabs">
          <button
            :class="['tab-btn', { active: activeTab === 'tables' }]"
            @click="activeTab = 'tables'"
          >
            数据表列表
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'records' }]"
            @click="activeTab = 'records'"
            :disabled="!selectedTable"
          >
            表数据 {{ selectedTable ? `(${selectedTable})` : '' }}
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'sql' }]"
            @click="activeTab = 'sql'"
          >
            SQL查询
          </button>
        </div>

        <!-- 数据表列表 -->
        <div v-if="activeTab === 'tables'" class="tab-content">
          <div class="table-list">
            <div
              v-for="table in tables"
              :key="table.name"
              class="table-item"
              @click="selectTable(table.name)"
            >
              <div class="table-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125m-3.75 0v7.5c0 .621.504 1.125 1.125 1.125m3.75-3.75C9.496 8.25 10 7.746 10 7.125m-3.75 0v3.75c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M9 12.75h3.75M9 12.75V5.625m0 7.5h3.75M9 12.75V5.625m0 7.5H6m0 7.5v7.5c0 .621.504 1.125 1.125 1.125m3.75-7.5h-3.75m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125m-3.75 0v7.5c0 .621.504 1.125 1.125 1.125m3.75-3.75C9.496 8.25 10 7.746 10 7.125m-3.75 0v3.75c0 .621.504 1.125 1.125 1.125m0 0h1.5" />
                </svg>
              </div>
              <div class="table-info">
                <span class="table-name">{{ table.name }}</span>
                <span class="table-comment">{{ table.comment || '无描述' }}</span>
              </div>
              <div class="table-count">
                <span class="count-value">{{ table.record_count }}</span>
                <span class="count-label">条记录</span>
              </div>
              <svg class="chevron" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </div>
          </div>

          <div v-if="tables.length === 0 && !isLoading" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125m-3.75 0v7.5c0 .621.504 1.125 1.125 1.125m3.75-3.75C9.496 8.25 10 7.746 10 7.125m-3.75 0v3.75c0 .621.504 1.125 1.125 1.125m0 0h1.5" />
            </svg>
            <p>暂无数据表</p>
          </div>
        </div>

        <!-- 表数据 -->
        <div v-if="activeTab === 'records'" class="tab-content">
          <div v-if="tableInfo" class="table-detail">
            <!-- 表信息头部 -->
            <div class="detail-header">
              <div class="detail-info">
                <h3>{{ tableInfo.table_name }}</h3>
                <span class="record-count">{{ tableInfo.record_count }} 条记录</span>
              </div>
              <div class="detail-actions">
                <button class="action-btn" @click="openCreateModal">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                  新增
                </button>
                <button
                  class="action-btn danger"
                  @click="showBulkDeleteConfirm = true"
                  :disabled="selectedIds.length === 0"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                  </svg>
                  删除选中 ({{ selectedIds.length }})
                </button>
              </div>
            </div>

            <!-- 表结构信息 -->
            <div class="schema-info">
              <div class="schema-section">
                <h4>列信息</h4>
                <div class="columns-list">
                  <span
                    v-for="col in tableInfo.columns"
                    :key="col.name"
                    :class="['column-tag', { primary: col.primary_key }]"
                  >
                    {{ col.name }}
                    <small>{{ col.type }}</small>
                  </span>
                </div>
              </div>
            </div>

            <!-- 数据表格 -->
            <div class="data-table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th class="checkbox-col">
                      <input
                        type="checkbox"
                        :checked="isAllSelected"
                        @change="toggleSelectAll"
                      />
                    </th>
                    <th v-for="col in tableInfo.columns" :key="col.name">
                      {{ col.name }}
                    </th>
                    <th class="action-col">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in records" :key="record.id as string">
                    <td class="checkbox-col">
                      <input
                        type="checkbox"
                        :checked="selectedIds.includes(record.id as string)"
                        @change="toggleSelect(record.id as string)"
                      />
                    </td>
                    <td v-for="col in tableInfo.columns" :key="col.name">
                      {{ formatValue(record[col.name]) }}
                    </td>
                    <td class="action-col">
                      <button class="icon-btn edit" @click="openEditModal(record)">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                        </svg>
                      </button>
                      <button class="icon-btn delete" @click="deleteRecord(record.id as string)">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>

              <div v-if="records.length === 0 && !isLoading" class="empty-table">
                暂无数据
              </div>
            </div>

            <!-- 分页 -->
            <div class="pagination" v-if="pagination.total_pages > 1">
              <button
                class="page-btn"
                :disabled="pagination.page === 1"
                @click="fetchRecords(selectedTable!, pagination.page - 1)"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ pagination.page }} / {{ pagination.total_pages }} 页
              </span>
              <button
                class="page-btn"
                :disabled="pagination.page === pagination.total_pages"
                @click="fetchRecords(selectedTable!, pagination.page + 1)"
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <!-- SQL查询 -->
        <div v-if="activeTab === 'sql'" class="tab-content">
          <div class="sql-section">
            <h3>SQL查询</h3>
            <p class="sql-hint">只支持 SELECT 查询，用于数据查询和分析</p>

            <textarea
              v-model="sqlQuery"
              placeholder="输入 SQL 查询语句，例如：SELECT * FROM users LIMIT 10"
              class="sql-input"
            ></textarea>

            <button class="execute-btn" @click="executeSql" :disabled="isExecutingSql">
              {{ isExecutingSql ? '执行中...' : '执行查询' }}
            </button>

            <!-- 查询结果 -->
            <div v-if="sqlResult" class="sql-result">
              <div class="result-header">
                <span>查询结果 ({{ sqlResult.row_count }} 行)</span>
              </div>
              <div class="result-table-container">
                <table class="result-table" v-if="sqlResult.data.length > 0">
                  <thead>
                    <tr>
                      <th v-for="col in sqlResult.columns" :key="col">{{ col }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in sqlResult.data" :key="idx">
                      <td v-for="col in sqlResult.columns" :key="col">
                        {{ formatValue(row[col]) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-result">查询结果为空</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- CRUD模态框 -->
    <div v-if="showCrudModal" class="modal-overlay" @click.self="closeCrudModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ crudMode === 'create' ? '新增记录' : '编辑记录' }}</h3>
          <button class="close-btn" @click="closeCrudModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveRecord">
            <div v-for="col in tableInfo?.columns" :key="col.name" class="form-group" v-show="col.name !== 'id' && col.name !== 'created_at' && col.name !== 'updated_at'">
              <label :for="col.name">
                {{ col.name }}
                <span v-if="col.primary_key" class="pk-badge">PK</span>
              </label>
              <input
                :id="col.name"
                v-model="crudForm[col.name]"
                :type="col.type.includes('INT') || col.type.includes('FLOAT') ? 'number' : 'text'"
                :placeholder="col.type"
              />
            </div>
            <div class="modal-actions">
              <button type="button" class="cancel-btn" @click="closeCrudModal">取消</button>
              <button type="submit" class="submit-btn">{{ crudMode === 'create' ? '创建' : '保存' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 批量删除确认 -->
    <div v-if="showBulkDeleteConfirm" class="modal-overlay" @click.self="showBulkDeleteConfirm = false">
      <div class="modal confirm-modal">
        <div class="modal-header">
          <h3>确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除选中的 {{ selectedIds.length }} 条记录吗？此操作不可恢复。</p>
          <div class="modal-actions">
            <button class="cancel-btn" @click="showBulkDeleteConfirm = false">取消</button>
            <button class="danger-btn" @click="bulkDelete">确认删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.db-manager-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

:global(.dark) .db-manager-page {
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

.db-container {
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

/* 标签页 */
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
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
  transition: all 0.2s;
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

:global(.dark) .tab-btn.active {
  color: #60a5fa;
  border-bottom-color: #60a5fa;
}

.tab-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 表列表 */
.table-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.table-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .table-item {
  background: #1f2937;
}

.table-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.table-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 0.5rem;
}

:global(.dark) .table-icon {
  background: #1e3a5f;
  color: #60a5fa;
}

.table-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.table-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.table-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .table-name {
  color: #f3f4f6;
}

.table-comment {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .table-comment {
  color: #9ca3af;
}

.table-count {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.count-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #3b82f6;
}

:global(.dark) .count-value {
  color: #60a5fa;
}

.count-label {
  font-size: 0.75rem;
  color: #6b7280;
}

:global(.dark) .count-label {
  color: #9ca3af;
}

.chevron {
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
}

.empty-state {
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

/* 表详情 */
.table-detail {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:global(.dark) .table-detail {
  background: #1f2937;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.detail-info h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

:global(.dark) .detail-info h3 {
  color: #f3f4f6;
}

.record-count {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .record-count {
  color: #9ca3af;
}

.detail-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
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

.action-btn:hover:not(:disabled) {
  background: #2563eb;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.danger {
  background: #ef4444;
}

.action-btn.danger:hover:not(:disabled) {
  background: #dc2626;
}

.action-btn svg {
  width: 1rem;
  height: 1rem;
}

/* 表结构信息 */
.schema-info {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

:global(.dark) .schema-info {
  background: #374151;
}

.schema-section h4 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .schema-section h4 {
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

.column-tag.primary {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

:global(.dark) .column-tag.primary {
  background: #78350f;
  border-color: #f59e0b;
  color: #fef3c7;
}

.column-tag small {
  color: #9ca3af;
  font-size: 0.7rem;
}

/* 数据表格 */
.data-table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
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

.checkbox-col {
  width: 40px;
  text-align: center;
}

.action-col {
  width: 100px;
  text-align: center;
}

.icon-btn {
  width: 2rem;
  height: 2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn svg {
  width: 1rem;
  height: 1rem;
}

.icon-btn.edit {
  background: #eff6ff;
  color: #3b82f6;
}

.icon-btn.edit:hover {
  background: #dbeafe;
}

.icon-btn.delete {
  background: #fef2f2;
  color: #ef4444;
  margin-left: 0.25rem;
}

.icon-btn.delete:hover {
  background: #fee2e2;
}

.empty-table {
  padding: 3rem;
  text-align: center;
  color: #9ca3af;
}

/* 分页 */
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
  transition: all 0.2s;
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

/* SQL查询 */
.sql-section h3 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  color: #1f2937;
}

:global(.dark) .sql-section h3 {
  color: #f3f4f6;
}

.sql-hint {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .sql-hint {
  color: #9ca3af;
}

.sql-input {
  width: 100%;
  height: 120px;
  padding: 1rem;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.875rem;
  color: #1f2937;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  resize: vertical;
}

:global(.dark) .sql-input {
  color: #f3f4f6;
  background: #1f2937;
  border-color: #4b5563;
}

.execute-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.95rem;
  color: white;
  background: #3b82f6;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.execute-btn:hover:not(:disabled) {
  background: #2563eb;
}

.execute-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sql-result {
  margin-top: 1.5rem;
}

.result-header {
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: #374151;
}

:global(.dark) .result-header {
  color: #f3f4f6;
}

.result-table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

:global(.dark) .result-table-container {
  border-color: #374151;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.result-table th,
.result-table td {
  padding: 0.5rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

:global(.dark) .result-table th,
:global(.dark) .result-table td {
  border-color: #374151;
}

.result-table th {
  background: #f9fafb;
  font-weight: 600;
}

:global(.dark) .result-table th {
  background: #374151;
}

.empty-result {
  padding: 2rem;
  text-align: center;
  color: #9ca3af;
}

/* 模态框 */
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
  z-index: 1000;
}

.modal {
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

:global(.dark) .modal {
  background: #1f2937;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

:global(.dark) .modal-header {
  border-color: #374151;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: #1f2937;
}

:global(.dark) .modal-header h3 {
  color: #f3f4f6;
}

.close-btn {
  font-size: 1.5rem;
  color: #9ca3af;
  background: transparent;
  border: none;
  cursor: pointer;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

:global(.dark) .form-group label {
  color: #f3f4f6;
}

.pk-badge {
  padding: 0.125rem 0.375rem;
  font-size: 0.7rem;
  font-weight: 600;
  background: #fef3c7;
  color: #92400e;
  border-radius: 0.25rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  color: #1f2937;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

:global(.dark) .modal-actions {
  border-color: #374151;
}

.cancel-btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.95rem;
  color: #374151;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
}

:global(.dark) .cancel-btn {
  color: #f3f4f6;
  background: #1f2937;
  border-color: #4b5563;
}

.submit-btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.95rem;
  color: white;
  background: #3b82f6;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

.submit-btn:hover {
  background: #2563eb;
}

.danger-btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.95rem;
  color: white;
  background: #ef4444;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

.danger-btn:hover {
  background: #dc2626;
}

.confirm-modal {
  max-width: 400px;
}

.confirm-modal .modal-body p {
  margin: 0;
  color: #374151;
}

:global(.dark) .confirm-modal .modal-body p {
  color: #f3f4f6;
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

  .tabs {
    overflow-x: auto;
  }

  .detail-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .detail-actions {
    width: 100%;
  }

  .action-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
