import api from '@/utils/api'
import * as mockData from './mockAnalyticsData'
import realtimeDataManager from './realtimeData'

/**
 * 分析API服务模块
 * 包含所有数据分析相关的API调用方法
 */

// ============ 基础分析 API ============

/**
 * 获取拥堵指数时间序列
 * @param {string} startDate - 开始日期 (YYYY-MM-DD)
 * @param {string} endDate - 结束日期 (YYYY-MM-DD)
 * @param {string} aggregation - 聚合粒度 (hour/day/week)
 * @param {string} roadId - 可选的道路ID
 * @returns {Promise}
 */
export const getCongestionTimeSeries = async (startDate, endDate, aggregation = 'day', roadId = null) => {
  try {
    const params = { startDate, endDate, aggregation }
    if (roadId) params.roadId = roadId
    return await api.get('/analytics/time-series/congestion', { params })
  } catch (error) {
    console.warn('获取拥堵时间序列失败，使用模拟数据:', error)
    return mockData.getMockCongestionTimeSeries(startDate, endDate)
  }
}

/**
 * 获取交通事件时间序列
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @param {string} aggregation - 聚合粒度
 * @param {string} eventType - 可选的事件类型
 * @returns {Promise}
 */
export const getEventsTimeSeries = async (startDate, endDate, aggregation = 'day', eventType = null) => {
  try {
    const params = { startDate, endDate, aggregation }
    if (eventType) params.eventType = eventType
    return await api.get('/analytics/time-series/events', { params })
  } catch (error) {
    console.warn('获取事件时间序列失败，使用模拟数据:', error)
    return mockData.getMockEventsTimeSeries(startDate, endDate)
  }
}

/**
 * 道路性能对比
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @param {array} roadIds - 道路ID数组
 * @returns {Promise}
 */
export const compareRoadPerformance = (startDate, endDate, roadIds) => {
  return api.post('/analytics/comparison/road-performance', {
    startDate,
    endDate,
    roadIds
  })
}

/**
 * 按道路类型对比
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const compareByRoadType = (startDate, endDate) => {
  return api.get('/analytics/comparison/by-road-type', {
    params: { startDate, endDate }
  })
}

/**
 * 获取事件统计
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getEventsStatistics = async (startDate, endDate) => {
  try {
    return await api.get('/analytics/events/statistics', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('获取事件统计失败，使用模拟数据:', error)
    return mockData.getMockEventStatistics(startDate, endDate)
  }
}

/**
 * 事件影响分析
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @param {string} roadId - 可选的道路ID
 * @returns {Promise}
 */
export const analyzeEventImpact = (startDate, endDate, roadId = null) => {
  const params = { startDate, endDate }
  if (roadId) params.roadId = roadId
  return api.get('/analytics/events/impact-analysis', { params })
}

/**
 * 周内趋势分析
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getWeeklyTrends = async (startDate, endDate) => {
  try {
    return await api.get('/analytics/trends/weekly', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('获取周趋势失败，使用模拟数据:', error)
    return mockData.getMockWeeklyTrends(startDate, endDate)
  }
}

/**
 * 月内趋势分析
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getMonthlyTrends = async (startDate, endDate) => {
  try {
    return await api.get('/analytics/trends/monthly', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('获取月趋势失败，使用模拟数据:', error)
    return mockData.getMockMonthlyTrends(startDate, endDate)
  }
}

/**
 * 异常检测
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @param {number} threshold - 阈值 (标准差倍数)
 * @returns {Promise}
 */
export const detectAnomalies = async (startDate, endDate, threshold = 2) => {
  try {
    return await api.get('/analytics/anomalies/detect', {
      params: { startDate, endDate, threshold }
    })
  } catch (error) {
    console.warn('异常检测失败，使用模拟数据:', error)
    return mockData.getMockAnomalies(startDate, endDate, threshold)
  }
}

/**
 * 每日汇总报告
 * @param {string} date - 日期 (YYYY-MM-DD)
 * @returns {Promise}
 */
export const getDailySummary = async (date) => {
  try {
    return await api.get('/analytics/report/daily-summary', {
      params: { date }
    })
  } catch (error) {
    console.warn('获取每日汇总失败，使用模拟数据:', error)
    return mockData.getMockDailySummary(date)
  }
}

/**
 * 道路性能卡片
 * @param {string} roadId - 道路ID
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getRoadPerformanceCard = (roadId, startDate, endDate) => {
  return api.get('/analytics/report/road-performance-card', {
    params: { roadId, startDate, endDate }
  })
}

// ============ 高级分析 API ============

/**
 * 获取道路详细统计
 * @param {string} roadId - 道路ID
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getRoadDetailedStats = (roadId, startDate, endDate) => {
  return api.get('/advanced/traffic/road-stats', {
    params: { roadId, startDate, endDate }
  })
}

/**
 * 高峰时段分析
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getPeakHoursAnalysis = async (startDate, endDate) => {
  try {
    return await api.get('/advanced/traffic/peak-hours', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('获取高峰时段分析失败，使用模拟数据:', error)
    return { data: { data: realtimeDataManager.getMockPeakHours().peak_hours_analysis } }
  }
}

/**
 * 道路排名
 * @param {string} metric - 排名指标 (congestion/speed)
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @param {number} limit - 返回数量限制
 * @returns {Promise}
 */
export const getRoadRanking = async (metric = 'congestion', startDate, endDate, limit = 10) => {
  try {
    const response = await api.get('/advanced/traffic/road-ranking', {
      params: { metric, startDate, endDate, limit }
    })
    console.log('✅ 获取道路排名成功 (API)')
    return response
  } catch (error) {
    console.warn('❌ 获取道路排名失败，使用模拟数据:', error.message)
    const mockResult = mockData.getMockRoadRanking(metric, startDate, endDate, limit)
    console.log('✅ 已返回模拟数据')
    return mockResult
  }
}

/**
 * 道路对比 (多条道路)
 * @param {array} roadIds - 道路ID数组
 * @param {string} metric - 对比指标
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const compareRoads = (roadIds, metric = 'congestion', startDate, endDate) => {
  return api.post('/advanced/traffic/road-comparison', {
    roadIds,
    metric,
    startDate,
    endDate
  })
}

/**
 * 事件统计 (高级)
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getAdvancedEventStatistics = (startDate, endDate) => {
  return api.get('/advanced/events/statistics', {
    params: { startDate, endDate }
  })
}

/**
 * 高影响事件
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @param {number} limit - 返回数量限制
 * @returns {Promise}
 */
export const getHighImpactEvents = async (startDate, endDate, limit = 10) => {
  try {
    return await api.get('/analytics/events/high-impact', {
      params: { startDate, endDate, limit }
    })
  } catch (error) {
    console.warn('获取高影响事件失败，使用模拟数据:', error)
    return mockData.getMockHighImpactEvents(startDate, endDate)
  }
}

/**
 * 事件多发地点
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getFrequentEventLocations = async (startDate, endDate) => {
  try {
    return await api.get('/advanced/events/frequent-locations', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('获取事件多发地点失败，使用模拟数据:', error)
    return { data: { locations: [] } }
  }
}

/**
 * 单个事件影响得分
 * @param {number} eventId - 事件ID
 * @returns {Promise}
 */
export const getEventImpactScore = (eventId) => {
  return api.get(`/advanced/events/impact-score/${eventId}`)
}

/**
 * 事件趋势分析
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getEventTrend = async (startDate, endDate) => {
  try {
    return await api.get('/advanced/events/trend', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('获取事件趋势分析失败，使用模拟数据:', error)
    return { data: { data: [] } }
  }
}

/**
 * 数据完整性检查
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const checkDataCompleteness = async (startDate, endDate) => {
  try {
    return await api.get('/advanced/quality/completeness', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('数据完整性检查失败，使用模拟数据:', error)
    return mockData.getMockDataQualityReport(startDate, endDate)
  }
}

/**
 * 数据一致性检查
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const checkDataConsistency = async (startDate, endDate) => {
  try {
    return await api.get('/advanced/quality/consistency', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('数据一致性检查失败，使用模拟数据:', error)
    return { data: { consistency: { status: 'good', score: 0.98 } } }
  }
}

/**
 * 数据质量报告
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getDataQualityReport = (startDate, endDate) => {
  return api.get('/advanced/quality/report', {
    params: { startDate, endDate }
  })
}

/**
 * 行政汇总报告
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const getExecutiveSummary = async (startDate, endDate) => {
  try {
    return await api.get('/advanced/report/executive-summary', {
      params: { startDate, endDate }
    })
  } catch (error) {
    console.warn('获取行政汇总失败，使用模拟数据:', error)
    return mockData.getMockExecutiveSummary(startDate, endDate)
  }
}

// ============ 数据导出 API ============

/**
 * 导出流量状态为CSV
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const exportTrafficStatusCSV = (startDate, endDate) => {
  return api.get('/export/traffic-status/csv', {
    params: { startDate, endDate },
    responseType: 'blob'
  })
}

/**
 * 导出交通事件为CSV
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const exportTrafficEventsCSV = (startDate, endDate) => {
  return api.get('/export/traffic-events/csv', {
    params: { startDate, endDate },
    responseType: 'blob'
  })
}

/**
 * 导出道路数据为CSV
 * @returns {Promise}
 */
export const exportRoadsCSV = () => {
  return api.get('/export/roads/csv', {
    responseType: 'blob'
  })
}

/**
 * 导出流量状态为JSON
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const exportTrafficStatusJSON = (startDate, endDate) => {
  return api.get('/export/traffic-status/json', {
    params: { startDate, endDate }
  })
}

/**
 * 导出交通事件为JSON
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const exportTrafficEventsJSON = (startDate, endDate) => {
  return api.get('/export/traffic-events/json', {
    params: { startDate, endDate }
  })
}

/**
 * 导出道路数据为JSON
 * @returns {Promise}
 */
export const exportRoadsJSON = () => {
  return api.get('/export/roads/json')
}

/**
 * 导出分析报告
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise}
 */
export const exportAnalyticsReport = (startDate, endDate) => {
  return api.get('/export/analytics-report/json', {
    params: { startDate, endDate }
  })
}

/**
 * 导出自定义数据集
 * @param {object} config - 导出配置
 * @returns {Promise}
 */
export const exportCustomDataset = (config) => {
  return api.post('/export/custom-dataset', config, {
    responseType: config.format === 'csv' ? 'blob' : undefined
  })
}

/**
 * 获取数据摘要
 * @returns {Promise}
 */
export const getDataSummary = () => {
  return api.get('/export/data-summary')
}

// ============ 辅助工具函数 ============

/**
 * 下载文件
 * @param {Blob} blob - 文件数据
 * @param {string} filename - 文件名
 */
export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

/**
 * 格式化日期为 YYYY-MM-DD
 * @param {Date|string} date - 日期对象或字符串
 * @returns {string}
 */
export const formatDate = (date) => {
  if (typeof date === 'string') return date
  const d = new Date(date)
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${month}-${day}`
}

/**
 * 获取近N天的日期范围
 * @param {number} days - 天数
 * @returns {object} { startDate, endDate }
 */
export const getDateRange = (days = 7) => {
  const endDate = new Date()
  const startDate = new Date(endDate.getTime() - days * 24 * 60 * 60 * 1000)
  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate)
  }
}

/**
 * 获取本周的日期范围
 * @returns {object} { startDate, endDate }
 */
export const getCurrentWeekRange = () => {
  const now = new Date()
  const dayOfWeek = now.getDay()
  const startDate = new Date(now.getTime() - dayOfWeek * 24 * 60 * 60 * 1000)
  const endDate = new Date(startDate.getTime() + 7 * 24 * 60 * 60 * 1000)
  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate)
  }
}

/**
 * 获取本月的日期范围
 * @returns {object} { startDate, endDate }
 */
export const getCurrentMonthRange = () => {
  const now = new Date()
  const startDate = new Date(now.getFullYear(), now.getMonth(), 1)
  const endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate)
  }
}
