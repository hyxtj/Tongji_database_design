<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" @click="navigateTo('roads')">
          <div class="stat-content">
            <div class="stat-icon icon-primary">
              <el-icon :size="32"><MapLocation /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">道路总数</div>
              <div class="stat-value">{{ stats.totalRoads }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" @click="navigateTo('smooth')">
          <div class="stat-content">
            <div class="stat-icon icon-success">
              <el-icon :size="32"><SuccessFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">畅通道路</div>
              <div class="stat-value">{{ stats.smoothRoads }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" @click="navigateTo('congested')">
          <div class="stat-content">
            <div class="stat-icon icon-danger">
              <el-icon :size="32"><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">拥堵道路</div>
              <div class="stat-value">{{ stats.congestedRoads }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" @click="navigateTo('events')">
          <div class="stat-content">
            <div class="stat-icon icon-warning">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">活跃事件</div>
              <div class="stat-value">{{ stats.activeEvents }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span class="card-title">GIS 地图可视化</span>
          </template>
          <TrafficMap height="400px" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span class="card-title">24小时拥堵趋势</span>
          </template>
          <v-chart :option="trendChartOption" style="height: 300px;" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span class="card-title">交通状态分布</span>
          </template>
          <v-chart :option="statusChartOption" style="height: 300px;" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="list-card">
          <template #header>
            <span class="card-title">最新交通事件</span>
          </template>
          <el-timeline v-if="recentEvents.length > 0">
            <el-timeline-item
              v-for="event in recentEvents"
              :key="event.id"
              :timestamp="formatTime(event.start_time)"
              placement="top"
              :color="getEventColor(event.severity)"
            >
              <el-tag :type="getEventType(event.severity)" effect="dark">{{ event.event_type }}</el-tag>
              <p class="event-desc">{{ event.description }}</p>
              <p class="event-road">
                道路: {{ event.road_name }}
              </p>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无交通事件" :image-size="120" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">实时交通状态</span>
              <div class="header-actions">
                <el-switch
                  v-model="autoRefresh"
                  active-text="自动刷新"
                  inactive-text="手动"
                  style="margin-right: 15px"
                />
                <el-button
                  class="refresh-btn"
                  type="primary"
                  link
                  @click="loadLatestStatus"
                >
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          <el-table :data="latestStatus" stripe style="width: 100%">
            <el-table-column prop="road_name" label="道路名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" effect="dark">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="speed" label="平均速度(km/h)" width="140" />
            <el-table-column prop="congestion_index" label="拥堵指数" width="100" />
            <el-table-column prop="timestamp" label="更新时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import TrafficMap from '@/components/TrafficMap.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'

use([CanvasRenderer, PieChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const router = useRouter()

const stats = ref({
  totalRoads: 0,
  smoothRoads: 0,
  congestedRoads: 0,
  activeEvents: 0
})

const latestStatus = ref([])
const recentEvents = ref([])
const trendData = ref({ times: [], values: [] })
const autoRefresh = ref(true)
let refreshTimer = null

const currentTheme = ref(document.documentElement.getAttribute('data-theme') || 'dark')

const updateTheme = () => {
  currentTheme.value = document.documentElement.getAttribute('data-theme') || 'dark'
}

onMounted(() => {
  window.addEventListener('theme-change', updateTheme)
  window.addEventListener('storage', (e) => {
    if (e.key === 'theme') {
      updateTheme()
    }
  })
  loadLatestStatus()
  loadRecentEvents()
  loadRoads()
  loadTrendData()
  
  // 启动自动刷新
  startAutoRefresh()
})

onUnmounted(() => {
  window.removeEventListener('theme-change', updateTheme)
  stopAutoRefresh()
})

// 监听自动刷新开关
import { watch } from 'vue'
watch(autoRefresh, (newVal) => {
  if (newVal) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(() => {
    loadLatestStatus()
    loadRecentEvents()
    // 趋势图不需要频繁刷新，可以每5分钟刷新一次，这里简单起见一起刷新
  }, 10000) // 每10秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const trendChartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  const textColor = isDark ? '#e0e0e0' : '#212529'
  const lineColor = isDark ? '#00f3ff' : '#0d6efd'
  const splitLineColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.value.times,
      axisLabel: { color: textColor },
      axisLine: { lineStyle: { color: textColor } }
    },
    yAxis: {
      type: 'value',
      name: '拥堵指数',
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor },
      splitLine: { lineStyle: { color: splitLineColor } }
    },
    series: [
      {
        name: '平均拥堵指数',
        type: 'line',
        smooth: true,
        data: trendData.value.values,
        itemStyle: { color: lineColor },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(13, 110, 253, 0.3)' },
              { offset: 1, color: isDark ? 'rgba(0, 243, 255, 0)' : 'rgba(13, 110, 253, 0)' }
            ]
          }
        }
      }
    ]
  }
})

const statusChartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  
  // Theme colors
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#00f3ff' : '#007bff'
  const tooltipText = isDark ? '#fff' : '#212529'
  const legendText = isDark ? '#e0e0e0' : '#212529'
  const borderColor = isDark ? '#000' : '#fff'
  const emphasisLabelColor = isDark ? '#fff' : '#000'
  const shadowColor = isDark ? 'rgba(0, 243, 255, 0.5)' : 'rgba(0, 123, 255, 0.3)'
  const smoothColor = isDark ? '#00f3ff' : '#0d6efd'
  const congestedColor = isDark ? '#ff0055' : '#dc3545'

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: {
        color: tooltipText
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: legendText
      }
    },
    series: [
      {
        name: '交通状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: borderColor,
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold',
            color: emphasisLabelColor
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: shadowColor
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: stats.value.smoothRoads, name: '畅通', itemStyle: { color: smoothColor } },
          { value: stats.value.congestedRoads, name: '拥堵', itemStyle: { color: congestedColor } }
        ]
      }
    ]
  }
})

const navigateTo = (type) => {
  switch (type) {
    case 'roads':
      router.push('/roads')
      break
    case 'smooth':
      router.push({ path: '/traffic', query: { status: '畅通' } })
      break
    case 'congested':
      router.push({ path: '/traffic', query: { status: '拥堵' } })
      break
    case 'events':
      router.push({ path: '/events', query: { status: 'active' } })
      break
  }
}

const loadTrendData = async () => {
  try {
    const res = await api.get('/analytics/time-series/congestion', {
      params: { hours: 24, aggregation: 'hour' }
    })
    if (res.data && res.data.data) {
      trendData.value = {
        times: res.data.data.map(item => {
            const date = new Date(item.timestamp)
            return `${date.getHours()}:00`
        }),
        values: res.data.data.map(item => item.congestion_index)
      }
    }
  } catch (error) {
    console.error('Failed to load trend data:', error)
  }
}

const loadLatestStatus = async () => {
  try {
    const response = await api.get('/traffic/status/latest')
    latestStatus.value = response.data.statuses.slice(0, 10)
    
    // 统计交通状态
    const statusCount = {}
    response.data.statuses.forEach(item => {
      statusCount[item.status] = (statusCount[item.status] || 0) + 1
    })
    
    stats.value.smoothRoads = statusCount['畅通'] || 0
    stats.value.congestedRoads = (statusCount['拥堵'] || 0) + (statusCount['严重拥堵'] || 0)
  } catch (error) {
    console.error('加载交通状态失败:', error)
  }
}

const loadRecentEvents = async () => {
  try {
    const response = await api.get('/events/active')
    recentEvents.value = response.data.events.slice(0, 5)
    stats.value.activeEvents = response.data.count
  } catch (error) {
    console.error('加载交通事件失败:', error)
  }
}

const loadRoads = async () => {
  try {
    const response = await api.get('/roads', { params: { per_page: 1 } })
    stats.value.totalRoads = response.data.total
  } catch (error) {
    console.error('加载道路数据失败:', error)
  }
}

const getStatusType = (status) => {
  const typeMap = {
    '畅通': 'success',
    '缓行': 'warning',
    '拥堵': 'danger',
    '严重拥堵': 'danger'
  }
  return typeMap[status] || 'info'
}

const getEventType = (severity) => {
  const typeMap = {
    '轻微': 'info',
    '一般': 'warning',
    '严重': 'danger'
  }
  return typeMap[severity] || 'info'
}

const getEventColor = (severity) => {
  const colorMap = {
    '轻微': '#909399',
    '一般': '#e6a23c',
    '严重': '#f56c6c'
  }
  return colorMap[severity] || '#909399'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.stat-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid var(--border-primary);
  background: var(--bg-card);
  backdrop-filter: blur(10px);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0 20px var(--primary-color-alpha);
  border-color: var(--primary-color);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.icon-primary {
  background: linear-gradient(135deg, #00f3ff, #0066ff);
}

.icon-success {
  background: linear-gradient(135deg, #00ff9d, #00cc44);
}

.icon-danger {
  background: linear-gradient(135deg, #ff0055, #cc0000);
}

.icon-warning {
  background: linear-gradient(135deg, #ffcc00, #ff9900);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  text-shadow: 0 0 10px var(--primary-color-alpha);
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 5px var(--primary-color-alpha);
}

.event-desc {
  margin: 5px 0;
  color: var(--text-primary);
}

.event-road {
  color: var(--text-secondary);
  font-size: 12px;
}

.refresh-btn {
  color: var(--primary-color);
}

.refresh-btn:hover {
  color: var(--secondary-color);
  text-shadow: 0 0 5px var(--secondary-color);
}

/* Chart and List Cards */
.chart-card, .list-card, .table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  backdrop-filter: blur(10px);
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--border-primary);
}

:deep(.el-table) {
  background-color: transparent !important;
  color: var(--text-primary);
  --el-table-header-bg-color: rgba(0, 243, 255, 0.1);
  --el-table-row-hover-bg-color: rgba(0, 243, 255, 0.1);
  --el-table-border-color: var(--border-primary);
}

:deep(.el-table th), :deep(.el-table tr) {
  background-color: transparent !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--border-primary);
}
</style>
