/**
 * 数据分析模块的模拟数据
 * 当后端API不可用时，使用这些模拟数据保证前端功能完整性
 */

/**
 * 生成随机拥堵指数时间序列
 */
export const getMockCongestionTimeSeries = (startDate, endDate) => {
  const result = []
  const start = new Date(startDate)
  const end = new Date(endDate)
  const current = new Date(start)

  while (current <= end) {
    const hour = current.getHours()
    // 早高峰 (7-9点)、晚高峰 (17-19点) 拥堵指数高
    let baseCongestion = 2
    if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19)) {
      baseCongestion = 6 + Math.random() * 3
    } else if (hour >= 10 && hour <= 16) {
      baseCongestion = 3 + Math.random() * 2
    } else {
      baseCongestion = 0.5 + Math.random()
    }

    result.push({
      timestamp: current.toISOString().split('T')[0],
      avg_congestion: parseFloat(baseCongestion.toFixed(2)),
      min_congestion: parseFloat((baseCongestion * 0.7).toFixed(2)),
      max_congestion: parseFloat((baseCongestion * 1.3).toFixed(2))
    })

    current.setDate(current.getDate() + 1)
  }

  return {
    data: {
      data: result,
      period: `${startDate}至${endDate}`,
      count: result.length
    }
  }
}

/**
 * 生成模拟事件时间序列
 */
export const getMockEventsTimeSeries = (startDate, endDate) => {
  const result = []
  const start = new Date(startDate)
  const end = new Date(endDate)
  const current = new Date(start)

  while (current <= end) {
    const dayOfWeek = current.getDay()
    // 工作日事件更多
    const eventCount = dayOfWeek === 0 || dayOfWeek === 6 ? Math.floor(Math.random() * 3) : Math.floor(Math.random() * 5) + 2

    result.push({
      timestamp: current.toISOString().split('T')[0],
      event_count: eventCount,
      severe_events: Math.floor(eventCount * 0.3),
      active_events: Math.floor(eventCount * 0.8)
    })

    current.setDate(current.getDate() + 1)
  }

  return {
    data: {
      data: result,
      period: `${startDate}至${endDate}`,
      count: result.length
    }
  }
}

/**
 * 生成模拟周内趋势
 */
export const getMockWeeklyTrends = (startDate, endDate) => {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return {
    data: {
      data: days.map((day, index) => ({
        day,
        avg_congestion: (3 + Math.random() * 4).toFixed(2),
        avg_speed: (30 + Math.random() * 20).toFixed(2),
        event_count: Math.floor(Math.random() * 8)
      }))
    }
  }
}

/**
 * 生成模拟月内趋势
 */
export const getMockMonthlyTrends = (startDate, endDate) => {
  const result = []
  for (let i = 1; i <= 30; i++) {
    result.push({
      day: i,
      avg_congestion: (3 + Math.random() * 4).toFixed(2),
      avg_speed: (30 + Math.random() * 20).toFixed(2),
      event_count: Math.floor(Math.random() * 10)
    })
  }
  return {
    data: { data: result }
  }
}

/**
 * 生成模拟异常检测结果
 */
export const getMockAnomalies = (startDate, endDate, threshold = 2) => {
  return {
    data: {
      anomalies: [
        {
          id: 1,
          timestamp: new Date().toISOString(),
          road_id: 4,
          road_name: '江汉路',
          congestion_index: 9.2,
          speed: 15.5,
          status: '严重拥堵',
          expected_value: 4.5,
          deviation: 4.7,
          reason: '突发事故导致大范围拥堵'
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          road_id: 1,
          road_name: '解放大道',
          congestion_index: 7.8,
          speed: 20.1,
          status: '拥堵',
          expected_value: 3.2,
          deviation: 4.6,
          reason: '施工占用车道'
        }
      ],
      total: 2
    }
  }
}

/**
 * 生成模拟每日汇总
 */
export const getMockDailySummary = (date) => {
  return {
    data: {
      summary: {
        date,
        avgCongestion: 4.2,
        avgSpeed: 38.5,
        eventCount: 6,
        eventResolutionRate: 0.83,
        peakHour: '18:00',
        peakCongestion: 7.8,
        totalVehicles: 50000,
        averageDelay: 12
      }
    }
  }
}

/**
 * 生成模拟事件统计
 */
export const getMockEventStatistics = (startDate, endDate) => {
  return {
    data: {
      statistics: {
        total_events: 48,
        type_distribution: {
          '事故': 15,
          '施工': 12,
          '管制': 10,
          '拥堵': 8,
          '恶劣天气': 3
        },
        severity_distribution: {
          '低': 16,
          '中': 20,
          '高': 12
        },
        status_distribution: {
          'active': 5,
          'resolved': 40,
          'pending': 3
        },
        average_duration_minutes: 45
      }
    }
  }
}

/**
 * 生成模拟高影响事件
 */
export const getMockHighImpactEvents = (startDate, endDate) => {
  return {
    data: {
      events: [
        {
          id: 1,
          event_type: '事故',
          severity: '高',
          description: '中山大道与武汉大道交叉口发生严重车碰撞',
          road_name: '中山大道',
          impact_score: 8.9,
          affected_roads: 3,
          duration_minutes: 120,
          start_time: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 2,
          event_type: '施工',
          severity: '中',
          description: '江汉路进行大规模路面维修',
          road_name: '江汉路',
          impact_score: 7.2,
          affected_roads: 2,
          duration_minutes: 480,
          start_time: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
        }
      ]
    }
  }
}

/**
 * 道路排名
 */
export const getMockRoadRanking = (metric, startDate, endDate, limit = 10) => {
  const roads = [
    { id: 1, name: '解放大道', avg_congestion: 6.5, avg_speed: 25.5, road_type: '主干道' },
    { id: 2, name: '中山大道', avg_congestion: 4.2, avg_speed: 35.2, road_type: '主干道' },
    { id: 3, name: '亚洲大道', avg_congestion: 1.2, avg_speed: 50.0, road_type: '快速道路' },
    { id: 4, name: '江汉路', avg_congestion: 8.5, avg_speed: 15.3, road_type: '主干道' },
    { id: 5, name: '武汉大道', avg_congestion: 3.8, avg_speed: 38.6, road_type: '次干道' },
    { id: 6, name: '中北路', avg_congestion: 1.5, avg_speed: 48.5, road_type: '快速道路' }
  ]

  if (metric === 'speed') {
    roads.sort((a, b) => b.avg_speed - a.avg_speed)
  } else {
    roads.sort((a, b) => b.avg_congestion - a.avg_congestion)
  }

  return {
    data: {
      roads: roads.slice(0, limit),
      metric,
      period: `${startDate}至${endDate}`
    }
  }
}

/**
 * 生成模拟数据质量报告
 */
export const getMockDataQualityReport = (startDate, endDate) => {
  return {
    data: {
      quality: {
        completeness_percentage: 95.5,
        missing_records: 24,
        total_records: 1000,
        consistency_score: 98,
        accuracy: 96,
        timeliness: 99
      }
    }
  }
}

/**
 * 生成模拟行政汇总
 */
export const getMockExecutiveSummary = (startDate, endDate) => {
  return {
    data: {
      summary: {
        total_roads: 6,
        avg_congestion: 4.2,
        peak_hour: '18:00',
        total_events: 48,
        critical_roads: [
          { name: '江汉路', status: '严重拥堵', congestion: 8.5, events: 3 },
          { name: '解放大道', status: '拥堵', congestion: 6.5, events: 2 }
        ],
        smooth_roads: [
          { name: '中北路', status: '畅通', speed: 48.5 },
          { name: '亚洲大道', status: '畅通', speed: 50.0 }
        ],
        recommendations: [
          '建议在18:00-19:00采取疏导措施',
          '江汉路需要增加交通管理力量',
          '建议优化公交路线以分流私家车'
        ]
      }
    }
  }
}

/**
 * 生成模拟导出报告
 */
export const getMockExportReport = (startDate, endDate) => {
  return {
    data: {
      report_title: `交通分析报告 (${startDate} 至 ${endDate})`,
      generation_time: new Date().toISOString(),
      summary: {
        total_roads: 6,
        monitoring_days: 7,
        total_events: 48,
        avg_congestion: 4.2
      },
      charts: {
        congestion_trend: {
          title: '拥堵指数趋势',
          data: Array(7).fill(0).map((_, i) => ({
            day: i,
            congestion: 4 + Math.random() * 3
          }))
        },
        road_ranking: {
          title: '道路拥堵排名',
          data: [
            { road: '江汉路', congestion: 8.5 },
            { road: '解放大道', congestion: 6.5 },
            { road: '中山大道', congestion: 4.2 }
          ]
        }
      }
    }
  }
}
