<template>
  <div class="traffic-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交通状态查询</span>
          <div>
            <el-button @click="loadLatestStatus">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button
              v-if="userStore.isAdmin"
              type="primary"
              @click="showAddDialog = true"
            >
              <el-icon><Plus /></el-icon>
              添加状态
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="实时状态" name="latest">
          <!-- 添加筛选工具栏 -->
          <el-form :inline="true" class="filter-form">
            <el-form-item label="状态筛选">
              <el-select v-model="statusFilter" placeholder="全部状态" clearable @change="handleFilterChange" style="width: 120px">
                <el-option label="畅通" value="畅通" />
                <el-option label="缓行" value="缓行" />
                <el-option label="拥堵" value="拥堵" />
                <el-option label="严重拥堵" value="严重拥堵" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button @click="loadLatestStatus">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </el-form-item>
          </el-form>

          <el-table :data="latestStatus" stripe v-loading="loading">
            <el-table-column prop="road_name" label="道路名称" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <StatusTag :text="row.status" category="traffic" />
              </template>
            </el-table-column>
            <el-table-column prop="speed" label="平均速度(km/h)" width="150">
              <template #default="{ row }">
                {{ row.speed ? row.speed.toFixed(1) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="congestion_index" label="拥堵指数" width="120">
              <template #default="{ row }">
                {{ row.congestion_index ? row.congestion_index.toFixed(1) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="vehicle_count" label="车辆数" width="100" />
            <el-table-column prop="timestamp" label="更新时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 16px; text-align: right;">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @current-page-change="handlePageChange"
              @page-size-change="handlePageSizeChange"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="历史记录" name="history">
          <el-form :inline="true">
            <el-form-item label="道路">
              <el-select
                v-model="historyRoadId"
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
            <el-form-item label="时间范围">
              <el-select v-model="historyHours" @change="loadHistory" style="width: 160px">
                <el-option label="最近6小时" :value="6" />
                <el-option label="最近12小时" :value="12" />
                <el-option label="最近24小时" :value="24" />
                <el-option label="最近3天" :value="72" />
                <el-option label="最近7天" :value="168" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadHistory">查询</el-button>
            </el-form-item>
          </el-form>

          <TrafficHistoryChart :data="historyData" />
        </el-tab-pane>

        <el-tab-pane label="统计分析" name="statistics">
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form :inline="true" style="margin-bottom: 20px;">
                <el-form-item label="统计周期:">
                  <el-select v-model="statisticsHours" @change="loadStatistics" placeholder="选择周期" style="width: 160px">
                    <el-option label="最近6小时" :value="6" />
                    <el-option label="最近12小时" :value="12" />
                    <el-option label="最近24小时" :value="24" />
                    <el-option label="最近3天" :value="72" />
                    <el-option label="最近7天" :value="168" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="loadStatistics" :loading="loading">
                    <el-icon><Refresh /></el-icon>
                    刷新数据
                  </el-button>
                </el-form-item>
              </el-form>
            </el-col>
          </el-row>
          <!-- 调试信息 -->
          <el-alert v-if="statistics.status_distribution" type="info" :closable="false" style="margin-bottom: 20px;">
            <template #default>
              <div style="font-size: 12px;">
                已加载数据: {{ Object.keys(statistics.status_distribution).length }} 个状态
                | 平均拥堵指数: {{ statistics.avg_congestion_index }}
                | 平均速度: {{ statistics.avg_speed }} km/h
              </div>
            </template>
          </el-alert>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <div class="card-header">
                    <span>状态分布</span>
                    <el-button type="text" @click="loadStatistics" :loading="loading">刷新</el-button>
                  </div>
                </template>
                <div v-if="statistics.status_distribution && Object.keys(statistics.status_distribution).length > 0" style="width: 100%; height: 300px;">
                  <TrafficStatusPieChart :data="statistics.status_distribution" />
                </div>
                <el-empty v-else description="暂无数据，请点击刷新" />
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>统计信息</template>
                <div class="stat-info">
                  <div class="stat-item">
                    <span class="label">平均拥堵指数:</span>
                    <span class="value">{{ statistics.avg_congestion_index || '--' }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="label">平均速度:</span>
                    <span class="value">{{ statistics.avg_speed || '--' }} km/h</span>
                  </div>
                  <div class="stat-item">
                    <span class="label">统计周期:</span>
                    <span class="value">最近 {{ statistics.period_hours || statisticsHours }} 小时</span>
                  </div>
                  <div class="stat-item" style="border-bottom: 1px solid var(--border-secondary);">
                    <span class="label" style="font-weight: bold;">状态统计:</span>
                  </div>
                  <div v-for="(count, status) in statistics.status_distribution || {}" :key="status" class="stat-item">
                    <span class="label">{{ status }}:</span>
                    <span class="value">{{ count }} 条</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 添加状态对话框 -->
    <TrafficStatusFormDialog
      v-model:visible="showAddDialog"
      :roads="roads"
      @saved="loadLatestStatus"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRoute } from 'vue-router'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import StatusTag from '@/components/StatusTag.vue'
import TrafficHistoryChart from '@/components/TrafficHistoryChart.vue'
import TrafficStatusPieChart from '@/components/TrafficStatusPieChart.vue'
import TrafficStatusFormDialog from '@/components/TrafficStatusFormDialog.vue'

const userStore = useUserStore()
const route = useRoute()

const loading = ref(false)
const showAddDialog = ref(false)
const activeTab = ref('latest')
const statusFilter = ref('')

const latestStatus = ref([])
const roads = ref([])
const historyData = ref([])
const historyRoadId = ref(null)
const historyHours = ref(24)
const statistics = ref({})
const statisticsHours = ref(24)
const chartKey = ref(0)
const chartRef = ref(null)

// 分页参数
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadLatestStatus = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const response = await api.get('/traffic/status', { params })
    latestStatus.value = response.data.statuses
    total.value = response.data.total
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadLatestStatus()
}

const handlePageChange = (newPage) => {
  currentPage.value = newPage
  loadLatestStatus()
}

const handlePageSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadLatestStatus()
}

const loadRoads = async () => {
  try {
    const response = await api.get('/roads', { params: { per_page: 100 } })
    roads.value = response.data.roads
  } catch (error) {
    console.error('加载道路列表失败:', error)
  }
}

const loadHistory = async () => {
  if (!historyRoadId.value) {
    ElMessage.warning('请选择道路')
    return
  }

  loading.value = true
  try {
    const response = await api.get(
      `/traffic/status/${historyRoadId.value}/history`,
      { params: { hours: historyHours.value } }
    )
    historyData.value = response.data.history
  } catch (error) {
    console.error('加载历史数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    console.log('🔄 开始加载统计数据，周期:', statisticsHours.value)
    const response = await api.get('/traffic/statistics', {
      params: { hours: statisticsHours.value }
    })
    
    console.log('📥 API 返回数据:', response.data)
    console.log('📥 状态分布:', response.data.status_distribution)
    
    // 完全重新赋值以触发响应式更新
    statistics.value = {}
    await nextTick()
    
    statistics.value = {
      status_distribution: response.data.status_distribution,
      avg_congestion_index: response.data.avg_congestion_index,
      avg_speed: response.data.avg_speed,
      period_hours: response.data.period_hours
    }
    
    console.log('✅ 统计数据加载成功:', statistics.value)
    console.log('✅ 当前 chartKey:', chartKey.value)
    
    // 触发 chartKey 更新以强制 VChart 重新渲染
    chartKey.value++
    console.log('🔄 增加 chartKey 到:', chartKey.value)
  } catch (error) {
    console.error('❌ 加载统计数据失败:', error.message)
    console.error('❌ 错误详情:', error)
    ElMessage.error('加载统计数据失败: ' + error.message)
  }
}

const handleTabChange = (tab) => {
  if (tab === 'statistics') {
    // 切换到统计分析标签时加载数据
    if (Object.keys(statistics.value).length === 0) {
      loadStatistics()
    }
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  if (route.query.status) {
    statusFilter.value = route.query.status
  }
  loadLatestStatus()
  loadRoads()
  loadStatistics()  // 页面加载时自动加载统计数据
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  padding: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 15px 0;
  border-bottom: 1px solid var(--border-secondary);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-item .label {
  color: var(--text-secondary);
  font-size: 14px;
}

.stat-item .value {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: bold;
  text-shadow: 0 0 5px var(--primary-color-alpha);
}
</style>
