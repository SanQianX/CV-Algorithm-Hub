<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ModeToggle from '@/components/ui/ModeToggle.vue'

const router = useRouter()

// API基础URL
const API_BASE = ''

// 状态变量
const isLoading = ref(false)
const isRefreshing = ref(false)
const isSubmitting = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// 模态框状态
const showAddModal = ref(false)
const showEditModal = ref(false)

// 用户列表数据
const users = ref<Array<{
  id: string
  username: string
  email: string
  created_at: string
  updated_at: string
}>>([])

// 当前编辑的用户
const editingUser = ref<{ id: string; username: string; email: string } | null>(null)

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

// 添加用户表单
const addForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 编辑用户表单
const editForm = reactive({
  username: '',
  email: '',
  password: ''
})

// 表单验证错误
const formErrors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

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

// 格式化时间
const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取用户列表
const fetchUsers = async (page = 1) => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/db-manager/users?page=${page}&page_size=${pagination.value.pageSize}`, {
      headers: getAuthHeaders()
    })

    if (res.ok) {
      const data = await res.json()
      users.value = data.items || []
      pagination.value = {
        page: data.page,
        pageSize: data.page_size,
        total: data.total,
        totalPages: data.total_pages
      }
    } else {
      const err = await res.json()
      showMessage(err.detail || '加载用户列表失败', 'error')
    }
  } catch (e) {
    console.error('加载用户列表失败:', e)
    showMessage('加载用户列表失败', 'error')
  } finally {
    isLoading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  isRefreshing.value = true
  await fetchUsers(pagination.value.page)
  isRefreshing.value = false
}

// 验证添加用户表单
const validateAddForm = (): boolean => {
  formErrors.username = ''
  formErrors.email = ''
  formErrors.password = ''
  formErrors.confirmPassword = ''

  let isValid = true

  if (!addForm.username || addForm.username.length < 3) {
    formErrors.username = '用户名长度至少为3个字符'
    isValid = false
  } else if (addForm.username.length > 20) {
    formErrors.username = '用户名长度不能超过20个字符'
    isValid = false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!addForm.email || !emailRegex.test(addForm.email)) {
    formErrors.email = '请输入有效的邮箱地址'
    isValid = false
  }

  if (!addForm.password || addForm.password.length < 6) {
    formErrors.password = '密码长度至少为6个字符'
    isValid = false
  }

  if (addForm.password !== addForm.confirmPassword) {
    formErrors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  return isValid
}

// 验证编辑用户表单
const validateEditForm = (): boolean => {
  formErrors.username = ''
  formErrors.email = ''
  formErrors.password = ''

  let isValid = true

  if (editForm.username) {
    if (editForm.username.length < 3) {
      formErrors.username = '用户名长度至少为3个字符'
      isValid = false
    } else if (editForm.username.length > 20) {
      formErrors.username = '用户名长度不能超过20个字符'
      isValid = false
    }
  }

  if (editForm.email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(editForm.email)) {
      formErrors.email = '请输入有效的邮箱地址'
      isValid = false
    }
  }

  if (editForm.password && editForm.password.length < 6) {
    formErrors.password = '密码长度至少为6个字符'
    isValid = false
  }

  return isValid
}

// 添加用户
const addUser = async () => {
  if (!validateAddForm()) {
    return
  }

  isSubmitting.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/db-manager/users`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        username: addForm.username,
        email: addForm.email,
        password: addForm.password
      })
    })

    if (res.ok) {
      showMessage('添加用户成功', 'success')
      closeAddModal()
      await fetchUsers(pagination.value.page)
    } else {
      const err = await res.json()
      showMessage(err.detail || '添加用户失败', 'error')
    }
  } catch (e) {
    console.error('添加用户失败:', e)
    showMessage('添加用户失败', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 删除用户
const deleteUser = async (userId: string, username: string) => {
  if (!confirm(`确定要删除用户 "${username}" 吗？此操作不可恢复！`)) {
    return
  }

  try {
    const res = await fetch(`${API_BASE}/api/v1/db-manager/users/${userId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })

    if (res.ok) {
      const result = await res.json()
      showMessage(result.message || '删除用户成功', 'success')
      await fetchUsers(pagination.value.page)
    } else {
      const err = await res.json()
      showMessage(err.detail || '删除用户失败', 'error')
    }
  } catch (e) {
    console.error('删除用户失败:', e)
    showMessage('删除用户失败', 'error')
  }
}

// 打开编辑用户模态框
const openEditModal = async (userId: string) => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/db-manager/users/${userId}`, {
      headers: getAuthHeaders()
    })

    if (res.ok) {
      const user = await res.json()
      editingUser.value = user
      editForm.username = user.username
      editForm.email = user.email
      editForm.password = ''
      showEditModal.value = true
    } else {
      showMessage('获取用户信息失败', 'error')
    }
  } catch (e) {
    console.error('获取用户信息失败:', e)
    showMessage('获取用户信息失败', 'error')
  }
}

// 更新用户
const updateUser = async () => {
  if (!editingUser.value) return

  if (!validateEditForm()) {
    return
  }

  isSubmitting.value = true
  try {
    const body: any = {}
    if (editForm.username) body.username = editForm.username
    if (editForm.email) body.email = editForm.email
    if (editForm.password) body.password = editForm.password

    const res = await fetch(`${API_BASE}/api/v1/db-manager/users/${editingUser.value.id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(body)
    })

    if (res.ok) {
      showMessage('更新用户成功', 'success')
      closeEditModal()
      await fetchUsers(pagination.value.page)
    } else {
      const err = await res.json()
      showMessage(err.detail || '更新用户失败', 'error')
    }
  } catch (e) {
    console.error('更新用户失败:', e)
    showMessage('更新用户失败', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 关闭添加模态框
const closeAddModal = () => {
  showAddModal.value = false
  addForm.username = ''
  addForm.email = ''
  addForm.password = ''
  addForm.confirmPassword = ''
  formErrors.username = ''
  formErrors.email = ''
  formErrors.password = ''
  formErrors.confirmPassword = ''
}

// 关闭编辑模态框
const closeEditModal = () => {
  showEditModal.value = false
  editingUser.value = null
  editForm.username = ''
  editForm.email = ''
  editForm.password = ''
  formErrors.username = ''
  formErrors.email = ''
  formErrors.password = ''
}

// 页面加载
onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="user-manager-page">
    <header class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/dashboard')">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          返回
        </button>
        <h1 class="logo">用户信息管理</h1>
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

        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <h2 class="page-title">用户列表</h2>
            <span class="user-count">共 {{ pagination.total }} 个用户</span>
          </div>
          <div class="toolbar-right">
            <button class="action-btn add" @click="showAddModal = true">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
              添加用户
            </button>
            <button class="action-btn refresh" @click="refreshData" :disabled="isRefreshing">
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
                <th>用户ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>注册时间</th>
                <th>最后更新</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!isLoading && users.length === 0">
                <td colspan="6" class="empty-state">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                  </svg>
                  <p>暂无用户数据</p>
                </td>
              </tr>
              <tr v-else-if="isLoading">
                <td colspan="6" class="loading-state">
                  <div class="spinner"></div>
                  <p>加载中...</p>
                </td>
              </tr>
              <tr v-for="user in users" :key="user.id">
                <td class="id-cell">{{ user.id }}</td>
                <td class="username-cell">{{ user.username }}</td>
                <td class="email-cell">{{ user.email }}</td>
                <td class="date-cell">{{ formatDateTime(user.created_at) }}</td>
                <td class="date-cell">{{ formatDateTime(user.updated_at) }}</td>
                <td class="action-cell">
                  <button class="icon-btn edit" @click="openEditModal(user.id)" title="编辑用户">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                    </svg>
                  </button>
                  <button class="icon-btn delete" @click="deleteUser(user.id, user.username)" title="删除用户">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页 -->
        <div class="pagination" v-if="pagination.totalPages > 1">
          <button
            class="page-btn"
            :disabled="pagination.page === 1"
            @click="fetchUsers(pagination.page - 1)"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ pagination.page }} / {{ pagination.totalPages }} 页
          </span>
          <button
            class="page-btn"
            :disabled="pagination.page === pagination.totalPages"
            @click="fetchUsers(pagination.page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </main>

    <!-- 添加用户模态框 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal">
        <div class="modal-header">
          <h3>添加用户</h3>
          <button class="close-btn" @click="closeAddModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addUser">
            <div class="form-group" :class="{ 'has-error': formErrors.username }">
              <label>用户名</label>
              <input
                v-model="addForm.username"
                type="text"
                placeholder="请输入用户名（3-20个字符）"
                maxlength="20"
              />
              <span v-if="formErrors.username" class="error-text">{{ formErrors.username }}</span>
            </div>
            <div class="form-group" :class="{ 'has-error': formErrors.email }">
              <label>邮箱</label>
              <input
                v-model="addForm.email"
                type="email"
                placeholder="请输入邮箱地址"
              />
              <span v-if="formErrors.email" class="error-text">{{ formErrors.email }}</span>
            </div>
            <div class="form-group" :class="{ 'has-error': formErrors.password }">
              <label>密码</label>
              <input
                v-model="addForm.password"
                type="password"
                placeholder="请输入密码（至少6个字符）"
              />
              <span v-if="formErrors.password" class="error-text">{{ formErrors.password }}</span>
            </div>
            <div class="form-group" :class="{ 'has-error': formErrors.confirmPassword }">
              <label>确认密码</label>
              <input
                v-model="addForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
              />
              <span v-if="formErrors.confirmPassword" class="error-text">{{ formErrors.confirmPassword }}</span>
            </div>
            <div class="modal-actions">
              <button type="button" class="cancel-btn" @click="closeAddModal">取消</button>
              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                {{ isSubmitting ? '提交中...' : '添加' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 编辑用户模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <div class="modal-header">
          <h3>编辑用户</h3>
          <button class="close-btn" @click="closeEditModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateUser">
            <div class="form-group" :class="{ 'has-error': formErrors.username }">
              <label>用户名</label>
              <input
                v-model="editForm.username"
                type="text"
                placeholder="留空表示不修改"
                maxlength="20"
              />
              <span v-if="formErrors.username" class="error-text">{{ formErrors.username }}</span>
            </div>
            <div class="form-group" :class="{ 'has-error': formErrors.email }">
              <label>邮箱</label>
              <input
                v-model="editForm.email"
                type="email"
                placeholder="留空表示不修改"
              />
              <span v-if="formErrors.email" class="error-text">{{ formErrors.email }}</span>
            </div>
            <div class="form-group" :class="{ 'has-error': formErrors.password }">
              <label>新密码</label>
              <input
                v-model="editForm.password"
                type="password"
                placeholder="留空表示不修改密码"
              />
              <span v-if="formErrors.password" class="error-text">{{ formErrors.password }}</span>
            </div>
            <div class="modal-actions">
              <button type="button" class="cancel-btn" @click="closeEditModal">取消</button>
              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                {{ isSubmitting ? '提交中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-manager-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

:global(.dark) .user-manager-page {
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
}

:global(.dark) .toolbar {
  background: #1f2937;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

:global(.dark) .page-title {
  color: #f3f4f6;
}

.user-count {
  font-size: 0.875rem;
  color: #6b7280;
}

:global(.dark) .user-count {
  color: #9ca3af;
}

.toolbar-right {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn svg {
  width: 1rem;
  height: 1rem;
}

.action-btn.add {
  color: white;
  background: #10b981;
}

.action-btn.add:hover:not(:disabled) {
  background: #059669;
}

.action-btn.refresh {
  color: white;
  background: #3b82f6;
}

.action-btn.refresh:hover:not(:disabled) {
  background: #2563eb;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.id-cell {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.75rem;
  color: #6b7280;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

:global(.dark) .id-cell {
  color: #9ca3af;
}

.username-cell {
  font-weight: 500;
  color: #1f2937;
}

:global(.dark) .username-cell {
  color: #f3f4f6;
}

.email-cell {
  color: #3b82f6;
}

.date-cell {
  color: #6b7280;
}

:global(.dark) .date-cell {
  color: #9ca3af;
}

.action-cell {
  display: flex;
  gap: 0.5rem;
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
}

.icon-btn.delete:hover {
  background: #fee2e2;
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

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem 0;
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
  max-width: 450px;
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
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

:global(.dark) .form-group label {
  color: #f3f4f6;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  color: #1f2937;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  box-sizing: border-box;
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

.form-group.has-error input {
  border-color: #ef4444;
}

.error-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
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

.submit-btn:hover:not(:disabled) {
  background: #2563eb;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .toolbar {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .toolbar-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .toolbar-right {
    justify-content: stretch;
  }

  .action-btn {
    flex: 1;
    justify-content: center;
  }

  .data-table {
    font-size: 0.75rem;
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
  }

  .id-cell {
    max-width: 50px;
  }
}
</style>
