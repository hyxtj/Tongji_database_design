<template>
  <div class="route-plan">
    <el-card class="plan-card">
      <template #header>
        <div class="card-header">
          <span class="title">路线通行时间估算</span>
          <el-tag type="success" effect="dark">新功能</el-tag>
        </div>
      </template>
      
      <div class="plan-content">
        <el-form label-position="top">
          <el-form-item label="选择途径道路 (按顺序)">
            <el-select
              v-model="selectedRoads"
              multiple
              filterable
              placeholder="请选择道路..."
              style="width: 100%"
              :multiple-limit="10"
            >
              <el-option
                v-for="road in roads"
                :key="road.id"
                :label="road.name"
                :value="road.id"
              >
                <span style="float: left">{{ road.name }}</span>
                <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
                  {{ road.road_type }}
                </span>
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-button type="primary" @click="calculateRoute" :loading="loading" :disabled="selectedRoads.length < 1">
            开始计算
          </el-button>
        </el-form>

        <div v-if="result" class="result-section">
          <el-divider content-position="center">计算结果</el-divider>
          
          <el-row :gutter="20" class="summary-row">
            <el-col :span="8">
              <div class="summary-item">
                <div class="label">总距离</div>
                <div class="value">{{ result.total_distance_km }} km</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-item">
                <div class="label">预计耗时</div>
                <div class="value highlight">{{ result.total_time_minutes }} 分钟</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-item">
                <div class="label">平均车速</div>
                <div class="value">{{ result.avg_speed_kmh }} km/h</div>
              </div>
            </el-col>
          </el-row>

          <el-timeline style="margin-top: 20px">
            <el-timeline-item
              v-for="(segment, index) in result.segments"
              :key="index"
              :type="getStatusType(segment.status)"
              :hollow="true"
            >
              <div class="segment-info">
                <span class="road-name">{{ segment.road_name }}</span>
                <el-tag size="small" :type="getStatusType(segment.status)" effect="plain" class="status-tag">
                  {{ segment.status }}
                </el-tag>
                <span class="details">
                  {{ segment.length }}km / {{ segment.speed }}km/h / 约 {{ Math.ceil(segment.time_seconds / 60) }}分钟
                </span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

const roads = ref([])
const selectedRoads = ref([])
const loading = ref(false)
const result = ref(null)

onMounted(async () => {
  try {
    const res = await api.get('/roads')
    roads.value = res.data.roads
  } catch (error) {
    console.error('Failed to load roads:', error)
  }
})

const calculateRoute = async () => {
  loading.value = true
  try {
    const res = await api.post('/traffic/route-estimate', {
      road_ids: selectedRoads.value
    })
    result.value = res.data
  } catch (error) {
    ElMessage.error('计算失败，请稍后重试')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const map = {
    '畅通': 'success',
    '缓行': 'warning',
    '拥堵': 'danger',
    '严重拥堵': 'danger',
    '未知': 'info'
  }
  return map[status] || 'info'
}
</script>

<style scoped>
.route-plan {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.result-section {
  margin-top: 30px;
  animation: fadeIn 0.5s ease;
}

.summary-item {
  text-align: center;
  padding: 15px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.summary-item .label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 5px;
}

.summary-item .value {
  font-size: 20px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.summary-item .value.highlight {
  color: var(--el-color-primary);
  font-size: 24px;
}

.segment-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.road-name {
  font-weight: bold;
  font-size: 16px;
}

.details {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
