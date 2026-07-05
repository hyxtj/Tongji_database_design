<template>
  <div class="analytics-container">
    <!-- 页面标题和操作栏 -->
    <el-row :gutter="20" class="header-row">
      <el-col :span="24">
        <el-card class="header-card">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><DataAnalysis /></el-icon>
                数据分析
              </span>
            </div>
          </template>

          <!-- 日期范围和快速选择 -->
          <div class="filter-container">
            <el-form :inline="true" class="filter-form">
              <el-form-item label="日期范围">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  style="width: 300px"
                />
              </el-form-item>
              <el-form-item label="快速选择">
                <el-select v-model="quickRange" placeholder="选择时间范围" style="width: 160px">
                  <el-option label="近7天" value="7" />
                  <el-option label="近30天" value="30" />
                  <el-option label="本周" value="week" />
                  <el-option label="本月" value="month" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadAllAnalytics" :loading="loading">
                  <el-icon><Refresh /></el-icon>
                  刷新数据
                </el-button>
                <el-button @click="exportAnalytics">
                  <el-icon><Download /></el-icon>
                  导出报告
                </el-button>
                <el-button type="success" @click="printReport">
                  <el-icon><Printer /></el-icon>
                  打印报表
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 每日汇总卡片 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card v-loading="loading" class="summary-card">
          <template #header>
            <span>
              <el-icon><BarChart /></el-icon>
              每日汇总
            </span>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">平均拥堵指数</div>
                <div class="summary-value">{{ dailySummary.avgCongestion?.toFixed(2) || '--' }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">平均速度 (km/h)</div>
                <div class="summary-value">{{ dailySummary.avgSpeed?.toFixed(1) || '--' }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">发生事件数</div>
                <div class="summary-value" style="color: var(--color-warning)">{{ dailySummary.eventCount || 0 }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">事件处理率</div>
                <div class="summary-value" style="color: var(--color-success)">
                  {{ dailySummary.eventResolutionRate ? (dailySummary.eventResolutionRate * 100).toFixed(1) + '%' : '--' }}
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析标签页 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-tabs v-model="activeTab" type="card">
          <!-- 时间序列分析 -->
          <el-tab-pane label="时间序列分析" name="timeseries">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>拥堵指数时间序列</span>
                  </template>
                  <v-chart :option="congestionChartOption" style="height: 400px" />
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>交通事件时间序列</span>
                  </template>
                  <v-chart :option="eventsChartOption" style="height: 400px" />
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 对比分析 -->
          <el-tab-pane label="道路对比分析" name="comparison">
            <div class="tab-controls">
              <el-form :inline="true" class="filter-form">
                <el-form-item label="选择道路" style="min-width: 400px;">
                  <el-select
                    v-model="selectedRoads"
                    multiple
                    placeholder="选择要对比的道路"
                    style="width: 300px"
                    class="road-select"
                    @change="loadComparisonData"
                  >
                    <el-option
                      v-for="road in availableRoads"
                      :key="road.id"
                      :label="road.name"
                      :value="road.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="对比指标">
                  <el-select
                    v-model="comparisonMetric"
                    placeholder="选择对比指标"
                    style="width: 160px"
                    @change="loadComparisonData"
                  >
                    <el-option label="拥堵指数" value="congestion" />
                    <el-option label="平均速度" value="speed" />
                  </el-select>
                </el-form-item>
              </el-form>
            </div>
            <el-row :gutter="20">
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>道路性能对比</span>
                  </template>
                  <div style="width: 100%; height: 400px;">
                    <v-chart 
                      ref="comparisonChartRef"
                      :option="comparisonChartOption" 
                      style="width: 100%; height: 100%;" 
                      autoresize
                    />
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 趋势分析 -->
          <el-tab-pane label="趋势分析" name="trend">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>周内流量规律</span>
                  </template>
                  <v-chart :option="weeklyTrendOption" style="height: 400px" autoresize />
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>月内流量趋势</span>
                  </template>
                  <v-chart :option="monthlyTrendOption" style="height: 400px" autoresize />
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 异常检测 -->
          <el-tab-pane label="异常检测" name="anomaly">
            <div class="tab-controls">
              <el-form :inline="true" class="filter-form">
                <el-form-item label="异常阈值 (标准差倍数)">
                  <div style="width: 300px; padding: 0 10px; display: inline-block; vertical-align: middle;">
                    <el-slider v-model="anomalyThreshold" :min="1" :max="5" :step="0.5" />
                  </div>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="performAnomalyDetection" :loading="loading">
                    <el-icon><Search /></el-icon>
                    检测异常
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
            <el-row>
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>异常数据列表 ({{ anomalies.length }}条)</span>
                  </template>
                  <el-table :data="anomalies" stripe style="width: 100%">
                    <el-table-column prop="road_name" label="道路名称" width="150" />
                    <el-table-column prop="timestamp" label="时间" width="180">
                      <template #default="{ row }">
                        {{ formatTime(row.timestamp) }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="congestion_index" label="拥堵指数" width="120" align="center" />
                    <el-table-column prop="speed" label="速度 (km/h)" width="120" align="center" />
                    <el-table-column prop="deviation" label="偏差" width="100" align="center">
                      <template #default="{ row }">
                        <el-tag type="danger">{{ row.deviation ? row.deviation.toFixed(2) : '--' }}</el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 事件分析 -->
          <el-tab-pane label="事件分析" name="event">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>事件类型分布</span>
                  </template>
                  <v-chart :option="eventTypeChartOption" style="height: 400px" autoresize />
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>事件严重程度统计</span>
                  </template>
                  <v-chart :option="eventSeverityChartOption" style="height: 400px" autoresize />
                </el-card>
              </el-col>
            </el-row>
            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>高影响事件</span>
                  </template>
                  <el-table :data="highImpactEvents" stripe style="width: 100%">
                    <el-table-column prop="road_name" label="道路名称" width="150" />
                    <el-table-column prop="event_type" label="事件类型" width="120" />
                    <el-table-column prop="severity" label="严重程度" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="impact_score" label="影响得分" width="100" align="center" />
                    <el-table-column prop="start_time" label="发生时间" width="180">
                      <template #default="{ row }">
                        {{ formatTime(row.start_time) }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" show-overflow-tooltip />
                  </el-table>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
console.log('[Analytics.vue] Script setup 执行开始')

import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  LineChart,
  BarChart,
  PieChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import {
  getCongestionTimeSeries,
  getEventsTimeSeries,
  compareRoads,
  getWeeklyTrends,
  getMonthlyTrends,
  detectAnomalies as detectAnomaliesAPI,
  getEventsStatistics,
  getHighImpactEvents,
  getDailySummary,
  getDateRange,
  getCurrentWeekRange,
  getCurrentMonthRange,
  formatDate,
  exportAnalyticsReport,
  downloadFile
} from '@/utils/analytics'
import api from '@/utils/api'
import {
  Sort,
  Refresh,
  Download,
  Search
} from '@element-plus/icons-vue'

// Use alternative icons for compatibility
const DataAnalysis = Sort

use([CanvasRenderer, LineChart, BarChart, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

// 数据状态
const loading = ref(false)
const dateRange = ref([])
const quickRange = ref('7')
const activeTab = ref('timeseries')

// 分析数据
const dailySummary = ref({})
const congestionData = ref([])
const eventsData = ref([])
const weeklyData = ref([])
const monthlyData = ref([])
const anomalies = ref([])
const eventStats = ref({})
const highImpactEvents = ref([])

// 对比分析
const selectedRoads = ref([])
const comparisonMetric = ref('congestion')
const comparisonData = ref([])
const availableRoads = ref([])
const comparisonChartRef = ref(null)

// 异常检测
const anomalyThreshold = ref(2)

// Theme management
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
  try {
    console.log('[Analytics] 页面初始化开始')
    
    // 加载道路列表
    loadRoads()
    
    // 初始化日期范围 (根据默认的 quickRange='7')
    updateDateRange()
    
    console.log('[Analytics] 页面初始化完成，日期范围:', dateRange.value)
  } catch (error) {
    console.error('[Analytics] 初始化失败:', error)
  }
})

onUnmounted(() => {
  window.removeEventListener('theme-change', updateTheme)
})

// 监听对比数据变化，强制重新渲染图表
watch(() => comparisonData.value, async (newVal) => {
  console.log('👁️ 检测到对比数据变化:', newVal.length, '条')
  if (newVal.length > 0 && comparisonChartRef.value) {
    await nextTick()
    console.log('🔄 触发图表重新渲染')
    comparisonChartRef.value.setOption(comparisonChartOption.value, true)
  }
}, { deep: false })

// 监听选中道路变化
watch(() => selectedRoads.value, async (newVal) => {
  console.log('🛣️ 选中的道路变化:', newVal)
  if (comparisonChartRef.value && comparisonData.value.length > 0) {
    await nextTick()
    comparisonChartRef.value.setOption(comparisonChartOption.value, true)
  }
}, { deep: false })

// 加载道路列表
const loadRoads = async () => {
  try {
    console.log('🔄 加载道路列表...')
    const response = await api.get('/roads', { params: { per_page: 100 } })
    console.log('📥 道路 API 响应:', response.data)
    availableRoads.value = response.data.roads || []
    console.log('✅ 加载到的道路数:', availableRoads.value.length)
    console.log('📋 道路列表:', availableRoads.value)
  } catch (error) {
    console.error('❌ 加载道路列表失败:', error.message)
    console.error('📋 错误详情:', error)
  }
}

// 更新日期范围
const updateDateRange = async () => {
  let start, end
  const now = new Date()
  
  if (quickRange.value === '7') {
    start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    end = new Date(now)
  } else if (quickRange.value === '30') {
    start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    end = new Date(now)
  } else if (quickRange.value === 'week') {
    const dayOfWeek = now.getDay()
    start = new Date(now.getTime() - dayOfWeek * 24 * 60 * 60 * 1000)
    end = new Date(start.getTime() + 7 * 24 * 60 * 60 * 1000)
  } else if (quickRange.value === 'month') {
    start = new Date(now.getFullYear(), now.getMonth(), 1)
    end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  }
  
  dateRange.value = [start, end]
  console.log(`📅 日期范围已更新: ${start.toLocaleDateString('zh-CN')} 到 ${end.toLocaleDateString('zh-CN')}`)
  
  // 注意：不需要显式调用 loadAllAnalytics，因为 watch(dateRange) 会自动触发它
}

// 加载所有分析数据
const loadAllAnalytics = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  try {
    const startDate = formatDate(dateRange.value[0])
    const endDate = formatDate(dateRange.value[1])
    
    console.log(`📅 加载分析数据: ${startDate} 到 ${endDate}`)

    // 并行加载所有数据
    const [summaryRes, congestionRes, eventsRes, weeklyRes, monthlyRes, eventStatsRes, highImpactRes] = await Promise.allSettled([
      getDailySummary(startDate),
      getCongestionTimeSeries(startDate, endDate, 'day'),
      getEventsTimeSeries(startDate, endDate, 'day'),
      getWeeklyTrends(startDate, endDate),
      getMonthlyTrends(startDate, endDate),
      getEventsStatistics(startDate, endDate),
      getHighImpactEvents(startDate, endDate)
    ])

    if (summaryRes.status === 'fulfilled') {
      dailySummary.value = summaryRes.value.data.summary || {}
      console.log('✅ 每日汇总:', dailySummary.value)
    } else {
      console.error('❌ 汇总失败:', summaryRes.reason)
    }
    
    if (congestionRes.status === 'fulfilled') {
      // 处理嵌套的数据结构
      let congestionArray = []
      if (congestionRes.value.data && Array.isArray(congestionRes.value.data.data)) {
        congestionArray = congestionRes.value.data.data
      } else if (congestionRes.value.data && Array.isArray(congestionRes.value.data)) {
        congestionArray = congestionRes.value.data
      }
      congestionData.value = congestionArray
      console.log('✅ 拥堵数据:', congestionData.value.length, '条')
    } else {
      console.error('❌ 拥堵数据失败:', congestionRes.reason)
    }
    
    if (eventsRes.status === 'fulfilled') {
      // 处理嵌套的数据结构
      let eventsArray = []
      if (eventsRes.value.data && Array.isArray(eventsRes.value.data.data)) {
        eventsArray = eventsRes.value.data.data
      } else if (eventsRes.value.data && Array.isArray(eventsRes.value.data)) {
        eventsArray = eventsRes.value.data
      }
      eventsData.value = eventsArray
      console.log('✅ 事件数据:', eventsData.value.length, '条')
      console.log('📊 事件数据详情:', eventsData.value)
    } else {
      console.error('❌ 事件数据失败:', eventsRes.reason)
    }
    
    if (weeklyRes.status === 'fulfilled') {
      console.log('📥 周趋势原始响应:', weeklyRes.value)
      // 处理嵌套的数据结构: response.data.data.data (Axios -> Flask Wrapper -> Inner Object -> Array)
      let weeklyArray = []
      const resData = weeklyRes.value.data
      
      if (resData && resData.data && Array.isArray(resData.data.data)) {
        // Case: { data: { data: [...] } }
        weeklyArray = resData.data.data
      } else if (resData && Array.isArray(resData.data)) {
        // Case: { data: [...] }
        weeklyArray = resData.data
      } else if (Array.isArray(resData)) {
        // Case: [...]
        weeklyArray = resData
      }
      
      weeklyData.value = weeklyArray
      console.log('✅ 周趋势数据:', weeklyData.value.length, '条')
      console.log('📊 周趋势数据详情:', weeklyData.value)
    } else {
      console.error('❌ 周趋势失败:', weeklyRes.reason)
    }
    
    if (monthlyRes.status === 'fulfilled') {
      console.log('📥 月趋势原始响应:', monthlyRes.value)
      // 处理嵌套的数据结构: response.data.data.data
      let monthlyArray = []
      const resData = monthlyRes.value.data
      
      if (resData && resData.data && Array.isArray(resData.data.data)) {
        // Case: { data: { data: [...] } }
        monthlyArray = resData.data.data
      } else if (resData && Array.isArray(resData.data)) {
        // Case: { data: [...] }
        monthlyArray = resData.data
      } else if (Array.isArray(resData)) {
        // Case: [...]
        monthlyArray = resData
      }
      
      monthlyData.value = monthlyArray
      console.log('✅ 月趋势数据:', monthlyData.value.length, '条')
      // 移除可能导致错误的日志
      // if (Array.isArray(monthlyData.value)) {
      //   console.log('📊 月趋势数据详情:', monthlyData.value.slice(0, 5))
      // }
    } else {
      console.error('❌ 月趋势失败:', monthlyRes.reason)
    }
    
    if (eventStatsRes.status === 'fulfilled') {
      eventStats.value = eventStatsRes.value.data.statistics || {}
      console.log('✅ 事件统计:', eventStats.value)
    } else {
      console.error('❌ 事件统计失败:', eventStatsRes.reason)
    }

    if (highImpactRes.status === 'fulfilled') {
      highImpactEvents.value = highImpactRes.value.data.events || []
      console.log('✅ 高影响事件:', highImpactEvents.value.length, '条')
    } else {
      console.error('❌ 高影响事件失败:', highImpactRes.reason)
    }

    // 保证各栏目数据一致性
    // 1. 如果有选中的道路，重新加载对比数据
    if (selectedRoads.value.length > 0) {
      loadComparisonData()
    }
    
    // 2. 处理异常检测数据一致性
    // 如果当前在异常检测标签页，自动刷新；否则清空旧数据以免误导
    if (activeTab.value === 'anomaly') {
      performAnomalyDetection()
    } else {
      anomalies.value = [] 
    }

    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载分析数据失败:', error)
    console.error('错误详情:', error.message, error.stack)
    ElMessage.error(`加载数据失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 加载对比数据
const loadComparisonData = async () => {
  if (selectedRoads.value.length === 0) {
    ElMessage.warning('请选择至少一条道路')
    return
  }

  loading.value = true
  try {
    const startDate = formatDate(dateRange.value[0])
    const endDate = formatDate(dateRange.value[1])
    
    // 确保 selectedRoads 是数字数组
    const roadIds = selectedRoads.value.map(r => typeof r === 'string' ? parseInt(r) : r)
    
    console.log(`🔄 加载道路对比数据: ${roadIds} - 指标: ${comparisonMetric.value}`)
    console.log(`📅 日期范围: ${startDate} 到 ${endDate}`)
    console.log(`🛣️  选中的道路 IDs:`, roadIds)
    console.log(`🛣️  道路类型:`, typeof roadIds[0], roadIds[0])
    
    const response = await compareRoads(roadIds, comparisonMetric.value, startDate, endDate)
    
    console.log('📥 对比 API 响应:', response.data)
    comparisonData.value = response.data.data || []
    
    console.log('✅ 对比数据加载成功:', comparisonData.value.length, '条')
    console.log('📊 对比数据详情:', comparisonData.value)
    
    // 验证数据结构
    if (comparisonData.value.length > 0) {
      console.log('📋 第一条数据:', comparisonData.value[0])
      console.log('🔍 数据字段检查:')
      console.log('  - timestamp:', comparisonData.value[0].timestamp)
      console.log('  - road_id:', comparisonData.value[0].road_id, '(类型:', typeof comparisonData.value[0].road_id + ')')
      console.log('  - avg_congestion:', comparisonData.value[0].avg_congestion)
      console.log('  - avg_speed:', comparisonData.value[0].avg_speed)
    }
    
    // 检查过滤是否有效
    console.log('🔎 过滤检查:')
    roadIds.forEach(roadId => {
      const filtered = comparisonData.value.filter(d => {
        const match = d.road_id === roadId
        if (!match) {
          console.log(`  比较: ${d.road_id} (${typeof d.road_id}) === ${roadId} (${typeof roadId}) => ${match}`)
        }
        return match
      })
      console.log(`  道路 ${roadId} 的数据条数: ${filtered.length}`)
    })
  } catch (error) {
    console.error('❌ 加载对比数据失败:', error.message)
    console.error('📋 错误详情:', error)
    ElMessage.error('加载对比数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 异常检测
const performAnomalyDetection = async () => {
  loading.value = true
  try {
    const startDate = formatDate(dateRange.value[0])
    const endDate = formatDate(dateRange.value[1])
    const response = await detectAnomaliesAPI(startDate, endDate, anomalyThreshold.value)
    anomalies.value = response.data.anomalies || []
    ElMessage.success(`检测到 ${anomalies.value.length} 条异常数据`)
  } catch (error) {
    console.error('异常检测失败:', error)
    ElMessage.error('异常检测失败')
  } finally {
    loading.value = false
  }
}

// 加载高影响事件
const loadHighImpactEvents = async () => {
  try {
    const startDate = formatDate(dateRange.value[0])
    const endDate = formatDate(dateRange.value[1])
    const response = await getHighImpactEvents(startDate, endDate)
    highImpactEvents.value = response.data.events || []
  } catch (error) {
    console.error('加载高影响事件失败:', error)
  }
}

// 导出报告
const exportAnalytics = async () => {
  try {
    const startDate = formatDate(dateRange.value[0])
    const endDate = formatDate(dateRange.value[1])
    const response = await exportAnalyticsReport(startDate, endDate)
    // 将JSON对象转换为Blob并下载
    const jsonBlob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
    downloadFile(jsonBlob, `分析报告_${startDate}_${endDate}.json`)
    ElMessage.success('报告导出成功')
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出报告失败')
  }
}

// 打印报表
const printReport = () => {
  window.print()
}

// 图表选项 - 拥堵指数时间序列
const congestionChartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#00f3ff' : '#007bff'
  const tooltipText = isDark ? '#fff' : '#212529'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const seriesColor = isDark ? '#00f3ff' : '#0d6efd'
  const areaStart = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(13, 110, 253, 0.3)'
  const areaEnd = isDark ? 'rgba(0, 243, 255, 0)' : 'rgba(13, 110, 253, 0)'

  return {
    backgroundColor: 'transparent',
    title: { text: '' },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText }
    },
    xAxis: {
      type: 'category',
      data: congestionData.value.map(d => d.timestamp?.split(' ')[0] || d.timestamp),
      axisLine: { lineStyle: { color: axisLine } },
      axisLabel: { color: axisLabel }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel }
    },
    series: [
      {
        data: congestionData.value.map(d => d.avg_congestion || 0),
        type: 'line',
        smooth: true,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: areaStart }, { offset: 1, color: areaEnd }]
          }
        },
        itemStyle: { color: seriesColor }
      }
    ]
  }
})

// 图表选项 - 交通事件时间序列
const eventsChartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#ffbd2e' : '#ffc107'
  const tooltipText = isDark ? '#fff' : '#212529'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const seriesColor = isDark ? '#ffbd2e' : '#ffc107'

  return {
    backgroundColor: 'transparent',
    title: { text: '' },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText }
    },
    xAxis: {
      type: 'category',
      data: eventsData.value.map(d => d.timestamp?.split(' ')[0] || d.timestamp),
      axisLine: { lineStyle: { color: axisLine } },
      axisLabel: { color: axisLabel }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel }
    },
    series: [
      {
        data: eventsData.value.map(d => d.count || 0),
        type: 'bar',
        itemStyle: { color: seriesColor }
      }
    ]
  }
})

// 图表选项 - 对比分析
const comparisonChartOption = computed(() => {
  console.log('🔄 重新计算对比图表选项')
  console.log('  - selectedRoads:', selectedRoads.value)
  console.log('  - comparisonData 条数:', comparisonData.value.length)
  console.log('  - comparisonMetric:', comparisonMetric.value)
  
  if (comparisonData.value.length === 0) {
    console.log('⚠️ 对比数据为空，返回空图表')
    return {
      title: { text: '无数据' },
      series: []
    }
  }
  
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#00f3ff' : '#007bff'
  const tooltipText = isDark ? '#fff' : '#212529'
  const legendBg = isDark ? 'rgba(0, 0, 0, 0.5)' : 'rgba(255, 255, 255, 0.8)'
  const legendBorder = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.1)'
  const legendText = isDark ? '#e0e0e0' : '#212529'
  const gridBorder = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'

  const xAxisData = [...new Set(comparisonData.value.map(d => d.timestamp?.split(' ')[0] || d.timestamp))].sort()
  console.log('  - X轴数据:', xAxisData)
  
  // 丰富的颜色调色板
  const colors = [
    '#409EFF', // 蓝色
    '#67C23A', // 绿色
    '#E6A23C', // 橙色
    '#F56C6C', // 红色
    '#909399', // 灰色
    '#85CE61', // 浅绿
    '#A6E3A1', // 薄荷绿
    '#FF7875', // 浅红
    '#FFC069', // 浅橙
    '#1890FF'  // 深蓝
  ]
  
  const seriesData = selectedRoads.value.map((roadId, index) => {
    const roadIdNum = typeof roadId === 'string' ? parseInt(roadId) : roadId
    const filtered = comparisonData.value.filter(d => d.road_id === roadIdNum)
    console.log(`  - 道路 ${roadIdNum}: ${filtered.length} 条数据`)
    
    const seriesValues = xAxisData.map(date => {
      const point = filtered.find(d => (d.timestamp?.split(' ')[0] || d.timestamp) === date)
      const value = point ? (comparisonMetric.value === 'congestion' ? point.avg_congestion : point.avg_speed) : null
      return value
    })
    
    console.log(`  - 道路 ${roadIdNum} 的值数组:`, seriesValues)
    
    const color = colors[index % colors.length]
    
    return {
      name: availableRoads.value.find(r => r.id === roadIdNum)?.name || `道路${roadIdNum}`,
      data: seriesValues,
      type: 'line',
      smooth: true,
      itemStyle: { color: color },
      lineStyle: { color: color, width: 2 },
      symbolSize: 5,
      symbol: 'circle'
    }
  })
  
  console.log('  - Series 数据:', seriesData)
  console.log('  - 完整图表配置:', {
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value' },
    series: seriesData
  })
  
  const option = {
    backgroundColor: 'transparent',
    title: { text: '' },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText },
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        const date = params[0].name
        let html = `<div>${date}<br/>`
        params.forEach(p => {
          html += `${p.seriesName}: ${p.value}<br/>`
        })
        html += '</div>'
        return html
      }
    },
    legend: { 
      data: selectedRoads.value.map((roadId, index) => {
        const id = typeof roadId === 'string' ? parseInt(roadId) : roadId
        return availableRoads.value.find(r => r.id === id)?.name || `道路${id}`
      }),
      orient: 'vertical',
      right: '2%',
      top: '8%',
      backgroundColor: legendBg,
      borderColor: legendBorder,
      borderWidth: 1,
      textStyle: { fontSize: 12, color: legendText }
    },
    grid: { left: 60, right: 200, top: 40, bottom: 60, containLabel: false, borderColor: gridBorder },
    xAxis: { 
      type: 'category', 
      data: xAxisData,
      boundaryGap: false,
      axisLine: { lineStyle: { color: axisLine } },
      axisLabel: { color: axisLabel }
    },
    yAxis: { 
      type: 'value',
      name: comparisonMetric.value === 'congestion' ? '拥堵指数' : '速度(km/h)',
      nameTextStyle: { fontSize: 12, color: axisLabel },
      splitLine: { lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel }
    },
    series: seriesData
  }
  
  console.log('✅ 最终图表配置已生成')
  return option
})

// 图表选项 - 周内趋势
const weeklyTrendOption = computed(() => {
  console.log('🔍 周内趋势计算 - weeklyData.value:', weeklyData.value)
  console.log('🔍 周内趋势计算 - 数组长度:', weeklyData.value.length)
  
  let seriesData = []
  if (Array.isArray(weeklyData.value) && weeklyData.value.length > 0) {
    console.log('🔍 周内趋势计算 - 第一条:', weeklyData.value[0])
    seriesData = weeklyData.value.slice(0, 7).map(d => d.avg_congestion || 0)
    console.log('🔍 周内趋势计算 - 数据值:', seriesData)
  }
  
  const xAxisData = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#00ff9d' : '#28a745'
  const tooltipText = isDark ? '#fff' : '#212529'
  const gridBorder = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const seriesColor = isDark ? '#00ff9d' : '#28a745'

  return {
    backgroundColor: 'transparent',
    color: [seriesColor],
    grid: {
      left: 50,
      right: 30,
      bottom: 30,
      top: 30,
      containLabel: true,
      borderColor: gridBorder
    },
    title: { 
      text: '',
      left: 'center',
      top: 0
    },
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText }
    },
    legend: { show: false },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisTick: { alignWithLabel: true },
      axisLine: { onZero: true, lineStyle: { color: axisLine } },
      axisLabel: { color: axisLabel },
      splitLine: { show: false }
    },
    yAxis: { 
      type: 'value',
      name: '拥堵指数',
      splitLine: { show: true, lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel },
      nameTextStyle: { color: axisLabel }
    },
    series: [
      {
        name: '拥堵指数',
        data: seriesData,
        type: 'bar',
        itemStyle: { 
          color: seriesColor
        },
        label: { show: false }
      }
    ]
  }
})

// 图表选项 - 月内趋势
const monthlyTrendOption = computed(() => {
  console.log('🔍 月内趋势计算 - monthlyData.value:', monthlyData.value)
  console.log('🔍 月内趋势计算 - 数组长度:', monthlyData.value.length)
  
  let xAxisData = []
  let seriesData = []
  
  if (Array.isArray(monthlyData.value) && monthlyData.value.length > 0) {
    console.log('🔍 月内趋势计算 - 第一条:', monthlyData.value[0])
    xAxisData = monthlyData.value.map(d => d.day || d.timestamp)
    seriesData = monthlyData.value.map(d => d.avg_congestion || 0)
    console.log('🔍 月内趋势计算 - X轴数据:', xAxisData)
    console.log('🔍 月内趋势计算 - Y轴数据:', seriesData)
  }
  
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#ff3860' : '#dc3545'
  const tooltipText = isDark ? '#fff' : '#212529'
  const gridBorder = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const seriesColor = isDark ? '#ff3860' : '#dc3545'
  const areaColor = isDark ? 'rgba(255, 56, 96, 0.2)' : 'rgba(220, 53, 69, 0.2)'

  return {
    backgroundColor: 'transparent',
    color: [seriesColor],
    grid: {
      left: 50,
      right: 30,
      bottom: 30,
      top: 30,
      containLabel: true,
      borderColor: gridBorder
    },
    title: { 
      text: '',
      left: 'center',
      top: 0
    },
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'line' },
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText }
    },
    legend: { show: false },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisTick: { alignWithLabel: true },
      axisLine: { onZero: true, lineStyle: { color: axisLine } },
      axisLabel: { color: axisLabel },
      splitLine: { show: false }
    },
    yAxis: { 
      type: 'value',
      name: '拥堵指数',
      splitLine: { show: true, lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel },
      nameTextStyle: { color: axisLabel }
    },
    series: [
      {
        name: '拥堵指数',
        data: seriesData,
        type: 'line',
        smooth: true,
        symbolSize: 6,
        itemStyle: { 
          color: seriesColor
        },
        areaStyle: {
          color: areaColor
        },
        label: { show: false }
      }
    ]
  }
})

// 图表选项 - 事件类型分布
const eventTypeChartOption = computed(() => ({
  title: { text: '' },
  tooltip: { trigger: 'item' },
  series: [
    {
      data: Object.entries(eventStats.value.by_type || {}).map(([name, value]) => ({
        name,
        value
      })),
      type: 'pie',
      radius: '50%'
    }
  ]
}))

// 图表选项 - 事件严重程度
const eventSeverityChartOption = computed(() => ({
  title: { text: '' },
  tooltip: { trigger: 'item' },
  series: [
    {
      data: Object.entries(eventStats.value.by_severity || {}).map(([name, value]) => ({
        name,
        value
      })),
      type: 'pie',
      radius: '50%'
    }
  ]
}))

// 辅助函数
const formatTime = (time) => {
  if (!time) return '--'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
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

const getSeverityType = (severity) => {
  const typeMap = {
    '低': 'info',
    '中': 'warning',
    '高': 'danger'
  }
  return typeMap[severity] || 'info'
}

// 监听快速选择变化
watch(quickRange, () => {
  updateDateRange()
})

// 监听日期范围直接变化（手动选择日期时）
watch(dateRange, async () => {
  if (dateRange.value && dateRange.value.length === 2) {
    console.log(`📅 日期范围手动变化: ${dateRange.value[0].toLocaleDateString('zh-CN')} 到 ${dateRange.value[1].toLocaleDateString('zh-CN')}`)
    await loadAllAnalytics()
  }
}, { deep: true })

</script>

<style scoped>
.analytics-container {
  padding: 20px;
  background: transparent;
  min-height: 100vh;
}

.header-row {
  margin-bottom: 20px;
}

.header-card {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 5px var(--primary-color-alpha);
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-container {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-primary);
}

.tab-controls {
  margin-bottom: 20px;
  padding: 15px;
  background: var(--bg-elevated);
  border-radius: 4px;
  border: 1px solid var(--border-primary);
}

:deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 30px;
}

:deep(.el-form-item__label) {
  color: var(--primary-color);
  font-weight: bold;
}

.button-group {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.summary-card {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  backdrop-filter: blur(10px);
}

.summary-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-secondary);
  color: var(--primary-color);
}

.summary-item {
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.3s;
}

.summary-item:hover {
  background: var(--bg-card-hover);
  transform: translateY(-2px);
}

.summary-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  text-shadow: 0 0 10px var(--primary-color-alpha);
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-secondary);
}

:deep(.el-tabs__item) {
  color: var(--text-secondary);
}

:deep(.el-tabs__item.is-active) {
  color: var(--primary-color);
  text-shadow: 0 0 5px var(--primary-color-alpha);
}

:deep(.el-tabs__item:hover) {
  color: var(--primary-color);
}

:deep(.el-card) {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  backdrop-filter: blur(10px);
  color: var(--text-primary);
}

:deep(.el-table) {
  background: transparent;
  color: var(--text-primary);
}

:deep(.el-table th) {
  background: var(--bg-elevated) !important;
  color: var(--primary-color);
  border-bottom: 1px solid var(--border-primary);
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--border-secondary);
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: var(--bg-elevated);
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background-color: var(--bg-card-hover);
}

/* 优化下拉框标签样式 */
.road-select :deep(.el-tag) {
  background-color: rgba(0, 243, 255, 0.1);
  border-color: rgba(0, 243, 255, 0.3);
  color: var(--primary-color);
}

.road-select :deep(.el-tag__close) {
  color: var(--primary-color);
}

.road-select :deep(.el-tag__close:hover) {
  background-color: var(--primary-color);
  color: #000;
}

@media print {
  .header-row, .filter-container, .el-button {
    display: none !important;
  }
  
  .analytics-container {
    padding: 0;
    background-color: white;
  }
  
  .el-card {
    box-shadow: none !important;
    border: none !important;
  }
  
  .summary-card {
    margin-top: 0 !important;
  }
  
  /* 确保图表在打印时可见 */
  .echarts {
    width: 100% !important;
    height: 300px !important;
  }
}
</style>
