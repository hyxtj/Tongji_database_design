// 主题管理工具
export const themeManager = {
  // 获取当前主题
  getTheme() {
    return localStorage.getItem('theme') || 'dark'
  },
  
  // 设置主题
  setTheme(theme) {
    localStorage.setItem('theme', theme)
    document.documentElement.setAttribute('data-theme', theme)
  },
  
  // 切换主题
  toggleTheme() {
    const current = this.getTheme()
    const newTheme = current === 'dark' ? 'light' : 'dark'
    this.setTheme(newTheme)
    return newTheme
  },
  
  // 初始化主题
  init() {
    const theme = this.getTheme()
    document.documentElement.setAttribute('data-theme', theme)
    return theme
  }
}
