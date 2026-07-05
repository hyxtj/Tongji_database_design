/**
 * 测试文件 - 验证所有需要的导入都存在
 */

console.log('[Test Imports] 开始验证导入...')

// 测试 analytics.js 导出
try {
  import('@/utils/analytics').then(module => {
    console.log('[Test] analytics.js 导入成功')
    const required = [
      'getCongestionTimeSeries',
      'getEventsTimeSeries',
      'compareRoads',
      'getWeeklyTrends',
      'getMonthlyTrends',
      'detectAnomalies',
      'getEventsStatistics',
      'getHighImpactEvents',
      'getDailySummary',
      'getDateRange',
      'getCurrentWeekRange',
      'getCurrentMonthRange',
      'formatDate',
      'exportAnalyticsReport',
      'downloadFile',
      'exportTrafficStatusCSV',
      'exportTrafficStatusJSON',
      'exportTrafficEventsCSV',
      'exportTrafficEventsJSON',
      'exportRoadsCSV',
      'exportRoadsJSON',
      'exportCustomDataset',
      'getDataSummary'
    ]
    
    for (const fnName of required) {
      if (!module[fnName]) {
        console.warn(`⚠️  缺少导出: ${fnName}`)
      } else {
        console.log(`✓ ${fnName}`)
      }
    }
  }).catch(err => {
    console.error('[Test] analytics.js 导入失败:', err)
  })
} catch (err) {
  console.error('[Test] 同步导入失败:', err)
}

// 测试 api.js
try {
  import('@/utils/api').then(module => {
    console.log('[Test] api.js 导入成功')
    console.log('[Test] 默认导出:', typeof module.default)
  }).catch(err => {
    console.error('[Test] api.js 导入失败:', err)
  })
} catch (err) {
  console.error('[Test] 同步导入失败:', err)
}

console.log('[Test Imports] 验证完成')
