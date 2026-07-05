<template>
  <div class="admin-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>系统概览</span>
          </template>
          <el-row :gutter="20" v-if="dashboard">
            <el-col :span="6">
              <div class="stat-box">
                <div class="stat-value">{{ dashboard.overview.total_roads }}</div>
                <div class="stat-label">道路总数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-box">
                <div class="stat-value">{{ dashboard.overview.total_users }}</div>
                <div class="stat-label">用户总数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-box">
                <div class="stat-value">{{ dashboard.overview.active_events }}</div>
                <div class="stat-label">活跃事件</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-box">
                <div class="stat-value">{{ dashboard.overview.recent_status_records }}</div>
                <div class="stat-label">最近状态记录</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>道路类型分布</span>
          </template>
          <v-chart
            v-if="dashboard"
            :option="roadTypeChartOption"
            style="height: 300px;"
          />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>事件类型分布(最近7天)</span>
          </template>
          <v-chart
            v-if="dashboard"
            :option="eventTypeChartOption"
            style="height: 300px;"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>数据备份与恢复</span>
          </template>
          <div class="backup-controls">
            <el-button type="primary" @click="handleBackup" :loading="backingUp">
              <el-icon><Download /></el-icon> 导出数据库备份
            </el-button>
            
            <el-upload
              class="upload-demo"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleRestore"
              accept=".json"
              style="display: inline-block; margin-left: 10px;"
            >
              <el-button type="warning" :loading="restoring">
                <el-icon><Upload /></el-icon> 从备份恢复数据
              </el-button>
            </el-upload>
            
            <div class="backup-tip">
              <el-alert
                title="注意：恢复数据将清空当前所有数据并替换为备份内容，请谨慎操作。"
                type="warning"
                show-icon
                :closable="false"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户管理</span>
              <el-button type="primary" @click="showInitDialog = true">
                初始化示例数据
              </el-button>
            </div>
          </template>

          <el-table :data="users" stripe v-loading="loadingUsers">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="is_admin" label="管理员" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_admin ? 'success' : 'info'">
                  {{ row.is_admin ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button
                  size="small"
                  :type="row.is_admin ? 'warning' : 'success'"
                  @click="toggleAdmin(row)"
                  :disabled="row.id === userStore.user.id"
                >
                  {{ row.is_admin ? '取消管理员' : '设为管理员' }}
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteUser(row)"
                  :disabled="row.id === userStore.user.id"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalUsers"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadUsers"
            @current-change="loadUsers"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>操作日志</span>
              <el-button type="primary" link @click="loadLogs">刷新</el-button>
            </div>
          </template>

          <el-table :data="logs" stripe v-loading="loadingLogs">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="action" label="操作" width="100">
              <template #default="{ row }">
                <el-tag :type="getActionType(row.action)">{{ row.action }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="table_name" label="对象" width="120" />
            <el-table-column prop="new_value" label="详情" show-overflow-tooltip />
            <el-table-column prop="changed_by" label="操作人" width="100" />
            <el-table-column prop="changed_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.changed_at) }}
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="logPage"
            v-model:page-size="logPageSize"
            :total="totalLogs"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadLogs"
            @current-change="loadLogs"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 初始化数据对话框 -->
    <el-dialog v-model="showInitDialog" title="初始化示例数据" width="400px">
      <el-alert
        title="警告"
        type="warning"
        description="此操作将创建示例道路数据,不会删除现有数据"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />
      <template #footer>
        <el-button @click="showInitDialog = false">取消</el-button>
        <el-button type="primary" @click="initData" :loading="initializing">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const userStore = useUserStore()

const dashboard = ref(null)
const users = ref([])
const loadingUsers = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalUsers = ref(0)
const showInitDialog = ref(false)
const initializing = ref(false)

// 日志相关
const logs = ref([])
const loadingLogs = ref(false)
const logPage = ref(1)
const logPageSize = ref(10)
const totalLogs = ref(0)

const loadLogs = async () => {
  loadingLogs.value = true
  try {
    const response = await api.get('/admin/audit-logs', {
      params: {
        page: logPage.value,
        per_page: logPageSize.value
      }
    })
    logs.value = response.data.logs
    totalLogs.value = response.data.total
  } catch (error) {
    console.error('加载日志失败:', error)
  } finally {
    loadingLogs.value = false
  }
}

const getActionType = (action) => {
  const map = {
    'INSERT': 'success',
    'UPDATE': 'warning',
    'DELETE': 'danger'
  }
  return map[action] || 'info'
}

const roadTypeChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderColor: '#00f3ff',
    textStyle: {
      color: '#fff'
    }
  },
  xAxis: {
    type: 'category',
    data: Object.keys(dashboard.value?.road_type_distribution || {}),
    axisLine: { lineStyle: { color: 'rgba(0, 243, 255, 0.3)' } },
    axisLabel: { color: '#a0a0a0' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(0, 243, 255, 0.05)' } },
    axisLabel: { color: '#a0a0a0' }
  },
  series: [
    {
      name: '道路数量',
      type: 'bar',
      data: Object.values(dashboard.value?.road_type_distribution || {}),
      itemStyle: {
        color: '#00f3ff'
      }
    }
  ]
}))

const eventTypeChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderColor: '#00f3ff',
    textStyle: {
      color: '#fff'
    }
  },
  xAxis: {
    type: 'category',
    data: Object.keys(dashboard.value?.event_type_distribution || {}),
    axisLine: { lineStyle: { color: 'rgba(0, 243, 255, 0.3)' } },
    axisLabel: { color: '#a0a0a0' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(0, 243, 255, 0.05)' } },
    axisLabel: { color: '#a0a0a0' }
  },
  series: [
    {
      name: '事件数量',
      type: 'bar',
      data: Object.values(dashboard.value?.event_type_distribution || {}),
      itemStyle: {
        color: '#ffbd2e'
      }
    }
  ]
}))

const loadDashboard = async () => {
  try {
    const response = await api.get('/admin/dashboard')
    dashboard.value = response.data
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}

const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await api.get('/admin/users', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value
      }
    })
    users.value = response.data.users
    totalUsers.value = response.data.total
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loadingUsers.value = false
  }
}

const toggleAdmin = async (row) => {
  try {
    await api.put(`/admin/users/${row.id}/admin`, {
      is_admin: !row.is_admin
    })
    ElMessage.success('权限更新成功')
    loadUsers()
  } catch (error) {
    console.error('更新权限失败:', error)
  }
}

const deleteUser = (row) => {
  ElMessageBox.confirm(`确定要删除用户"${row.username}"吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/admin/users/${row.id}`)
      ElMessage.success('删除成功')
      loadUsers()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

const initData = async () => {
  initializing.value = true
  try {
    await api.post('/admin/init-data')
    ElMessage.success('示例数据初始化成功')
    showInitDialog.value = false
    loadDashboard()
  } catch (error) {
    console.error('初始化数据失败:', error)
  } finally {
    initializing.value = false
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadDashboard()
  loadUsers()
  loadLogs()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-box {
  text-align: center;
  padding: 20px;
  background-color: var(--bg-elevated);
  border-radius: 8px;
  border: 1px solid var(--border-secondary);
  transition: all 0.3s;
}

.stat-box:hover {
  border-color: var(--primary-color);
  box-shadow: 0 0 15px var(--primary-color-alpha);
  transform: translateY(-2px);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 10px;
  text-shadow: 0 0 10px var(--primary-color-alpha);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
