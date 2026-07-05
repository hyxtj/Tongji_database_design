/**
 * 实时数据服务 - 整合多种数据源
 */

import api from './api'

/**
 * 数据源配置
 * 可以从以下来源获取实时交通数据:
 * 1. 本地后端API(模拟数据)
 * 2. 高德地图API
 * 3. 百度地图API
 * 4. 政府开放数据平台
 */

class RealtimeDataService {
  constructor() {
    this.updateInterval = null
    this.listeners = []
    
    // 配置: 是否启用自动刷新
    this.autoRefresh = true
    this.refreshInterval = 30000 // 30秒刷新一次
  }

  /**
   * 获取实时交通概览
   */
  async getRealtimeSummary() {
    try {
      const response = await api.get('/traffic/realtime/summary')
      return response.data
    } catch (error) {
      console.error('获取实时交通概览失败:', error)
      return this.getMockSummary()
    }
  }

  /**
   * 获取最新交通状态
   */
  async getLatestTrafficStatus() {
    try {
      const response = await api.get('/traffic/status/latest')
      return response.data
    } catch (error) {
      console.error('获取最新交通状态失败:', error)
      return this.getMockLatestStatus()
    }
  }

  /**
   * 获取活跃交通事件
   */
  async getActiveEvents() {
    try {
      const response = await api.get('/events/active')
      return response.data
    } catch (error) {
      console.error('获取活跃事件失败:', error)
      return this.getMockActiveEvents()
    }
  }

  /**
   * 获取高峰时段分析
   */
  async getPeakHoursAnalysis(days = 7) {
    try {
      const response = await api.get('/traffic/analysis/peak-hours', {
        params: { days }
      })
      return response.data
    } catch (error) {
      console.error('获取高峰时段分析失败:', error)
      return this.getMockPeakHours()
    }
  }

  /**
   * 获取最拥堵道路
   */
  async getMostCongestedRoads(hours = 24, limit = 10) {
    try {
      const response = await api.get('/traffic/analysis/congested-roads', {
        params: { hours, limit }
      })
      return response.data
    } catch (error) {
      console.error('获取最拥堵道路失败:', error)
      return this.getMockCongestedRoads(limit)
    }
  }

  /**
   * 获取最畅通道路
   */
  async getSmoothestRoads(hours = 24, limit = 10) {
    try {
      const response = await api.get('/traffic/analysis/smooth-roads', {
        params: { hours, limit }
      })
      return response.data
    } catch (error) {
      console.error('获取最畅通道路失败:', error)
      return this.getMockSmoothestRoads(limit)
    }
  }

  /**
   * 获取交通统计数据
   */
  async getTrafficStatistics(hours = 24) {
    try {
      const response = await api.get('/traffic/statistics', {
        params: { hours }
      })
      return response.data
    } catch (error) {
      console.error('获取交通统计失败:', error)
      return {
        status_distribution: {},
        avg_congestion_index: 0,
        avg_speed: 0
      }
    }
  }

  /**
   * 获取事件统计
   */
  async getEventStatistics(days = 30) {
    try {
      const response = await api.get('/events/statistics', {
        params: { days }
      })
      return response.data
    } catch (error) {
      console.error('获取事件统计失败:', error)
      return {
        type_distribution: {},
        severity_distribution: {},
        status_distribution: {}
      }
    }
  }

  /**
   * 启动自动刷新
   */
  startAutoRefresh(callback, interval = this.refreshInterval) {
    this.stopAutoRefresh() // 先停止现有的
    
    this.updateInterval = setInterval(async () => {
      if (this.autoRefresh) {
        const data = await this.getRealtimeSummary()
        callback(data)
        
        // 通知所有监听器
        this.notifyListeners(data)
      }
    }, interval)
    
    console.log(`✅ 实时数据刷新已启动 (间隔: ${interval/1000}秒)`)
  }

  /**
   * 停止自动刷新
   */
  stopAutoRefresh() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
      this.updateInterval = null
      console.log('⏸️ 实时数据刷新已停止')
    }
  }

  /**
   * 添加数据监听器
   */
  addListener(callback) {
    this.listeners.push(callback)
  }

  /**
   * 移除监听器
   */
  removeListener(callback) {
    this.listeners = this.listeners.filter(cb => cb !== callback)
  }

  /**
   * 通知所有监听器
   */
  notifyListeners(data) {
    this.listeners.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error('监听器执行失败:', error)
      }
    })
  }

  /**
   * 模拟数据(当API不可用时使用)
   */
  getMockSummary() {
    return {
      total_roads: 6,
      status_breakdown: {
        '畅通': 2,
        '缓行': 2,
        '拥堵': 1,
        '严重拥堵': 1
      },
      avg_congestion_index: 3.5,
      avg_speed: 35.8,
      update_time: new Date().toISOString()
    }
  }

  /**
   * 模拟最新交通状态
   */
  getMockLatestStatus() {
    const now = new Date()
    return {
      statuses: [
        {
          id: 1,
          road_id: 1,
          road_name: '解放大道',
          status: '拥堵',
          speed: 25.5,
          congestion_index: 6.5,
          travel_time: 3600,
          timestamp: now.toISOString(),
          vehicle_count: 150
        },
        {
          id: 2,
          road_id: 2,
          road_name: '中山大道',
          status: '缓行',
          speed: 35.2,
          congestion_index: 4.2,
          travel_time: 2400,
          timestamp: now.toISOString(),
          vehicle_count: 100
        },
        {
          id: 3,
          road_id: 3,
          road_name: '亚洲大道',
          status: '畅通',
          speed: 50.0,
          congestion_index: 1.2,
          travel_time: 1800,
          timestamp: now.toISOString(),
          vehicle_count: 60
        },
        {
          id: 4,
          road_id: 4,
          road_name: '江汉路',
          status: '严重拥堵',
          speed: 15.3,
          congestion_index: 8.5,
          travel_time: 5400,
          timestamp: now.toISOString(),
          vehicle_count: 200
        },
        {
          id: 5,
          road_id: 5,
          road_name: '武汉大道',
          status: '缓行',
          speed: 38.6,
          congestion_index: 3.8,
          travel_time: 2200,
          timestamp: now.toISOString(),
          vehicle_count: 90
        },
        {
          id: 6,
          road_id: 6,
          road_name: '中北路',
          status: '畅通',
          speed: 48.5,
          congestion_index: 1.5,
          travel_time: 1900,
          timestamp: now.toISOString(),
          vehicle_count: 70
        }
      ],
      count: 6
    }
  }

  /**
   * 模拟活跃交通事件
   */
  getMockActiveEvents() {
    const now = new Date()
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)
    return {
      events: [
        {
          id: 1,
          event_type: '事故',
          severity: '高',
          status: 'active',
          description: '中山大道与武汉大道交叉口发生轻微车碰撞',
          road_name: '中山大道',
          affected_lanes: 2,
          start_time: oneHourAgo.toISOString(),
          latitude: 30.593,
          longitude: 114.305
        },
        {
          id: 2,
          event_type: '施工',
          severity: '中',
          status: 'active',
          description: '江汉路进行路面维修，占用一条车道',
          road_name: '江汉路',
          affected_lanes: 1,
          start_time: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
          latitude: 30.590,
          longitude: 114.265
        },
        {
          id: 3,
          event_type: '拥堵',
          severity: '高',
          status: 'active',
          description: '解放大道上班高峰期拥堵严重',
          road_name: '解放大道',
          affected_lanes: 3,
          start_time: new Date(now.getTime() - 30 * 60 * 1000).toISOString(),
          latitude: 30.578,
          longitude: 114.298
        }
      ],
      count: 3
    }
  }

  /**
   * 模拟高峰时段分析
   */
  getMockPeakHours() {
    const baseData = [
      { hour: 0, avg_congestion: 1.2, event_count: 0 },
      { hour: 1, avg_congestion: 0.8, event_count: 0 },
      { hour: 2, avg_congestion: 0.6, event_count: 0 },
      { hour: 3, avg_congestion: 0.5, event_count: 0 },
      { hour: 4, avg_congestion: 0.7, event_count: 1 },
      { hour: 5, avg_congestion: 1.5, event_count: 1 },
      { hour: 6, avg_congestion: 3.2, event_count: 2 },
      { hour: 7, avg_congestion: 5.8, event_count: 3 },
      { hour: 8, avg_congestion: 7.2, event_count: 4 },
      { hour: 9, avg_congestion: 6.5, event_count: 3 },
      { hour: 10, avg_congestion: 4.5, event_count: 2 },
      { hour: 11, avg_congestion: 3.8, event_count: 2 },
      { hour: 12, avg_congestion: 4.2, event_count: 3 },
      { hour: 13, avg_congestion: 3.9, event_count: 2 },
      { hour: 14, avg_congestion: 3.5, event_count: 1 },
      { hour: 15, avg_congestion: 3.8, event_count: 2 },
      { hour: 16, avg_congestion: 4.5, event_count: 2 },
      { hour: 17, avg_congestion: 6.2, event_count: 4 },
      { hour: 18, avg_congestion: 7.5, event_count: 5 },
      { hour: 19, avg_congestion: 6.8, event_count: 4 },
      { hour: 20, avg_congestion: 5.5, event_count: 3 },
      { hour: 21, avg_congestion: 4.2, event_count: 2 },
      { hour: 22, avg_congestion: 3.0, event_count: 1 },
      { hour: 23, avg_congestion: 1.8, event_count: 0 }
    ]

    const enrichedData = baseData.map(item => {
      // 根据拥堵指数估算速度 (拥堵越高速度越低)
      // 假设基础速度60km/h，每增加1点拥堵指数减少约6km/h
      const estimatedSpeed = Math.max(5, 60 - item.avg_congestion * 6 + (Math.random() * 5 - 2.5))
      
      return {
        ...item,
        avg_speed: parseFloat(estimatedSpeed.toFixed(1)),
        max_congestion: parseFloat(Math.min(10, item.avg_congestion * (1.2 + Math.random() * 0.3)).toFixed(2)),
        min_speed: parseFloat(Math.max(0, estimatedSpeed * (0.5 + Math.random() * 0.2)).toFixed(1)),
        record_count: 100 + Math.floor(Math.random() * 50)
      }
    })

    return {
      peak_hours_analysis: enrichedData
    }
  }

  /**
   * 模拟最拥堵道路
   */
  getMockCongestedRoads(limit = 5) {
    const roads = [
      {
        road: { id: 4, name: '江汉路', start_point: '武汉站', end_point: '江汉关' },
        avg_congestion_index: 8.5,
        avg_speed: 15.3,
        event_count: 3
      },
      {
        road: { id: 1, name: '解放大道', start_point: '武昌首义广场', end_point: '汉口北' },
        avg_congestion_index: 6.5,
        avg_speed: 25.5,
        event_count: 2
      },
      {
        road: { id: 2, name: '中山大道', start_point: '汉口', end_point: '武昌' },
        avg_congestion_index: 4.2,
        avg_speed: 35.2,
        event_count: 1
      },
      {
        road: { id: 5, name: '武汉大道', start_point: '青山', end_point: '光谷' },
        avg_congestion_index: 3.8,
        avg_speed: 38.6,
        event_count: 1
      },
      {
        road: { id: 3, name: '亚洲大道', start_point: '武汉客运港', end_point: '三环线' },
        avg_congestion_index: 1.2,
        avg_speed: 50.0,
        event_count: 0
      }
    ]
    return {
      most_congested_roads: roads.slice(0, limit)
    }
  }

  /**
   * 模拟最畅通道路
   */
  getMockSmoothestRoads(limit = 5) {
    const roads = [
      {
        road: { id: 3, name: '亚洲大道', start_point: '武汉客运港', end_point: '三环线' },
        avg_congestion_index: 1.2,
        avg_speed: 50.0
      },
      {
        road: { id: 6, name: '中北路', start_point: '解放公园', end_point: '中北路隧道' },
        avg_congestion_index: 1.5,
        avg_speed: 48.5
      },
      {
        road: { id: 2, name: '中山大道', start_point: '汉口', end_point: '武昌' },
        avg_congestion_index: 4.2,
        avg_speed: 35.2
      },
      {
        road: { id: 5, name: '武汉大道', start_point: '青山', end_point: '光谷' },
        avg_congestion_index: 3.8,
        avg_speed: 38.6
      },
      {
        road: { id: 1, name: '解放大道', start_point: '武昌首义广场', end_point: '汉口北' },
        avg_congestion_index: 6.5,
        avg_speed: 25.5
      }
    ]
    return {
      smoothest_roads: roads.slice(0, limit).reverse()
    }
  }

  /**
   * 获取天气信息(可选 - 影响交通)
   * 可以接入天气API: https://www.qweather.com/
   */
  async getWeatherInfo(city = '武汉') {
    // TODO: 接入天气API
    return {
      city: city,
      weather: '晴',
      temperature: 22,
      humidity: 65,
      aqi: 58,
      visibility: 10
    }
  }

  /**
   * 计算道路拥堵预测(基于历史数据)
   */
  async predictCongestion(roadId, timeOffset = 0) {
    try {
      // 获取历史数据
      const response = await api.get(`/traffic/status/${roadId}/history`, {
        params: { hours: 168 } // 最近7天
      })
      
      const history = response.data.history
      if (!history || history.length === 0) {
        return { prediction: '无法预测', confidence: 0 }
      }
      
      // 简单的预测逻辑(可以用机器学习模型优化)
      const currentHour = new Date().getHours()
      const targetHour = (currentHour + timeOffset) % 24
      
      // 找出历史上同一时段的数据
      const samePeriodData = history.filter(record => {
        const recordHour = new Date(record.timestamp).getHours()
        return recordHour === targetHour
      })
      
      if (samePeriodData.length === 0) {
        return { prediction: '数据不足', confidence: 0 }
      }
      
      // 计算平均拥堵指数
      const avgCongestion = samePeriodData.reduce(
        (sum, record) => sum + (record.congestion_index || 0), 0
      ) / samePeriodData.length
      
      let prediction = '畅通'
      if (avgCongestion > 7) prediction = '严重拥堵'
      else if (avgCongestion > 4) prediction = '拥堵'
      else if (avgCongestion > 2) prediction = '缓行'
      
      return {
        prediction,
        avgCongestion: avgCongestion.toFixed(2),
        confidence: Math.min(samePeriodData.length / 10, 1),
        sampleCount: samePeriodData.length
      }
    } catch (error) {
      console.error('预测失败:', error)
      return { prediction: '预测失败', confidence: 0 }
    }
  }
}

// 导出单例
export default new RealtimeDataService()

/**
 * 使用示例:
 * 
 * import realtimeData from '@/utils/realtimeData'
 * 
 * // 获取实时数据
 * const summary = await realtimeData.getRealtimeSummary()
 * 
 * // 启动自动刷新
 * realtimeData.startAutoRefresh((data) => {
 *   console.log('数据更新:', data)
 * }, 30000) // 30秒
 * 
 * // 停止自动刷新
 * realtimeData.stopAutoRefresh()
 */

/**
 * 接入外部API的方案:
 * 
 * 1. 高德地图API
 *    - 注册: https://lbs.amap.com/
 *    - 文档: https://lbs.amap.com/api/webservice/guide/api/trafficstatus
 *    - 费用: 有免费额度
 * 
 * 2. 百度地图API
 *    - 注册: https://lbsyun.baidu.com/
 *    - 文档: https://lbsyun.baidu.com/index.php?title=webapi/traffic
 *    - 费用: 有免费额度
 * 
 * 3. 城市交通开放数据
 *    - 各城市政府数据开放平台
 *    - 如: 北京交通委、上海交通委等
 *    - 通常免费但需要申请
 * 
 * 4. 爬虫方案(需谨慎)
 *    - 爬取公开的交通网站数据
 *    - 注意遵守robots.txt
 *    - 建议使用官方API
 */
