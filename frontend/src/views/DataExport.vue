<template>
  <div class="data-export-container">
    <div v-if="!userStore.isAdmin" style="padding: 20px;">
      <el-alert
        title="权限不足"
        type="error"
        description="只有管理员可以访问数据导出功能。"
        show-icon
        :closable="false"
      />
    </div>
    <div v-else>
      <!-- 页面标题 -->
      <el-row :gutter="20" class="header-row">
      <el-col :span="24">
        <el-card class="header-card">
          <template #header>
            <span class="title">
              <el-icon><Download /></el-icon>
              数据导出
            </span>
          </template>
          <el-alert
            title="数据导出说明"
            type="info"
            description="您可以导出不同时间范围和类型的数据，支持CSV和JSON两种格式。CSV文件可用于Excel分析，JSON文件可用于程序集成。"
            :closable="false"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 导出选项卡 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-tabs v-model="activeTab" type="card">
          <!-- 快速导出 -->
          <el-tab-pane label="快速导出" name="quick">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="export-card">
                  <template #header>
                    <span>
                      <el-icon><DocumentCopy /></el-icon>
                      流量状态数据
                    </span>
                  </template>
                  <p>导出选定时间范围内的流量状态数据</p>
                  <el-form :model="trafficStatusForm" label-width="100px">
                    <el-form-item label="日期范围">
                      <el-date-picker
                        v-model="trafficStatusForm.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item label="导出格式">
                      <el-select v-model="trafficStatusForm.format" style="width: 100%">
                        <el-option label="CSV格式" value="csv" />
                        <el-option label="JSON格式" value="json" />
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="exportTrafficStatus" :loading="exporting">
                        <el-icon><Download /></el-icon>
                        导出流量状态
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card class="export-card">
                  <template #header>
                    <span>
                      <el-icon><Warning /></el-icon>
                      交通事件数据
                    </span>
                  </template>
                  <p>导出选定时间范围内的交通事件数据</p>
                  <el-form :model="trafficEventForm" label-width="100px">
                    <el-form-item label="日期范围">
                      <el-date-picker
                        v-model="trafficEventForm.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item label="导出格式">
                      <el-select v-model="trafficEventForm.format" style="width: 100%">
                        <el-option label="CSV格式" value="csv" />
                        <el-option label="JSON格式" value="json" />
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="exportTrafficEvents" :loading="exporting">
                        <el-icon><Download /></el-icon>
                        导出交通事件
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="12">
                <el-card class="export-card">
                  <template #header>
                    <span>
                      <el-icon><Location /></el-icon>
                      道路数据
                    </span>
                  </template>
                  <p>导出所有道路的基础信息和参数</p>
                  <el-form label-width="100px">
                    <el-form-item label="导出格式">
                      <el-select v-model="roadsFormat" style="width: 100%">
                        <el-option label="CSV格式" value="csv" />
                        <el-option label="JSON格式" value="json" />
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="exportRoads" :loading="exporting">
                        <el-icon><Download /></el-icon>
                        导出道路数据
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card class="export-card">
                  <template #header>
                    <span>
                      <el-icon><Histogram /></el-icon>
                      分析报告
                    </span>
                  </template>
                  <p>导出完整的数据分析报告</p>
                  <el-form :model="reportForm" label-width="100px">
                    <el-form-item label="日期范围">
                      <el-date-picker
                        v-model="reportForm.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="exportReport" :loading="exporting">
                        <el-icon><Download /></el-icon>
                        导出分析报告
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 自定义导出 -->
          <el-tab-pane label="自定义导出" name="custom">
            <el-row>
              <el-col :span="24">
                <el-card class="export-card">
                  <template #header>
                    <span>
                      <el-icon><Tools /></el-icon>
                      自定义数据导出
                    </span>
                  </template>

                  <el-form :model="customExportForm" label-width="120px">
                    <el-form-item label="日期范围">
                      <el-date-picker
                        v-model="customExportForm.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        style="width: 100%"
                      />
                    </el-form-item>

                    <el-form-item label="包含数据类型">
                      <el-checkbox-group v-model="customExportForm.dataTypes" style="width: 100%">
                        <el-checkbox label="trafficStatus">流量状态</el-checkbox>
                        <el-checkbox label="trafficEvents">交通事件</el-checkbox>
                        <el-checkbox label="roads">道路信息</el-checkbox>
                        <el-checkbox label="statistics">统计数据</el-checkbox>
                      </el-checkbox-group>
                    </el-form-item>

                    <el-form-item label="包含字段">
                      <el-select
                        v-model="customExportForm.fields"
                        multiple
                        placeholder="选择要包含的字段（不选则包含全部）"
                        style="width: 100%"
                      >
                        <el-option label="道路名称" value="road_name" />
                        <el-option label="拥堵指数" value="congestion_index" />
                        <el-option label="平均速度" value="speed" />
                        <el-option label="交通状态" value="status" />
                        <el-option label="事件类型" value="event_type" />
                        <el-option label="事件严重程度" value="severity" />
                        <el-option label="时间戳" value="timestamp" />
                      </el-select>
                    </el-form-item>

                    <el-form-item label="聚合粒度">
                      <el-select v-model="customExportForm.aggregation" style="width: 100%">
                        <el-option label="无聚合" value="none" />
                        <el-option label="按小时" value="hour" />
                        <el-option label="按天" value="day" />
                        <el-option label="按周" value="week" />
                        <el-option label="按月" value="month" />
                      </el-select>
                    </el-form-item>

                    <el-form-item label="导出格式">
                      <el-select v-model="customExportForm.format" style="width: 100%">
                        <el-option label="CSV格式" value="csv" />
                        <el-option label="JSON格式" value="json" />
                      </el-select>
                    </el-form-item>

                    <el-form-item label="文件名前缀">
                      <el-input
                        v-model="customExportForm.filename"
                        placeholder="输入文件名前缀"
                      />
                    </el-form-item>

                    <el-form-item>
                      <el-button type="primary" @click="exportCustom" :loading="exporting">
                        <el-icon><Download /></el-icon>
                        导出自定义数据集
                      </el-button>
                      <el-button @click="resetCustomForm">重置</el-button>
                    </el-form-item>
                  </el-form>

                  <el-divider />

                  <div class="export-tips">
                    <el-alert
                      title="导出提示"
                      type="success"
                      :closable="false"
                      description="
                      • CSV格式适合在Excel中打开和分析
                      • JSON格式适合在程序中集成和处理
                      • 大量数据导出可能需要较长时间，请耐心等待
                      • 导出的文件可用于数据备份和二次分析
                      "
                    />
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- 导出历史 -->
          <el-tab-pane label="导出历史与统计" name="history">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>
                      <el-icon><Sort /></el-icon>
                      数据库统计
                    </span>
                  </template>
                  <el-descriptions :column="1" border v-if="dataSummary">
                    <el-descriptions-item label="流量状态记录数">
                      <el-tag type="primary">{{ dataSummary.traffic_status_count || 0 }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="交通事件记录数">
                      <el-tag type="warning">{{ dataSummary.traffic_event_count || 0 }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="道路总数">
                      <el-tag type="info">{{ dataSummary.road_count || 0 }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="数据覆盖时间范围">
                      <span>{{ dataSummary.date_range || '--' }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="最后更新时间">
                      <span>{{ dataSummary.last_update || '--' }}</span>
                    </el-descriptions-item>
                  </el-descriptions>
                  <el-empty v-else description="暂无数据" />
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>
                      <el-icon><SuccessFilled /></el-icon>
                      快速统计
                    </span>
                  </template>
                  <el-row :gutter="10">
                    <el-col :span="12">
                      <div class="stat-box">
                        <div class="stat-title">今日流量状态</div>
                        <div class="stat-value">{{ dataSummary.today_traffic_status_count || 0 }}</div>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div class="stat-box">
                        <div class="stat-title">今日事件数</div>
                        <div class="stat-value">{{ dataSummary.today_event_count || 0 }}</div>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div class="stat-box">
                        <div class="stat-title">本周事件数</div>
                        <div class="stat-value">{{ dataSummary.week_event_count || 0 }}</div>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div class="stat-box">
                        <div class="stat-title">本月事件数</div>
                        <div class="stat-value">{{ dataSummary.month_event_count || 0 }}</div>
                      </div>
                    </el-col>
                  </el-row>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="24">
                <el-card>
                  <template #header>
                    <span>
                      <el-icon><Clock /></el-icon>
                      最近导出
                    </span>
                  </template>
                  <el-timeline v-if="exportHistory.length > 0">
                    <el-timeline-item
                      v-for="item in exportHistory"
                      :key="item.id"
                      :timestamp="item.time"
                      placement="top"
                    >
                      <p>
                        <strong>{{ item.name }}</strong>
                      </p>
                      <p>{{ item.format }} 格式 • {{ item.size }} • {{ item.records }} 条记录</p>
                    </el-timeline-item>
                  </el-timeline>
                  <el-empty v-else description="暂无导出历史" />
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
    </div>
  </div>
</template>

<script setup>
console.log('[DataExport.vue] Script setup 执行开始')

import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  exportTrafficStatusCSV,
  exportTrafficStatusJSON,
  exportTrafficEventsCSV,
  exportTrafficEventsJSON,
  exportRoadsCSV,
  exportRoadsJSON,
  exportAnalyticsReport,
  exportCustomDataset,
  getDataSummary,
  downloadFile,
  formatDate
} from '@/utils/analytics'
import {
  DocumentCopy,
  Warning,
  Location,
  Histogram,
  Tools,
  Download,
  Sort,
  SuccessFilled,
  Clock
} from '@element-plus/icons-vue'

const userStore = useUserStore()

// 状态
const activeTab = ref('quick')
const exporting = ref(false)

// 快速导出表单
const trafficStatusForm = ref({
  dateRange: [],
  format: 'csv'
})

const trafficEventForm = ref({
  dateRange: [],
  format: 'csv'
})

const roadsFormat = ref('csv')

const reportForm = ref({
  dateRange: []
})

// 自定义导出表单
const customExportForm = ref({
  dateRange: [],
  dataTypes: ['trafficStatus', 'trafficEvents'],
  fields: [],
  aggregation: 'none',
  format: 'csv',
  filename: '数据导出'
})

// 历史数据
const dataSummary = ref({})
const exportHistory = ref([])

// 初始化
onMounted(() => {
  try {
    console.log('[DataExport] 页面初始化开始')
    const today = new Date()
    const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    const defaultDateRange = [sevenDaysAgo, today]

    trafficStatusForm.value.dateRange = [...defaultDateRange]
    trafficEventForm.value.dateRange = [...defaultDateRange]
    reportForm.value.dateRange = [...defaultDateRange]
    customExportForm.value.dateRange = [...defaultDateRange]

    // 加载数据统计
    loadDataSummary()

    console.log('[DataExport] 页面初始化完成')
  } catch (error) {
    console.error('[DataExport] 初始化失败:', error)
  }
})

// 加载数据统计
const loadDataSummary = async () => {
  try {
    const response = await getDataSummary()
    console.log('Data summary response:', response)
    dataSummary.value = response?.data?.summary || response || {}

    // 构造导出历史（模拟数据）
    exportHistory.value = [
      {
        id: 1,
        name: '2025-11-20 流量状态 CSV',
        time: '今天 14:30',
        format: 'CSV',
        size: '2.3 MB',
        records: '15,680'
      },
      {
        id: 2,
        name: '2025-11-19 分析报告 JSON',
        time: '昨天 09:15',
        format: 'JSON',
        size: '1.8 MB',
        records: '12,450'
      },
      {
        id: 3,
        name: '2025-11-18 交通事件 CSV',
        time: '3天前',
        format: 'CSV',
        size: '856 KB',
        records: '3,250'
      }
    ]
  } catch (error) {
    console.error('加载数据统计失败:', error)
  }
}

// 导出流量状态
const exportTrafficStatus = async () => {
  if (!userStore.isAdmin) {
    ElMessage.error('需要管理员权限')
    return
  }
  if (!trafficStatusForm.value.dateRange || trafficStatusForm.value.dateRange.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  exporting.value = true
  try {
    const startDate = formatDate(trafficStatusForm.value.dateRange[0])
    const endDate = formatDate(trafficStatusForm.value.dateRange[1])
    const format = trafficStatusForm.value.format

    let response
    if (format === 'csv') {
      response = await exportTrafficStatusCSV(startDate, endDate)
    } else {
      response = await exportTrafficStatusJSON(startDate, endDate)
    }

    if (format === 'csv') {
      downloadFile(response.data, `流量状态_${startDate}_${endDate}.csv`)
    } else {
      const json = JSON.stringify(response.data, null, 2)
      const blob = new Blob([json], { type: 'application/json' })
      downloadFile(blob, `流量状态_${startDate}_${endDate}.json`)
    }

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 导出交通事件
const exportTrafficEvents = async () => {
  if (!userStore.isAdmin) {
    ElMessage.error('需要管理员权限')
    return
  }
  if (!trafficEventForm.value.dateRange || trafficEventForm.value.dateRange.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  exporting.value = true
  try {
    const startDate = formatDate(trafficEventForm.value.dateRange[0])
    const endDate = formatDate(trafficEventForm.value.dateRange[1])
    const format = trafficEventForm.value.format

    let response
    if (format === 'csv') {
      response = await exportTrafficEventsCSV(startDate, endDate)
    } else {
      response = await exportTrafficEventsJSON(startDate, endDate)
    }

    if (format === 'csv') {
      downloadFile(response.data, `交通事件_${startDate}_${endDate}.csv`)
    } else {
      const json = JSON.stringify(response.data, null, 2)
      const blob = new Blob([json], { type: 'application/json' })
      downloadFile(blob, `交通事件_${startDate}_${endDate}.json`)
    }

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 导出道路数据
const exportRoads = async () => {
  if (!userStore.isAdmin) {
    ElMessage.error('需要管理员权限')
    return
  }
  exporting.value = true
  try {
    const format = roadsFormat.value
    let response
    if (format === 'csv') {
      response = await exportRoadsCSV()
    } else {
      response = await exportRoadsJSON()
    }

    if (format === 'csv') {
      downloadFile(response.data, '道路数据.csv')
    } else {
      const json = JSON.stringify(response.data, null, 2)
      const blob = new Blob([json], { type: 'application/json' })
      downloadFile(blob, '道路数据.json')
    }

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 导出分析报告
const exportReport = async () => {
  if (!userStore.isAdmin) {
    ElMessage.error('需要管理员权限')
    return
  }
  if (!reportForm.value.dateRange || reportForm.value.dateRange.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  exporting.value = true
  try {
    const startDate = formatDate(reportForm.value.dateRange[0])
    const endDate = formatDate(reportForm.value.dateRange[1])
    const response = await exportAnalyticsReport(startDate, endDate)

    const json = JSON.stringify(response.data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    downloadFile(blob, `分析报告_${startDate}_${endDate}.json`)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 导出自定义数据集
const exportCustom = async () => {
  if (!userStore.isAdmin) {
    ElMessage.error('需要管理员权限')
    return
  }
  if (!customExportForm.value.dateRange || customExportForm.value.dateRange.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  if (customExportForm.value.dataTypes.length === 0) {
    ElMessage.warning('请选择至少一种数据类型')
    return
  }

  exporting.value = true
  try {
    const startDate = formatDate(customExportForm.value.dateRange[0])
    const endDate = formatDate(customExportForm.value.dateRange[1])

    const config = {
      startDate,
      endDate,
      dataTypes: customExportForm.value.dataTypes,
      fields: customExportForm.value.fields,
      aggregation: customExportForm.value.aggregation,
      format: customExportForm.value.format
    }

    const response = await exportCustomDataset(config)

    if (customExportForm.value.format === 'csv') {
      downloadFile(response.data, `${customExportForm.value.filename}.csv`)
    } else {
      const json = JSON.stringify(response.data, null, 2)
      const blob = new Blob([json], { type: 'application/json' })
      downloadFile(blob, `${customExportForm.value.filename}.json`)
    }

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 重置自定义表单
const resetCustomForm = () => {
  customExportForm.value = {
    dateRange: [],
    dataTypes: ['trafficStatus', 'trafficEvents'],
    fields: [],
    aggregation: 'none',
    format: 'csv',
    filename: '数据导出'
  }
}
</script>

<style scoped>
.data-export-container {
  padding: 20px;
  min-height: 100vh;
}

.header-row {
  margin-bottom: 20px;
}

.header-card {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-md);
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 10px var(--border-secondary);
}

.export-card {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-md);
  margin-bottom: 20px;
  color: var(--text-primary);
}

.export-card p {
  color: var(--text-secondary);
  margin-bottom: 15px;
  font-size: 14px;
}

.export-tips {
  margin-top: 20px;
}

.stat-box {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  color: var(--text-primary);
  padding: 20px;
  border-radius: 6px;
  text-align: center;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
}

.stat-title {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 10px var(--border-secondary);
}

:deep(.el-card) {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-md);
  color: var(--text-primary);
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--border-primary);
  color: var(--primary-color);
}

/* 标签页样式 */
:deep(.el-tabs__header) {
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-primary);
}

:deep(.el-tabs__item) {
  color: var(--text-secondary);
}

:deep(.el-tabs__item.is-active) {
  color: var(--primary-color);
  text-shadow: 0 0 10px var(--border-secondary);
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__nav) {
  border: 1px solid var(--border-primary);
  border-bottom: none;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item) {
  border-left: 1px solid var(--border-primary);
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item.is-active) {
  background: var(--bg-elevated);
  border-bottom-color: transparent;
}

/* 表单样式 */
:deep(.el-form-item__label) {
  color: var(--text-primary);
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper),
:deep(.el-range-editor.el-input__wrapper) {
  background-color: var(--bg-card);
  box-shadow: 0 0 0 1px var(--border-primary) inset;
}

:deep(.el-input__inner),
:deep(.el-range-input) {
  color: var(--text-primary);
}

:deep(.el-checkbox) {
  color: var(--text-primary);
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

:deep(.el-checkbox__inner) {
  background-color: transparent;
  border-color: var(--border-primary);
}

/* 描述列表样式 */
:deep(.el-descriptions) {
  --el-descriptions-table-border: 1px solid var(--border-primary);
  --el-descriptions-item-bordered-label-background: var(--bg-elevated);
}

:deep(.el-descriptions__body) {
  background: transparent;
  color: var(--text-primary);
}

:deep(.el-descriptions__label) {
  color: var(--text-secondary);
}

/* 时间轴样式 */
:deep(.el-timeline-item__timestamp) {
  color: var(--text-secondary);
}

:deep(.el-timeline-item__content) {
  color: var(--text-primary);
}

:deep(.el-timeline-item__node) {
  background-color: var(--primary-color);
}

:deep(.el-timeline-item__tail) {
  border-left: 2px solid var(--border-primary);
}

/* 警告框样式 */
:deep(.el-alert--info) {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

:deep(.el-alert--success) {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--color-success);
}

:deep(.el-alert__title) {
  color: var(--primary-color);
  font-weight: bold;
}

:deep(.el-alert--success .el-alert__title) {
  color: var(--color-success);
}

:deep(.el-alert__description) {
  color: var(--text-secondary);
}

:deep(.el-divider) {
  border-top: 1px solid var(--border-primary);
  margin: 20px 0;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}
</style>
