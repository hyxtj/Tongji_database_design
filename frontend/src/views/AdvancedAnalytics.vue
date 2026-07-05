<template>
  <div class="advanced-analytics-container">
    <!-- 页面标题 -->
    <el-row :gutter="20" class="header-row">
      <el-col :span="24">
        <el-card class="header-card">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><DataAnalysis /></el-icon>
                高级分析
              </span>
              <el-button type="primary" @click="loadAllData" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新数据
              </el-button>
            </div>
          </template>

          <!-- 筛选工具栏 -->
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
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析标签页 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-tabs v-model="activeTab" type="card">
          <!-- 道路排名 -->
          <el-tab-pane label="道路排名" name="ranking">
            <div class="tab-controls">
              <el-form :inline="true" class="filter-form">
                <el-form-item label="排名指标">
                  <el-select v-model="rankingMetric" placeholder="选择排名指标" style="width: 160px" @change="loadRoadRanking">
                    <el-option label="拥堵指数" value="congestion" />
                    <el-option label="平均速度" value="speed" />
                  </el-select>
                </el-form-item>
                <el-form-item label="显示数量">
                  <div style="width: 200px; padding: 0 10px; display: inline-block; vertical-align: middle;">
                    <el-slider 
                      v-model="rankingLimit" 
                      :min="5" 
                      :max="20" 
                      :step="1" 
                      @change="loadRoadRanking"
                    />
                  </div>
                </el-form-item>
              </el-form>
            </div>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>
                      <el-icon><Trophy /></el-icon>
                      道路排名 ({{ rankingMetric === 'congestion' ? '拥堵' : '速度' }})
                    </span>
                  </template>
                  <el-table :data="roadRanking" stripe style="width: 100%" max-height="500">
                    <el-table-column label="排名" width="60" align="center">
                      <template #default="{ $index }">
                        <el-tag :type="$index === 0 ? 'danger' : $index === 1 ? 'warning' : 'info'">
                          {{ $index + 1 }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="road_name" label="道路名称" show-overflow-tooltip />
                    <el-table-column
                      :prop="rankingMetric === 'congestion' ? 'avg_congestion' : 'avg_speed'"
                      :label="rankingMetric === 'congestion' ? '平均拥堵指数' : '平均速度(km/h)'"
                      width="140"
                      align="center"
                    >
                      <template #default="{ row }">
                        {{ (rankingMetric === 'congestion' ? row.avg_congestion : row.avg_speed) ? (rankingMetric === 'congestion' ? row.avg_congestion : row.avg_speed).toFixed(2) : '--' }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="road_type" label="道路类型" width="100" />
                  </el-table>
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>排名分布图</span>
                  </template>
                  <v-chart :option="rankingChartOption" style="height: 450px" autoresize />
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 高峰时段分析 -->
          <el-tab-pane label="高峰时段分析" name="peakhours">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>
                      <el-icon><Clock /></el-icon>
                      小时级拥堵指数分布
                    </span>
                  </template>
                  <v-chart :option="peakHoursChartOption" style="height: 400px" autoresize />
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>高峰时段详情</span>
                  </template>
                  <el-table :data="peakHoursList" stripe style="width: 100%">
                    <el-table-column prop="hour" label="小时" width="80" align="center" />
                    <el-table-column prop="avg_congestion" label="平均拥堵指数" width="140" align="center">
                      <template #default="{ row }">
                        {{ row.avg_congestion != null ? row.avg_congestion.toFixed(2) : '--' }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="max_congestion" label="最高拥堵" width="120" align="center">
                      <template #default="{ row }">
                        {{ row.max_congestion != null ? row.max_congestion.toFixed(2) : '--' }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="avg_speed" label="平均速度(km/h)" width="140" align="center">
                      <template #default="{ row }">
                        {{ row.avg_speed != null ? row.avg_speed.toFixed(1) : '--' }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="min_speed" label="最低速度" width="120" align="center">
                      <template #default="{ row }">
                        {{ row.min_speed != null ? row.min_speed.toFixed(1) : '--' }}
                      </template>
                    </el-table-column>
                    <el-table-column label="拥堵等级" width="100" align="center">
                      <template #default="{ row }">
                        <el-tag :type="getCongestionTag(row.avg_congestion)">
                          {{ getCongestionLevel(row.avg_congestion) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="event_count" label="事件数" width="100" align="center" />
                    <el-table-column prop="record_count" label="样本量" width="100" align="center" />
                  </el-table>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 事件深度分析 -->
          <el-tab-pane label="事件深度分析" name="eventanalysis">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>高影响事件排名</span>
                  </template>
                  <el-table :data="highImpactEvents" stripe style="width: 100%" max-height="400">
                    <el-table-column prop="road_name" label="道路" width="120" show-overflow-tooltip />
                    <el-table-column prop="event_type" label="事件类型" width="100" />
                    <el-table-column prop="impact_score" label="影响得分" width="100" align="center">
                      <template #default="{ row }">
                        <el-tag type="danger">{{ row.impact_score ? row.impact_score.toFixed(1) : '--' }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="duration" label="持续时长(分)" width="110" align="center" />
                  </el-table>
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>事件多发地点</span>
                  </template>
                  <el-table :data="frequentLocations" stripe style="width: 100%" max-height="400">
                    <el-table-column prop="road_name" label="道路名称" show-overflow-tooltip />
                    <el-table-column prop="event_count" label="事件数" width="100" align="center">
                      <template #default="{ row }">
                        <el-tag type="warning">{{ row.event_count }}</el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>事件时间趋势</span>
                  </template>
                  <v-chart :option="eventTrendChartOption" style="height: 400px" autoresize />
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 数据质量检查 -->
          <el-tab-pane label="数据质量检查" name="quality">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>
                      <el-icon><SuccessFilled /></el-icon>
                      数据完整性
                    </span>
                  </template>

                  <div class="quality-item">
                    <div class="quality-label">完整性百分比</div>
                    <el-progress
                      :percentage="Math.round(dataQuality.completeness_percentage || 0)"
                      :color="dataQuality.completeness_percentage > 80 ? '#67C23A' : '#E6A23C'"
                    />
                  </div>

                  <div class="quality-item" style="margin-top: 20px">
                    <div class="quality-label">缺失记录数</div>
                    <div class="quality-value">{{ dataQuality.missing_records || 0 }}</div>
                  </div>

                  <div class="quality-item" style="margin-top: 20px">
                    <div class="quality-label">总记录数</div>
                    <div class="quality-value">{{ dataQuality.total_records || 0 }}</div>
                  </div>
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>
                      <el-icon><WarningFilled /></el-icon>
                      数据一致性
                    </span>
                  </template>

                  <div v-if="dataConsistency" class="consistency-items">
                    <div class="consistency-item">
                      <span class="label">孤立记录数:</span>
                      <el-tag :type="dataConsistency.orphan_records === 0 ? 'success' : 'warning'">
                        {{ dataConsistency.orphan_records || 0 }}
                      </el-tag>
                    </div>

                    <div class="consistency-item">
                      <span class="label">未来时间戳:</span>
                      <el-tag :type="dataConsistency.future_timestamps === 0 ? 'success' : 'warning'">
                        {{ dataConsistency.future_timestamps || 0 }}
                      </el-tag>
                    </div>

                    <div class="consistency-item">
                      <span class="label">异常关闭事件:</span>
                      <el-tag :type="dataConsistency.anomalous_closures === 0 ? 'success' : 'warning'">
                        {{ dataConsistency.anomalous_closures || 0 }}
                      </el-tag>
                    </div>

                    <div class="consistency-item">
                      <span class="label">一致性状态:</span>
                      <el-tag :type="dataConsistency.is_consistent ? 'success' : 'danger'">
                        {{ dataConsistency.is_consistent ? '正常' : '异常' }}
                      </el-tag>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>数据质量报告</span>
                  </template>
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="检查时间范围">
                      {{ dateRangeText }}
                    </el-descriptions-item>
                    <el-descriptions-item label="总体质量评分">
                      <el-rate
                        v-model="dataQualityScore"
                        disabled
                        show-score
                        text-color="#ff9900"
                        score-template="优秀"
                      />
                    </el-descriptions-item>
                    <el-descriptions-item label="完整性">
                      <el-tag :type="dataQuality.completeness_percentage > 80 ? 'success' : 'warning'">
                        {{ (dataQuality.completeness_percentage || 0).toFixed(2) }}%
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="一致性">
                      <el-tag :type="(dataConsistency && dataConsistency.is_consistent) ? 'success' : 'danger'">
                        {{ (dataConsistency && dataConsistency.is_consistent) ? '正常' : '异常' }}
                      </el-tag>
                    </el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 行政汇总 -->
          <el-tab-pane label="行政汇总报告" name="executive">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic title="日均拥堵指数" :value="executiveSummary.avg_congestion || 0" precision="2" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="日均速度(km/h)" :value="executiveSummary.avg_speed || 0" precision="1" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="总事件数" :value="executiveSummary.total_events || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="事件处理率" :value="(executiveSummary.event_resolution_rate || 0) * 100" suffix="%" precision="1" />
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>拥堵道路排名</span>
                  </template>
                  <el-table :data="executiveSummary.most_congested_roads || []" stripe style="width: 100%">
                    <el-table-column prop="road_name" label="道路名称" />
                    <el-table-column prop="avg_congestion" label="平均拥堵指数" width="140" align="center">
                      <template #default="{ row }">
                        {{ row.avg_congestion ? row.avg_congestion.toFixed(2) : '--' }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="congestion_percentage" label="拥堵率" width="100" align="center">
                      <template #default="{ row }">
                        {{ row.congestion_percentage ? (row.congestion_percentage * 100).toFixed(1) : '0.0' }}%
                      </template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card v-loading="loading">
                  <template #header>
                    <span>畅通道路排名</span>
                  </template>
                  <el-table :data="executiveSummary.smoothest_roads || []" stripe style="width: 100%">
                    <el-table-column prop="road_name" label="道路名称" />
                    <el-table-column prop="avg_speed" label="平均速度(km/h)" width="140" align="center">
                      <template #default="{ row }">
                        {{ row.avg_speed ? row.avg_speed.toFixed(1) : '--' }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="smooth_percentage" label="畅通率" width="100" align="center">
                      <template #default="{ row }">
                        {{ row.smooth_percentage ? (row.smooth_percentage * 100).toFixed(1) : '0.0' }}%
                      </template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="24">
                <el-card v-loading="loading">
                  <template #header>
                    <span>关键建议</span>
                  </template>
                  <template v-if="executiveSummary.recommendations && executiveSummary.recommendations.length > 0">
                    <el-alert
                      v-for="(rec, index) in executiveSummary.recommendations"
                      :key="index"
                      :title="rec"
                      type="info"
                      :closable="false"
                      style="margin-bottom: 10px"
                    />
                  </template>
                  <el-empty v-else description="暂无建议" />
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
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import {
  getRoadRanking,
  getPeakHoursAnalysis,
  getHighImpactEvents,
  getFrequentEventLocations,
  getEventTrend,
  checkDataCompleteness,
  checkDataConsistency,
  getExecutiveSummary,
  getDateRange,
  getCurrentWeekRange,
  getCurrentMonthRange,
  formatDate
} from '@/utils/analytics'
import { DataAnalysis, Refresh, Trophy, Clock, SuccessFilled, WarningFilled } from '@element-plus/icons-vue'

use([CanvasRenderer, LineChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

// 数据状态
const loading = ref(false)
const dateRange = ref([])
const quickRange = ref('7')
const activeTab = ref('ranking')

// 分析数据
const roadRanking = ref([])
const rankingMetric = ref('congestion')
const rankingLimit = ref(10)

const peakHoursList = ref([])
const highImpactEvents = ref([])
const frequentLocations = ref([])
const eventTrendData = ref([])

const dataQuality = ref({})
const dataConsistency = ref({})
const dataQualityScore = ref(5)

const executiveSummary = ref({})

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
  updateDateRange()
  loadAllData()
})

onUnmounted(() => {
  window.removeEventListener('theme-change', updateTheme)
})

// 更新日期范围
const updateDateRange = () => {
  let start, end
  if (quickRange.value === '7') {
    const range = getDateRange(7)
    start = new Date(range.startDate)
    end = new Date(range.endDate)
  } else if (quickRange.value === '30') {
    const range = getDateRange(30)
    start = new Date(range.startDate)
    end = new Date(range.endDate)
  } else if (quickRange.value === 'week') {
    const range = getCurrentWeekRange()
    start = new Date(range.startDate)
    end = new Date(range.endDate)
  } else if (quickRange.value === 'month') {
    const range = getCurrentMonthRange()
    start = new Date(range.startDate)
    end = new Date(range.endDate)
  }
  dateRange.value = [start, end]
}

// 加载所有数据
const loadAllData = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  try {
    const startDate = formatDate(dateRange.value[0])
    const endDate = formatDate(dateRange.value[1])

    const promises = [
      getRoadRanking(rankingMetric.value, startDate, endDate, rankingLimit.value),
      getPeakHoursAnalysis(startDate, endDate),
      getHighImpactEvents(startDate, endDate),
      getFrequentEventLocations(startDate, endDate),
      getEventTrend(startDate, endDate),
      checkDataCompleteness(startDate, endDate),
      checkDataConsistency(startDate, endDate),
      getExecutiveSummary(startDate, endDate)
    ]

    const results = await Promise.allSettled(promises)

    if (results[0].status === 'fulfilled') roadRanking.value = results[0].value.data.roads || []
    if (results[1].status === 'fulfilled') peakHoursList.value = results[1].value.data.data || []
    
    // 处理高影响事件数据 (兼容后端嵌套结构和Mock扁平结构)
    if (results[2].status === 'fulfilled') {
      const events = results[2].value.data.events || []
      highImpactEvents.value = events.map(item => {
        const eventData = item.event || item
        return {
          road_name: eventData.road_name || '未知道路',
          event_type: eventData.event_type,
          impact_score: item.impact_score || eventData.impact_score,
          duration: calculateDuration(eventData.start_time, eventData.end_time)
        }
      })
    }

    // 处理事件多发地点数据
    if (results[3].status === 'fulfilled') {
      const locations = results[3].value.data.locations || []
      frequentLocations.value = locations.map(item => ({
        road_name: item.road ? item.road.name : (item.road_name || '未知道路'),
        event_count: item.event_count
      }))
    }

    // 处理事件趋势数据
    if (results[4].status === 'fulfilled') eventTrendData.value = results[4].value.data.data || []
    if (results[5].status === 'fulfilled') dataQuality.value = results[5].value.data.quality || {}
    if (results[6].status === 'fulfilled') dataConsistency.value = results[6].value.data.consistency || {}
    if (results[7].status === 'fulfilled') executiveSummary.value = results[7].value.data.summary || {}

    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载道路排名
const loadRoadRanking = async () => {
  const startDate = formatDate(dateRange.value[0])
  const endDate = formatDate(dateRange.value[1])
  try {
    const response = await getRoadRanking(rankingMetric.value, startDate, endDate, rankingLimit.value)
    roadRanking.value = response.data.roads || []
  } catch (error) {
    ElMessage.error('加载道路排名失败')
  }
}

// 辅助函数
const getCongestionLevel = (value) => {
  if (value < 2) return '畅通'
  if (value < 5) return '缓行'
  if (value < 8) return '拥堵'
  return '严重拥堵'
}

const getCongestionTag = (value) => {
  if (value < 2) return 'success'
  if (value < 5) return 'warning'
  return 'danger'
}

// 计算日期范围文本
const dateRangeText = computed(() => {
  if (!dateRange.value || dateRange.value.length !== 2) return '--'
  return `${formatDate(dateRange.value[0])} 至 ${formatDate(dateRange.value[1])}`
})

// 图表选项 - 排名
const rankingChartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#00f3ff' : '#007bff'
  const tooltipText = isDark ? '#fff' : '#212529'
  const gridBorder = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const barColorStart = isDark ? '#00f3ff' : '#0d6efd'
  const barColorEnd = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(13, 110, 253, 0.1)'

  return {
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText }
    },
    grid: {
      containLabel: true,
      borderColor: gridBorder
    },
    xAxis: {
      type: 'category',
      data: roadRanking.value.map(r => r.road_name),
      axisLabel: { interval: 0, rotate: 30, color: axisLabel },
      axisLine: { lineStyle: { color: axisLine } }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel }
    },
    series: [
      {
        data: roadRanking.value.map(r => rankingMetric.value === 'congestion' ? r.avg_congestion : r.avg_speed),
        type: 'bar',
        itemStyle: { 
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: barColorStart },
              { offset: 1, color: barColorEnd }
            ]
          }
        }
      }
    ]
  }
})

// 图表选项 - 高峰时段
const peakHoursChartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#ff3860' : '#dc3545'
  const tooltipText = isDark ? '#fff' : '#212529'
  const gridBorder = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const lineColor = isDark ? '#ff3860' : '#dc3545'
  const areaStart = isDark ? 'rgba(255, 56, 96, 0.5)' : 'rgba(220, 53, 69, 0.5)'
  const areaEnd = isDark ? 'rgba(255, 56, 96, 0.0)' : 'rgba(220, 53, 69, 0.0)'

  return {
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText }
    },
    grid: {
      containLabel: true,
      borderColor: gridBorder
    },
    xAxis: {
      type: 'category',
      data: peakHoursList.value.map(p => `${p.hour}:00`),
      axisLabel: { color: axisLabel },
      axisLine: { lineStyle: { color: axisLine } }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel }
    },
    series: [
      {
        data: peakHoursList.value.map(p => p.avg_congestion),
        type: 'line',
        smooth: true,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: areaStart },
              { offset: 1, color: areaEnd }
            ]
          }
        },
        itemStyle: { color: lineColor }
      }
    ]
  }
})

// 图表选项 - 事件趋势
const eventTrendChartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#bc13fe' : '#6f42c1'
  const tooltipText = isDark ? '#fff' : '#212529'
  const gridBorder = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const barColorStart = isDark ? '#bc13fe' : '#6f42c1'
  const barColorEnd = isDark ? 'rgba(188, 19, 254, 0.1)' : 'rgba(111, 66, 193, 0.1)'

  return {
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: tooltipText }
    },
    grid: {
      containLabel: true,
      borderColor: gridBorder
    },
    xAxis: {
      type: 'category',
      data: eventTrendData.value.map(e => e.date),
      axisLabel: { color: axisLabel },
      axisLine: { lineStyle: { color: axisLine } }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: splitLine } },
      axisLabel: { color: axisLabel }
    },
    series: [
      {
        data: eventTrendData.value.map(e => e.total_events || e.count || 0),
        type: 'bar',
        itemStyle: { 
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: barColorStart },
              { offset: 1, color: barColorEnd }
            ]
          }
        }
      }
    ]
  }
})

// 计算持续时间(分钟)
const calculateDuration = (start, end) => {
  if (!start) return 0
  const startTime = new Date(start)
  const endTime = end ? new Date(end) : new Date()
  return Math.floor((endTime - startTime) / (1000 * 60))
}

// 监听快速选择变化
watch(quickRange, () => {
  updateDateRange()
  loadAllData()
})
</script>

<style scoped>
.advanced-analytics-container {
  padding: 20px;
  min-height: 100vh;
  background-color: var(--bg-color);
  color: var(--text-primary);
}

.header-row {
  margin-bottom: 20px;
}

.header-card {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  box-shadow: var(--box-shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
  text-shadow: var(--text-shadow);
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quality-item {
  padding: 15px 0;
  border-bottom: 1px solid var(--border-color);
}

.quality-item:last-child {
  border-bottom: none;
}

.quality-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.quality-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  text-shadow: var(--text-shadow);
}

.consistency-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.consistency-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.consistency-item .label {
  font-weight: 500;
  color: var(--text-primary);
}

:deep(.el-card) {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  box-shadow: var(--box-shadow);
  color: var(--text-primary);
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

/* 标签页样式 */
:deep(.el-tabs__header) {
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-tabs__item) {
  color: var(--text-secondary);
}

:deep(.el-tabs__item.is-active) {
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__nav) {
  border: 1px solid var(--border-color);
  border-bottom: none;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item) {
  border-left: 1px solid var(--border-color);
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item.is-active) {
  background: var(--bg-hover);
  border-bottom-color: transparent;
}

/* 表格样式 */
:deep(.el-table) {
  background-color: transparent !important;
  color: var(--text-primary);
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: var(--bg-hover);
  --el-table-row-hover-bg-color: var(--bg-hover) !important;
  --el-table-tr-bg-color: transparent;
}

:deep(.el-table th),
:deep(.el-table tr),
:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table__inner-wrapper::before) {
  background-color: var(--border-color);
}

/* 统计数值样式 */
:deep(.el-statistic) {
  --el-statistic-content-color: var(--text-primary);
  --el-statistic-title-color: var(--text-secondary);
}

:deep(.el-statistic__content) {
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
}

/* 描述列表样式 */
:deep(.el-descriptions) {
  --el-descriptions-table-border: 1px solid var(--border-color);
  --el-descriptions-item-bordered-label-background: var(--bg-hover);
}

:deep(.el-descriptions__body) {
  background: transparent;
  color: var(--text-primary);
}

:deep(.el-descriptions__label) {
  color: var(--primary-color);
}

/* 输入框和选择器样式 */
:deep(.el-input__wrapper),
:deep(.el-select__wrapper),
:deep(.el-range-editor.el-input__wrapper) {
  background-color: var(--bg-input);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

:deep(.el-input__inner),
:deep(.el-range-input) {
  color: var(--text-primary);
}

/* 警告框样式 */
:deep(.el-alert--info) {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.filter-container {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.tab-controls {
  margin-bottom: 20px;
  padding: 15px;
  background: var(--bg-hover);
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

:deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 30px;
}

:deep(.el-form-item__label) {
  color: var(--text-primary);
  font-weight: bold;
}
</style>
