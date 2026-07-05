<template>
  <span :class="['bw-status-badge', `bw-status-badge--${status}`, { 'has-dot': showDot }]">
    <span v-if="showDot" class="bw-status-badge__dot"></span>
    <span class="bw-status-badge__text">
      <slot>{{ text }}</slot>
    </span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'smooth', 'slow', 'congested', 'severe', 'success', 'warning', 'error', 'info'].includes(value)
  },
  showDot: {
    type: Boolean,
    default: true
  }
})

const text = computed(() => {
  const statusMap = {
    smooth: '畅通',
    slow: '缓慢',
    congested: '拥堵',
    severe: '严重拥堵',
    success: '成功',
    warning: '警告',
    error: '错误',
    info: '信息',
    default: '默认'
  }
  return statusMap[props.status] || props.status
})
</script>

<style scoped>
.bw-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.bw-status-badge__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

.bw-status-badge__text {
  line-height: 1;
}

/* 状态颜色 */
.bw-status-badge--default {
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-secondary);
}

.bw-status-badge--default .bw-status-badge__dot {
  background: var(--text-tertiary);
}

.bw-status-badge--smooth,
.bw-status-badge--success {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
  border: 1px solid rgba(82, 196, 26, 0.2);
}

.bw-status-badge--smooth .bw-status-badge__dot,
.bw-status-badge--success .bw-status-badge__dot {
  background: #52c41a;
}

.bw-status-badge--slow,
.bw-status-badge--info {
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
  border: 1px solid rgba(24, 144, 255, 0.2);
}

.bw-status-badge--slow .bw-status-badge__dot,
.bw-status-badge--info .bw-status-badge__dot {
  background: #1890ff;
}

.bw-status-badge--congested,
.bw-status-badge--warning {
  background: rgba(250, 173, 20, 0.1);
  color: #faad14;
  border: 1px solid rgba(250, 173, 20, 0.2);
}

.bw-status-badge--congested .bw-status-badge__dot,
.bw-status-badge--warning .bw-status-badge__dot {
  background: #faad14;
}

.bw-status-badge--severe,
.bw-status-badge--error {
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
  border: 1px solid rgba(255, 77, 79, 0.2);
}

.bw-status-badge--severe .bw-status-badge__dot,
.bw-status-badge--error .bw-status-badge__dot {
  background: #ff4d4f;
}

/* 无点样式 */
.bw-status-badge:not(.has-dot) {
  padding: 4px 12px;
}
</style>
