<template>
  <div class="events-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交通事件管理</span>
          <el-button
            v-if="userStore.isLoggedIn"
            type="primary"
            @click="openAddDialog"
          >
            <el-icon><Plus /></el-icon>
            {{ userStore.isAdmin ? '发布事件' : '上报事件' }}
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm">
        <el-form-item label="道路">
          <el-select
            v-model="searchForm.road_id"
            placeholder="选择道路"
            clearable
            filterable
            style="width: 160px"
          >
            <el-option
              v-for="road in roads"
              :key="road.id"
              :label="road.name"
              :value="road.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="事件类型">
          <el-select v-model="searchForm.type" placeholder="类型" clearable style="width: 120px">
            <el-option label="事故" value="事故" />
            <el-option label="故障" value="故障" />
            <el-option label="施工" value="施工" />
            <el-option label="管制" value="管制" />
            <el-option label="积水" value="积水" />
            <el-option label="障碍物" value="障碍物" />
            <el-option label="恶劣天气" value="恶劣天气" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="searchForm.severity" placeholder="严重程度" clearable style="width: 120px">
            <el-option label="轻微" value="低" />
            <el-option label="一般" value="中" />
            <el-option label="严重" value="高" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="状态" clearable style="width: 120px">
            <el-option label="活跃" value="active" />
            <el-option label="已解决" value="resolved" />
            <el-option v-if="userStore.isAdmin" label="待审核" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="events" stripe v-loading="loading">
        <el-table-column prop="road_name" label="道路名称" width="150" />
        <el-table-column prop="event_type" label="事件类型" width="100">
          <template #default="{ row }">
            <StatusTag :text="row.event_type" category="event_type" />
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <StatusTag :text="formatSeverity(row.severity)" category="severity" />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <StatusTag :text="row.status" category="status">
              {{ formatStatus(row.status) }}
            </StatusTag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="发生时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" v-if="userStore.isAdmin">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="handleApprove(row)">通过</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">拒绝</el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button
                v-if="row.status === 'active'"
                size="small"
                type="success"
                @click="handleResolve(row)"
              >
                解决
              </el-button>
              <el-button
                v-if="row.status === 'resolved'"
                size="small"
                type="danger"
                link
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadEvents"
        @current-change="loadEvents"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <EventFormDialog
      v-model:visible="showAddDialog"
      :event-data="editingEvent"
      :roads="roads"
      @saved="loadEvents"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRoute } from 'vue-router'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import StatusTag from '@/components/StatusTag.vue'
import EventFormDialog from '@/components/EventFormDialog.vue'

const userStore = useUserStore()
const route = useRoute()

const loading = ref(false)
const showAddDialog = ref(false)
const editingEvent = ref(null)
const events = ref([])
const roads = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = reactive({
  road_id: null,
  type: '',
  severity: '',
  status: 'active'
})

const openAddDialog = () => {
  editingEvent.value = null
  showAddDialog.value = true
}

const loadEvents = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      ...searchForm
    }
    const response = await api.get('/events', { params })
    events.value = response.data.events
    total.value = response.data.total
  } catch (error) {
    console.error('加载事件列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadRoads = async () => {
  try {
    const response = await api.get('/roads', { params: { per_page: 100 } })
    roads.value = response.data.roads
  } catch (error) {
    console.error('加载道路列表失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadEvents()
}

const handleEdit = (row) => {
  editingEvent.value = row
  showAddDialog.value = true
}

const handleApprove = async (row) => {
  try {
    await api.put(`/events/${row.id}/approve`)
    ElMessage.success('审核通过')
    loadEvents()
  } catch (error) {
    console.error('操作失败:', error)
  }
}

const handleResolve = async (row) => {
  ElMessageBox.confirm('确定要将此事件标记为已解决吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'success'
  }).then(async () => {
    try {
      await api.put(`/events/${row.id}`, { status: 'resolved' })
      ElMessage.success('操作成功')
      loadEvents()
    } catch (error) {
      console.error('操作失败:', error)
    }
  })
}

const handleDelete = (row) => {
  const actionText = row.status === 'pending' ? '拒绝' : '删除'
  ElMessageBox.confirm(`确定要${actionText}此事件吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/events/${row.id}`)
      ElMessage.success(`${actionText}成功`)
      loadEvents()
    } catch (error) {
      console.error('操作失败:', error)
    }
  })
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const formatStatus = (status) => {
  const map = {
    'active': '活跃',
    'resolved': '已解决',
    'pending': '待审核'
  }
  return map[status] || status
}

const formatSeverity = (val) => {
  const map = {
    '低': '轻微',
    '中': '一般',
    '高': '严重'
  }
  return map[val] || val
}

onMounted(() => {
  if (route.query.status) {
    searchForm.status = route.query.status
  }
  loadEvents()
  loadRoads()
})
</script>

<style scoped>
.events-page {
  padding: 20px;
}

:deep(.el-card) {
  background: rgba(5, 5, 8, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 243, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
  color: #fff;
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(0, 243, 255, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: #00f3ff;
  text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
}

/* 表格样式 */
:deep(.el-table) {
  background-color: transparent !important;
  color: #fff;
  --el-table-border-color: rgba(0, 243, 255, 0.2);
  --el-table-header-bg-color: rgba(0, 243, 255, 0.1);
  --el-table-row-hover-bg-color: rgba(0, 243, 255, 0.15) !important;
  --el-table-tr-bg-color: transparent;
}

:deep(.el-table th),
:deep(.el-table tr),
:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid rgba(0, 243, 255, 0.1);
}

:deep(.el-table__inner-wrapper::before) {
  background-color: rgba(0, 243, 255, 0.2);
}

/* 表单样式 */
:deep(.el-form-item__label) {
  color: #00f3ff;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  background-color: rgba(0, 243, 255, 0.05);
  box-shadow: 0 0 0 1px rgba(0, 243, 255, 0.2) inset;
}

:deep(.el-input__inner) {
  color: #fff;
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background: linear-gradient(45deg, #00f3ff, #0066ff);
  border: none;
  box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
}

:deep(.el-button--primary:hover) {
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.5);
  transform: translateY(-1px);
}

:deep(.el-button--success) {
  background: linear-gradient(45deg, #00ff9d, #00cc7a);
  border: none;
  box-shadow: 0 0 10px rgba(0, 255, 157, 0.3);
}

:deep(.el-button--danger) {
  background: linear-gradient(45deg, #ff3860, #ff0000);
  border: none;
  box-shadow: 0 0 10px rgba(255, 56, 96, 0.3);
}

/* 分页样式 */
:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: #a0a0a0;
  --el-pagination-button-color: #a0a0a0;
  --el-pagination-button-disabled-bg-color: transparent;
  --el-pagination-hover-color: #00f3ff;
}

:deep(.el-pagination .el-pager li) {
  background: transparent;
  border: 1px solid rgba(0, 243, 255, 0.2);
  color: #a0a0a0;
}

:deep(.el-pagination .el-pager li.is-active) {
  background: rgba(0, 243, 255, 0.2);
  color: #00f3ff;
  border-color: #00f3ff;
}

/* 标签样式 */
:deep(.el-tag) {
  background-color: rgba(0, 243, 255, 0.1);
  border-color: rgba(0, 243, 255, 0.3);
  color: #00f3ff;
}
</style>
