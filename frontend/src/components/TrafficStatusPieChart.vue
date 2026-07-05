<template>
  <div style="width: 100%; height: 300px;">
    <v-chart
      :option="chartOption"
      style="width: 100%; height: 100%;"
      autoresize
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
])

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const currentTheme = ref(document.documentElement.getAttribute('data-theme') || 'dark')

const updateTheme = () => {
  currentTheme.value = document.documentElement.getAttribute('data-theme') || 'dark'
}

onMounted(() => {
  window.addEventListener('theme-change', updateTheme)
  // Also listen for storage events in case theme changes in another tab
  window.addEventListener('storage', (e) => {
    if (e.key === 'theme') {
      updateTheme()
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('theme-change', updateTheme)
})

const chartOption = computed(() => {
  const isDark = currentTheme.value === 'dark'
  const distribution = props.data || {}
  const distributionData = Object.entries(distribution).map(([name, value]) => ({ 
    name, 
    value: Number(value) 
  }))
  
  if (distributionData.length === 0) {
    return { 
      backgroundColor: 'transparent',
      series: [] 
    }
  }
  
  // Theme colors
  const textColor = isDark ? '#e0e0e0' : '#212529'
  const tooltipBg = isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.9)'
  const tooltipBorder = isDark ? '#00f3ff' : '#007bff'
  const tooltipText = isDark ? '#fff' : '#212529'
  const borderColor = isDark ? '#050508' : '#ffffff'
  const emphasisLabelColor = isDark ? '#fff' : '#000'
  const shadowColor = isDark ? 'rgba(0, 243, 255, 0.5)' : 'rgba(0, 123, 255, 0.3)'

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      textStyle: {
        color: tooltipText
      }
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: {
        color: textColor
      }
    },
    color: ['#00ff9d', '#ffbd2e', '#ff3860', '#ff0000'], // Success, Warning, Error, Severe
    series: [
      {
        name: '交通状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        data: distributionData,
        itemStyle: {
          borderRadius: 8,
          borderColor: borderColor,
          borderWidth: 2
        },
        label: {
          show: true,
          fontSize: 12,
          color: textColor,
          formatter: '{b}\n{d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold',
            color: emphasisLabelColor
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: shadowColor
          }
        }
      }
    ]
  }
})
</script>
