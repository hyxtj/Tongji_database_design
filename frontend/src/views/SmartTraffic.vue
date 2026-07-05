<template>
  <div class="smart-traffic-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>智能交通中心</span>
          <el-button type="primary" @click="refreshData">刷新数据</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="demo-tabs">
        <!-- 天气监控 -->
        <el-tab-pane label="实时天气监控" name="weather">
          <div class="weather-grid">
            <el-card v-for="item in weatherList" :key="item.id" class="weather-card" shadow="hover">
              <template #header>
                <div class="weather-header">
                  <span>{{ item.city }} - {{ item.road_name || '全区' }}</span>
                </div>
              </template>
              <div class="weather-content">
                <div class="weather-main">
                  <div class="weather-temp">
                    <el-icon :size="28" class="weather-icon-large">
                      <component :is="getWeatherIcon(item.condition)" />
                    </el-icon>
                    <span class="temp-value">{{ formatNumber(item.temperature, 1) }}°C</span>
                  </div>
                  <el-tag :type="getWeatherTagType(item.condition)" effect="plain" round>{{ getWeatherLabel(item.condition) }}</el-tag>
                </div>
                
                <div class="weather-details">
                  <div class="detail-item">
                    <div class="detail-icon"><el-icon><View /></el-icon></div>
                    <div class="detail-info">
                      <span class="detail-label">能见度</span>
                      <span class="detail-value">{{ formatNumber(item.visibility / 1000, 1) }} km</span>
                    </div>
                  </div>
                  <div class="detail-item">
                    <div class="detail-icon"><el-icon><Pouring /></el-icon></div>
                    <div class="detail-info">
                      <span class="detail-label">降水</span>
                      <span class="detail-value">{{ formatNumber(item.precipitation, 1) }} mm</span>
                    </div>
                  </div>
                  <div class="detail-item">
                    <div class="detail-icon"><el-icon><WindPower /></el-icon></div>
                    <div class="detail-info">
                      <span class="detail-label">风速</span>
                      <span class="detail-value">{{ formatNumber(item.wind_speed, 1) }} km/h</span>
                    </div>
                  </div>
                </div>

                <div class="weather-time">
                  更新于 {{ formatDate(item.timestamp) }}
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 交通预测 -->
        <el-tab-pane label="AI 交通预测" name="prediction">
          <div class="prediction-container">
            <div class="chart-controls">
              <el-select v-model="selectedRoadId" placeholder="选择道路" @change="fetchPredictions">
                <el-option
                  v-for="road in roads"
                  :key="road.id"
                  :label="road.name"
                  :value="road.id"
                />
              </el-select>
            </div>
            <div ref="chartRef" class="chart-container"></div>
          </div>
        </el-tab-pane>

        <!-- 维护计划 -->
        <el-tab-pane label="道路维护计划" name="maintenance">
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in maintenanceList"
              :key="index"
              :timestamp="formatDateRange(activity.start_time, activity.end_time)"
              :type="getMaintenanceType(activity.status)"
              placement="top"
            >
              <el-card>
                <h4>{{ activity.road_name }} - {{ activity.maintenance_type }}</h4>
                <p>{{ activity.description }}</p>
                <div class="maintenance-footer">
                  <el-tag size="small" :type="getImpactTagType(activity.impact_level)">
                    影响等级: {{ activity.impact_level }}
                  </el-tag>
                  <el-tag size="small" :type="getStatusTagType(activity.status)" style="margin-left: 10px;">
                    状态: {{ activity.status }}
                  </el-tag>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import api from '@/utils/api'
import * as echarts from 'echarts'
import { Sunny, View, Pouring, WindPower, Cloudy, Lightning } from '@element-plus/icons-vue'

const activeTab = ref('weather')
const weatherList = ref([])
const maintenanceList = ref([])
const predictions = ref([])
const roads = ref([])
const selectedRoadId = ref(null)
const chartRef = ref(null)
let chartInstance = null

// Theme management
const currentTheme = ref(document.documentElement.getAttribute('data-theme') || 'dark')

const updateTheme = () => {
  currentTheme.value = document.documentElement.getAttribute('data-theme') || 'dark'
  if (chartInstance) {
    updateChart()
  }
}

onMounted(() => {
  window.addEventListener('theme-change', updateTheme)
  window.addEventListener('storage', (e) => {
    if (e.key === 'theme') {
      updateTheme()
    }
  })
  fetchWeather()
  fetchMaintenance()
  fetchRoads()
  
  window.addEventListener('resize', () => {
    chartInstance && chartInstance.resize()
  })
})

onUnmounted(() => {
  window.removeEventListener('theme-change', updateTheme)
})

// 获取天气数据
const fetchWeather = async () => {
  try {
    const res = await api.get('/smart/weather')
    weatherList.value = res.data
  } catch (error) {
    console.error('Failed to fetch weather:', error)
  }
}

// 获取维护数据
const fetchMaintenance = async () => {
  try {
    const res = await api.get('/smart/maintenance')
    maintenanceList.value = res.data
  } catch (error) {
    console.error('Failed to fetch maintenance:', error)
  }
}

// 获取道路列表（用于下拉选择）
const fetchRoads = async () => {
  try {
    const res = await api.get('/roads')
    roads.value = res.data.roads || []
    if (roads.value.length > 0) {
      selectedRoadId.value = roads.value[0].id
      fetchPredictions()
    }
  } catch (error) {
    console.error('Failed to fetch roads:', error)
  }
}

// 获取预测数据
const fetchPredictions = async () => {
  if (!selectedRoadId.value) return
  try {
    const res = await api.get(`/smart/predictions?road_id=${selectedRoadId.value}`)
    predictions.value = res.data
    updateChart()
  } catch (error) {
    console.error('Failed to fetch predictions:', error)
  }
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const isDark = currentTheme.value === 'dark'
  const textColor = isDark ? '#fff' : '#212529'
  const axisLineColor = isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.1)'
  const splitLineColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#333' : '#ccc'

  // 优化时间显示格式为 HH:mm
  const times = predictions.value.map(p => {
    const date = new Date(p.predicted_time)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  })
  const speeds = predictions.value.map(p => p.predicted_speed)
  const congestions = predictions.value.map(p => p.congestion_level)

  const option = {
    backgroundColor: 'transparent',
    title: { 
      text: '未来24小时交通预测',
      textStyle: { color: textColor }
    },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: { color: textColor }
    },
    legend: { 
      data: ['预测速度 (km/h)', '拥堵指数'],
      textStyle: { color: textColor }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: { 
      type: 'category', 
      data: times,
      axisLabel: { 
        color: textColor,
        rotate: 45, // 旋转标签防止重叠
        interval: 'auto' 
      },
      axisLine: { lineStyle: { color: axisLineColor } }
    },
    yAxis: [
      { 
        type: 'value', 
        name: '速度', 
        min: 0, 
        max: 120,
        nameTextStyle: { color: textColor },
        axisLabel: { color: textColor },
        splitLine: { lineStyle: { color: splitLineColor } }
      },
      { 
        type: 'value', 
        name: '拥堵指数', 
        min: 0, 
        max: 10,
        nameTextStyle: { color: textColor },
        axisLabel: { color: textColor },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '预测速度 (km/h)',
        type: 'line',
        data: speeds,
        smooth: true,
        areaStyle: { opacity: 0.1 },
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '拥堵指数',
        type: 'line',
        yAxisIndex: 1,
        data: congestions,
        smooth: true,
        itemStyle: { color: '#F56C6C' }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 辅助函数
const getWeatherIcon = (condition) => {
  const map = {
    'Sunny': Sunny,
    'Rainy': Pouring,
    'Foggy': Cloudy,
    'Snowy': Lightning, // 暂用 Lightning 代替下雪
    'Cloudy': Cloudy
  }
  return map[condition] || Sunny
}

const getWeatherTagType = (condition) => {
  const map = { 
    'Sunny': 'success', 
    'Rainy': 'primary', 
    'Foggy': 'warning', 
    'Snowy': 'info',
    'Cloudy': 'info'
  }
  return map[condition] || 'info'
}

const getWeatherLabel = (condition) => {
  const map = { 
    'Sunny': '晴朗', 
    'Rainy': '下雨', 
    'Foggy': '雾天', 
    'Snowy': '下雪',
    'Cloudy': '多云'
  }
  return map[condition] || condition
}

const getMaintenanceType = (status) => {
  return status === 'In Progress' ? 'primary' : 'info'
}

const getImpactTagType = (level) => {
  const map = { 'High': 'danger', 'Medium': 'warning', 'Low': 'info' }
  return map[level] || 'info'
}

const getStatusTagType = (status) => {
  const map = { 'Scheduled': 'info', 'In Progress': 'primary', 'Completed': 'success' }
  return map[status] || 'info'
}

const formatDate = (isoString) => {
  return new Date(isoString).toLocaleString()
}

const formatDateRange = (start, end) => {
  return `${new Date(start).toLocaleDateString()} - ${new Date(end).toLocaleDateString()}`
}

const formatNumber = (num, decimals = 1) => {
  if (num === null || num === undefined) return '-'
  return Number(num).toFixed(decimals)
}

const refreshData = () => {
  fetchWeather()
  fetchMaintenance()
  if (selectedRoadId.value) fetchPredictions()
}

// 监听 Tab 切换，如果是预测 Tab 且图表未初始化，则初始化
watch(activeTab, (newVal) => {
  if (newVal === 'prediction') {
    nextTick(() => {
      // 关键修复：Tab切换可见时，必须重置图表尺寸
      if (chartInstance) {
        chartInstance.resize()
      }
      
      if (selectedRoadId.value) {
        fetchPredictions()
      } else {
        fetchRoads()
      }
    })
  }
})
</script>

<style scoped>
.smart-traffic-container {
  padding: 20px;
  background-color: var(--bg-color);
  min-height: 100vh;
}
.prediction-container {
  width: 100%; /* 确保容器占满宽度 */
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.weather-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.weather-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.weather-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}
.weather-temp {
  display: flex;
  align-items: center;
  gap: 12px;
}
.weather-icon-large {
  color: #e6a23c; /* Sunny color */
}
.temp-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
}
.weather-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 5px;
  padding: 8px;
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}
.detail-icon {
  color: var(--text-secondary);
  font-size: 16px;
}
.detail-info {
  display: flex;
  flex-direction: column;
}
.detail-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}
.detail-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.weather-time {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
  margin-top: 5px;
}
.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}
.chart-controls {
  margin-bottom: 20px;
}
.maintenance-footer {
  margin-top: 10px;
}

:deep(.el-card) {
  background-color: var(--bg-card);
  border-color: var(--border-color);
  color: var(--text-primary);
}

:deep(.el-card__header) {
  border-bottom-color: var(--border-color);
}

:deep(.el-tabs__item) {
  color: var(--text-secondary);
}

:deep(.el-tabs__item.is-active) {
  color: var(--primary-color);
}

:deep(.el-timeline-item__content) {
  color: var(--text-primary);
}

:deep(.el-timeline-item__timestamp) {
  color: var(--text-secondary);
}
</style>
