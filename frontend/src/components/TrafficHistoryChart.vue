<template>
  <v-chart
    v-if="data.length > 0"
    :option="chartOption"
    style="height: 400px; margin-top: 20px;"
    autoresize
  />
  <el-empty v-else description="请选择道路查询历史数据" />
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  }
})

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
})

onUnmounted(() => {
  window.removeEventListener('theme-change', updateTheme)
})

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

const chartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  
  // Theme colors
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#00f3ff' : '#007bff'
  const tooltipText = isDark ? '#fff' : '#212529'
  const legendText = isDark ? '#e0e0e0' : '#212529'
  const gridBorder = isDark ? 'rgba(0, 243, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
  const axisLabel = isDark ? '#a0a0a0' : '#6c757d'
  const splitLine = isDark ? 'rgba(0, 243, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const yAxis1Line = isDark ? '#ff0055' : '#dc3545'
  const yAxis2Line = isDark ? '#00f3ff' : '#0d6efd'
  const series1Color = isDark ? '#ff0055' : '#dc3545'
  const series2Color = isDark ? '#00f3ff' : '#0d6efd'
  const series1AreaStart = isDark ? 'rgba(255, 0, 85, 0.3)' : 'rgba(220, 53, 69, 0.3)'
  const series1AreaEnd = isDark ? 'rgba(255, 0, 85, 0)' : 'rgba(220, 53, 69, 0)'
  const series2AreaStart = isDark ? 'rgba(0, 243, 255, 0.3)' : 'rgba(13, 110, 253, 0.3)'
  const series2AreaEnd = isDark ? 'rgba(0, 243, 255, 0)' : 'rgba(13, 110, 253, 0)'

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: {
        color: tooltipText
      }
    },
    legend: {
      data: ['拥堵指数', '平均速度'],
      textStyle: {
        color: legendText
      }
    },
    grid: {
      containLabel: true,
      borderColor: gridBorder
    },
    xAxis: {
      type: 'category',
      data: props.data.map(item => formatTime(item.timestamp)),
      axisLine: {
        lineStyle: {
          color: axisLine
        }
      },
      axisLabel: {
        color: axisLabel
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '拥堵指数',
        max: 10,
        splitLine: {
          lineStyle: {
            color: splitLine
          }
        },
        axisLine: {
          lineStyle: {
            color: yAxis1Line
          }
        },
        axisLabel: {
          color: axisLabel
        },
        nameTextStyle: {
          color: axisLabel
        }
      },
      {
        type: 'value',
        name: '速度(km/h)',
        splitLine: {
          show: false
        },
        axisLine: {
          lineStyle: {
            color: yAxis2Line
          }
        },
        axisLabel: {
          color: axisLabel
        },
        nameTextStyle: {
          color: axisLabel
        }
      }
    ],
    series: [
      {
        name: '拥堵指数',
        type: 'line',
        data: props.data.map(item => item.congestion_index),
        itemStyle: {
          color: series1Color
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
                offset: 0, color: series1AreaStart
            }, {
                offset: 1, color: series1AreaEnd
            }]
          }
        }
      },
      {
        name: '平均速度',
        type: 'line',
        yAxisIndex: 1,
        data: props.data.map(item => item.speed),
        itemStyle: {
          color: series2Color
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
                offset: 0, color: series2AreaStart
            }, {
                offset: 1, color: series2AreaEnd
            }]
          }
        }
      }
    ]
  }
})
</script>
