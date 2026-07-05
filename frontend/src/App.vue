<template>
  <div id="app" :data-theme="theme">
    <!-- 主题切换按钮 -->
    <button class="theme-toggle" @click="toggleTheme" title="切换主题">
      <span class="theme-toggle-icon">{{ theme === 'dark' ? '🌙' : '☀️' }}</span>
    </button>
    
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 主题管理
const theme = ref(localStorage.getItem('theme') || 'dark')

// 切换主题
const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', theme.value)
  document.documentElement.setAttribute('data-theme', theme.value)
  
  // 触发自定义事件通知其他组件
  window.dispatchEvent(new Event('theme-change'))
  window.dispatchEvent(new StorageEvent('storage', {
    key: 'theme',
    newValue: theme.value
  }))
}

onMounted(() => {
  // 恢复主题设置
  document.documentElement.setAttribute('data-theme', theme.value)
  
  // 尝试从本地存储恢复登录状态
  const token = localStorage.getItem('token')
  if (token) {
    userStore.getCurrentUser()
  }
})
</script>

<style>
@import '@/styles/theme-bw.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  border: none !important; /* Ensure no borders */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  background: var(--layout-bg) !important;
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

#app {
  min-height: 100vh;
}

/* 主题切换按钮样式已在 theme-bw.css 中定义 */

/* Element Plus 组件主题适配 */
.el-card {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-primary) !important;
  border-radius: 8px !important;
  color: var(--text-primary) !important;
  box-shadow: var(--shadow-sm) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--border-primary) !important;
  color: var(--text-primary) !important;
}

/* 按钮 */
.el-button {
  border-radius: 6px !important;
  transition: all var(--transition-fast) !important;
}

.el-button--default {
  background: var(--bg-card) !important;
  border-color: var(--border-primary) !important;
  color: var(--text-primary) !important;
}

.el-button--default:hover {
  background: var(--bg-card-hover) !important;
  border-color: var(--border-hover) !important;
}

.el-button--primary {
  background: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

[data-theme="light"] .el-button--primary {
  color: #000000 !important;
}

[data-theme="dark"] .el-button--primary {
  color: #ffffff !important;
}

/* 输入框 */
.el-input__wrapper {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-primary) !important;
  border-radius: 6px !important;
  box-shadow: none !important;
  transition: all var(--transition-fast) !important;
}

.el-input__wrapper:hover {
  border-color: var(--border-hover) !important;
}

.el-input__wrapper.is-focus {
  border-color: var(--primary-color) !important;
}

.el-input__inner {
  color: var(--text-primary) !important;
}

.el-input__inner::placeholder {
  color: var(--text-disabled) !important;
}

/* 下拉框 */
.el-select-dropdown {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-primary) !important;
  border-radius: 6px !important;
  box-shadow: var(--shadow-md) !important;
}

.el-select-dropdown__item {
  color: var(--text-primary) !important;
}

.el-select-dropdown__item:hover {
  background: var(--bg-card-hover) !important;
}

.el-select-dropdown__item.selected {
  color: var(--primary-color) !important;
}

/* 表格 */
.el-table {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  --el-table-bg-color: var(--bg-card) !important;
  --el-table-tr-bg-color: var(--bg-card) !important;
  --el-table-header-bg-color: var(--bg-elevated) !important;
  --el-table-row-hover-bg-color: var(--bg-card-hover) !important;
}

.el-table th {
  background: var(--bg-elevated) !important;
  color: var(--text-secondary) !important;
  border-bottom: 2px solid var(--border-primary) !important;
}

.el-table tr {
  background-color: var(--bg-card) !important;
}

.el-table td {
  background-color: var(--bg-card) !important;
  border-bottom: 1px solid var(--border-secondary) !important;
}

/* 斑马纹样式适配 */
.el-table--striped .el-table__body tr.el-table__row--striped td {
  background: var(--bg-elevated) !important;
}

.el-table tr:hover > td {
  background: var(--bg-card-hover) !important;
}

.el-table--border {
  border-color: var(--border-primary) !important;
}

/* 对话框 */
.el-dialog {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-primary) !important;
  border-radius: 8px !important;
  box-shadow: var(--shadow-lg) !important;
}

.el-dialog__header {
  border-bottom: 1px solid var(--border-primary) !important;
}

.el-dialog__title {
  color: var(--text-primary) !important;
}

.el-dialog__body {
  color: var(--text-primary) !important;
}

.el-dialog__close {
  color: var(--text-secondary) !important;
}

.el-dialog__close:hover {
  color: var(--text-primary) !important;
}

/* 消息提示 */
.el-message {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-primary) !important;
  border-radius: 6px !important;
  box-shadow: var(--shadow-md) !important;
}

.el-message__content {
  color: var(--text-primary) !important;
}

/* 分页 */
.el-pagination {
  color: var(--text-primary) !important;
}

.el-pagination button {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-primary) !important;
}

.el-pagination button:hover {
  color: var(--primary-color) !important;
}

.el-pagination .el-pager li {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-primary);
  margin: 0 2px;
}

.el-pagination .el-pager li:hover {
  color: var(--primary-color) !important;
}

.el-pagination .el-pager li.active {
  background: var(--primary-color) !important;
}

[data-theme="light"] .el-pagination .el-pager li.active {
  color: var(--bg-primary) !important;
}

[data-theme="dark"] .el-pagination .el-pager li.active {
  color: var(--bg-primary) !important;
}

/* 加载动画 */
.el-loading-mask {
  background-color: rgba(0, 0, 0, 0.5) !important;
}

[data-theme="light"] .el-loading-mask {
  background-color: rgba(255, 255, 255, 0.7) !important;
}

/* 空状态 */
.el-empty {
  color: var(--text-tertiary) !important;
}

.el-empty__description p {
  color: var(--text-tertiary) !important;
}

/* 标签 */
.el-tag {
  border-radius: 4px !important;
}

/* 开关 */
.el-switch {
  --el-switch-on-color: var(--primary-color) !important;
}

/* 滑块 */
.el-slider__button {
  border-color: var(--primary-color) !important;
}

.el-slider__bar {
  background-color: var(--primary-color) !important;
}

/* 复选框 */
.el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

/* 单选框 */
.el-radio__input.is-checked .el-radio__inner {
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

/* 菜单 */
.el-menu {
  background: var(--bg-card) !important;
  border-color: var(--border-primary) !important;
}

.el-menu-item {
  color: var(--text-primary) !important;
}

.el-menu-item:hover {
  background: var(--bg-card-hover) !important;
}

.el-menu-item.is-active {
  color: var(--primary-color) !important;
}

/* 标签页 */
.el-tabs__item {
  color: var(--text-secondary) !important;
}

.el-tabs__item:hover {
  color: var(--text-primary) !important;
}

.el-tabs__item.is-active {
  color: var(--primary-color) !important;
}

.el-tabs__active-bar {
  background-color: var(--primary-color) !important;
}

.el-tabs__nav-wrap::after {
  background-color: var(--border-primary) !important;
}
</style>
