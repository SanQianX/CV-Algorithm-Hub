import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

interface MonitorItem {
  id: string
  code: string
  name: string
  item_type: string
  market?: string
  sync_frequency: string
  sync_history: boolean
  history_range: string
  indicators: string[]
  alerts: any[]
  tags: string[]
  extra_data?: any
  created_at: string
  updated_at: string
}

interface MonitorList {
  id: string
  name: string
  description?: string
  list_type: string
  created_at: string
  updated_at: string
  items: MonitorItem[]
}

export const useMonitorStore = defineStore('monitor', () => {
  const lists = ref<MonitorList[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const token = ref<string | null>(localStorage.getItem('token'))

  // 获取认证头
  const getAuthHeaders = () => ({
    Authorization: `Bearer ${token.value}`
  })

  // 加载监控列表
  const fetchLists = async (listType?: string) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null

    try {
      const params = listType ? { list_type: listType } : {}
      const response = await axios.get(`${API_BASE_URL}/api/v1/monitor/lists`, {
        headers: getAuthHeaders(),
        params
      })
      lists.value = response.data
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '加载失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 创建监控列表
  const createList = async (name: string, description?: string, listType = 'stock') => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/monitor/lists`,
        { name, description, list_type: listType },
        { headers: getAuthHeaders() }
      )
      lists.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 更新监控列表
  const updateList = async (listId: string, name: string, description?: string) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null

    try {
      const response = await axios.put(
        `${API_BASE_URL}/api/v1/monitor/lists/${listId}`,
        { name, description },
        { headers: getAuthHeaders() }
      )

      const index = lists.value.findIndex(l => l.id === listId)
      if (index !== -1) {
        lists.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 删除监控列表
  const deleteList = async (listId: string) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null

    try {
      await axios.delete(`${API_BASE_URL}/api/v1/monitor/lists/${listId}`, {
        headers: getAuthHeaders()
      })
      lists.value = lists.value.filter(l => l.id !== listId)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 添加标的到列表
  const addItem = async (
    listId: string,
    item: {
      code: string
      name: string
      item_type: string
      market?: string
      sync_frequency?: string
      sync_history?: boolean
      history_range?: string
      indicators?: string[]
      alerts?: any[]
      tags?: string[]
      extra_data?: any
    }
  ) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/monitor/lists/${listId}/items`,
        item,
        { headers: getAuthHeaders() }
      )

      const list = lists.value.find(l => l.id === listId)
      if (list) {
        list.items.push(response.data)
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '添加失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 更新标的
  const updateItem = async (
    itemId: string,
    item: Partial<{
      code: string
      name: string
      item_type: string
      market?: string
      sync_frequency: string
      sync_history: boolean
      history_range: string
      indicators: string[]
      alerts: any[]
      tags: string[]
      extra_data: any
    }>
  ) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null

    try {
      const response = await axios.put(
        `${API_BASE_URL}/api/v1/monitor/items/${itemId}`,
        item,
        { headers: getAuthHeaders() }
      )

      // 更新本地数据
      for (const list of lists.value) {
        const index = list.items.findIndex(i => i.id === itemId)
        if (index !== -1) {
          list.items[index] = response.data
          break
        }
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 删除标的
  const deleteItem = async (itemId: string) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null

    try {
      await axios.delete(`${API_BASE_URL}/api/v1/monitor/items/${itemId}`, {
        headers: getAuthHeaders()
      })

      // 从本地移除
      for (const list of lists.value) {
        const index = list.items.findIndex(i => i.id === itemId)
        if (index !== -1) {
          list.items.splice(index, 1)
          break
        }
      }
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取指定类型的列表
  const getListsByType = (type: 'stock' | 'fund') => {
    return lists.value.filter(l => l.list_type === type)
  }

  // 根据ID获取列表
  const getListById = (id: string) => {
    return lists.value.find(l => l.id === id)
  }

  return {
    lists,
    isLoading,
    error,
    fetchLists,
    createList,
    updateList,
    deleteList,
    addItem,
    updateItem,
    deleteItem,
    getListsByType,
    getListById
  }
})
