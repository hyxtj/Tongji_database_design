<template>
  <div class="traffic-map-container" :style="{ height: height }" ref="containerRef">
    <div class="map-controls">
      <el-button circle type="info" @click="toggleFullScreen">
        <el-icon><FullScreen /></el-icon>
      </el-button>
    </div>
    
    <!-- Traffic Statistics Overlay -->
    <div class="map-stats" v-if="stats">
      <div class="stat-item">
        <span class="dot green"></span> 畅通: {{ stats.smooth }}
      </div>
      <div class="stat-item">
        <span class="dot yellow"></span> 缓行: {{ stats.slow }}
      </div>
      <div class="stat-item">
        <span class="dot orange"></span> 拥堵: {{ stats.congested }}
      </div>
      <div class="stat-item">
        <span class="dot red"></span> 严重: {{ stats.severe }}
      </div>
      <div class="last-updated">更新: {{ lastUpdated }}</div>
    </div>

    <div ref="chartRef" class="chart-container"></div>

    <el-dialog
      v-model="dialogVisible"
      title="道路详情"
      width="30%"
      :append-to-body="true"
    >
      <div v-if="selectedRoad" class="road-details">
        <p><strong>道路名称:</strong> {{ selectedRoad.name }}</p>
        <p><strong>当前状态:</strong> 
          <el-tag :type="getStatusType(selectedRoad.status)">{{ selectedRoad.status }}</el-tag>
        </p>
        <p><strong>拥堵指数:</strong> {{ selectedRoad.congestion }}</p>
        <p><strong>道路长度:</strong> {{ selectedRoad.value }} km</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '../utils/api'
import socket from '../utils/socket'
import { FullScreen } from '@element-plus/icons-vue'

const chartRef = ref(null)
const containerRef = ref(null)
let chartInstance = null
let timer = null

const dialogVisible = ref(false)
const selectedRoad = ref(null)
const stats = ref({ smooth: 0, slow: 0, congested: 0, severe: 0 })
const lastUpdated = ref('')

const props = defineProps({
  height: {
    type: String,
    default: '400px'
  }
})

const getStatusType = (status) => {
  const map = {
    '畅通': 'success',
    '缓行': 'warning',
    '拥堵': 'danger',
    '严重拥堵': 'danger'
  }
  return map[status] || 'info'
}

const getStatusColor = (status) => {
  const colors = {
    '畅通': '#00E676', // Green
    '缓行': '#FFC400', // Amber
    '拥堵': '#FF3D00', // Deep Orange
    '严重拥堵': '#D50000', // Red
    '未知': '#909399'   // Grey
  }
  return colors[status] || colors['未知']
}

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    containerRef.value.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value, 'dark')
    window.addEventListener('resize', resizeChart)
    
    chartInstance.on('click', (params) => {
      if (params.componentType === 'series' && params.seriesType === 'lines') {
        selectedRoad.value = params.data
        dialogVisible.value = true
      }
    })

    // Initialize with base options
    chartInstance.setOption({
      backgroundColor: 'transparent',
      title: {
        text: '实时路网状态 (Real-time Traffic GIS)',
        left: 'center',
        textStyle: { color: '#fff', fontSize: 16 }
      },
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderColor: '#333',
        textStyle: { color: '#fff' },
        formatter: (params) => {
          if (params.seriesType === 'lines') {
            const data = params.data
            return `
              <div style="font-weight:bold">${data.name}</div>
              <div>状态: <span style="color:${data.lineStyle.color}">${data.status}</span></div>
              <div>拥堵指数: ${data.congestion}</div>
              <div>长度: ${data.value} km</div>
              <div style="font-size:12px;color:#aaa;margin-top:4px">点击查看详情</div>
            `
          }
          return params.name
        }
      },
      legend: {
        bottom: 10,
        data: ['畅通', '缓行', '拥堵', '严重拥堵'],
        textStyle: { color: '#ccc' },
        selectedMode: false
      },
      dataZoom: [
        { type: 'inside', xAxisIndex: 0, filterMode: 'filter' },
        { type: 'inside', yAxisIndex: 0, filterMode: 'filter' }
      ],
      grid: {
        left: '2%', right: '2%', bottom: '10%', top: '10%', containLabel: false
      },
      xAxis: {
        type: 'value', scale: true, axisLabel: { show: false }, axisLine: { show: false }, splitLine: { show: false }, axisTick: { show: false }
      },
      yAxis: {
        type: 'value', scale: true, axisLabel: { show: false }, axisLine: { show: false }, splitLine: { show: false }, axisTick: { show: false }
      }
    })
  }
}

const resizeChart = () => {
  chartInstance?.resize()
}

const fetchAndRenderData = async () => {
  try {
    const response = await api.get('/roads', { params: { page: 1, per_page: 200 } })
    const roads = response.data.roads || []
    
    const linesData = []
    const scatterData = []
    
    // Reset stats
    const newStats = { smooth: 0, slow: 0, congested: 0, severe: 0 }

    roads.forEach(road => {
      if (road.coordinates && road.coordinates.start.lat && road.coordinates.end.lat) {
        const color = getStatusColor(road.current_status)
        
        // Update stats
        if (road.current_status === '畅通') newStats.smooth++
        else if (road.current_status === '缓行') newStats.slow++
        else if (road.current_status === '拥堵') newStats.congested++
        else if (road.current_status === '严重拥堵') newStats.severe++

        // Line data
        linesData.push({
          coords: [
            [road.coordinates.start.lng, road.coordinates.start.lat],
            [road.coordinates.end.lng, road.coordinates.end.lat]
          ],
          name: road.name,
          value: road.length,
          status: road.current_status,
          congestion: road.congestion_index,
          lineStyle: {
            color: color,
            shadowColor: color,
            shadowBlur: 10
          }
        })

        // Scatter data (Start point)
        scatterData.push({
          name: road.name,
          value: [road.coordinates.start.lng, road.coordinates.start.lat],
          itemStyle: {
            color: color,
            shadowColor: color,
            shadowBlur: 10
          }
        })
      }
    })

    // Update stats and time
    stats.value = newStats
    lastUpdated.value = new Date().toLocaleTimeString()

    // Calculate bounds
    let minLng = 180, maxLng = -180, minLat = 90, maxLat = -90
    linesData.forEach(item => {
      item.coords.forEach(coord => {
        minLng = Math.min(minLng, coord[0])
        maxLng = Math.max(maxLng, coord[0])
        minLat = Math.min(minLat, coord[1])
        maxLat = Math.max(maxLat, coord[1])
      })
    })
    
    const padding = 0.02
    minLng -= padding
    maxLng += padding
    minLat -= padding
    maxLat += padding

    // Only update series and axis range
    chartInstance.setOption({
      xAxis: { min: minLng, max: maxLng },
      yAxis: { min: minLat, max: maxLat },
      series: [
        {
          type: 'lines',
          coordinateSystem: 'cartesian2d',
          data: linesData,
          polyline: false,
          large: true,
          effect: {
            show: true,
            period: 4,
            trailLength: 0.1,
            symbol: 'arrow',
            symbolSize: 5
          },
          lineStyle: {
            width: 2,
            opacity: 0.8,
            curveness: 0.2
          },
          emphasis: {
            lineStyle: {
              width: 4,
              opacity: 1
            }
          }
        },
        {
          type: 'effectScatter',
          coordinateSystem: 'cartesian2d',
          data: scatterData,
          symbolSize: 6,
          showEffectOn: 'render',
          rippleEffect: {
            brushType: 'stroke',
            scale: 3
          },
          itemStyle: {
            opacity: 0.8
          },
          zlevel: 1
        },
        // Dummy series for legend
        ...['畅通', '缓行', '拥堵', '严重拥堵'].map(status => ({
          name: status,
          type: 'line',
          data: [],
          itemStyle: { color: getStatusColor(status) },
          lineStyle: { color: getStatusColor(status) }
        }))
      ]
    })
  } catch (error) {
    console.error('Failed to fetch map data:', error)
  }
}

onMounted(() => {
  initChart()
  fetchAndRenderData()
  
  // Connect to WebSocket
  socket.connect()
  
  // Listen for real-time updates
  socket.on('traffic_update', (data) => {
    console.log('Received real-time update:', data)
    fetchAndRenderData()
  })

  // Fallback: Refresh every 30 seconds just in case
  timer = setInterval(fetchAndRenderData, 30000)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
  if (timer) clearInterval(timer)
  
  socket.off('traffic_update')
  socket.disconnect()
})
</script>

<style scoped>
.traffic-map-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: radial-gradient(circle at center, #1a2a3a 0%, #0b1015 100%);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}
.chart-container {
  width: 100%;
  height: 100%;
}
.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
}
.map-stats {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.6);
  padding: 10px;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.stat-item {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
.dot.green { background-color: #00cc00; }
.dot.yellow { background-color: #ffcc00; }
.dot.orange { background-color: #ff6600; }
.dot.red { background-color: #cc0000; }
.last-updated {
  margin-top: 8px;
  color: #aaa;
  font-size: 11px;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 4px;
}
.road-details p {
  margin: 10px 0;
  font-size: 16px;
}
</style>
