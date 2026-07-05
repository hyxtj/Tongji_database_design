<template>
  <div :class="['bw-loading', { 'is-fullscreen': fullscreen }]">
    <div :class="['bw-loading__spinner', `bw-loading__spinner--${type}`]">
      <div v-if="type === 'circle'" class="spinner-circle"></div>
      <div v-else-if="type === 'dots'" class="spinner-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <div v-else-if="type === 'bars'" class="spinner-bars">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
    <p v-if="text" class="bw-loading__text">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'circle',
    validator: (value) => ['circle', 'dots', 'bars'].includes(value)
  },
  text: String,
  fullscreen: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.bw-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
}

.bw-loading.is-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 2000;
}

.bw-loading__spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.bw-loading__text {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 圆形加载器 */
.spinner-circle {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-secondary);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 点状加载器 */
.spinner-dots {
  display: flex;
  gap: 8px;
}

.spinner-dots span {
  width: 10px;
  height: 10px;
  background: var(--text-primary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.spinner-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.spinner-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.5);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 条形加载器 */
.spinner-bars {
  display: flex;
  gap: 4px;
  align-items: flex-end;
  height: 30px;
}

.spinner-bars span {
  width: 6px;
  background: var(--text-primary);
  border-radius: 3px;
  animation: grow 1.2s infinite ease-in-out;
}

.spinner-bars span:nth-child(1) {
  animation-delay: -1.2s;
}

.spinner-bars span:nth-child(2) {
  animation-delay: -1.1s;
}

.spinner-bars span:nth-child(3) {
  animation-delay: -1.0s;
}

.spinner-bars span:nth-child(4) {
  animation-delay: -0.9s;
}

@keyframes grow {
  0%, 40%, 100% {
    height: 10px;
  }
  20% {
    height: 30px;
  }
}

/* 全屏模式样式 */
.bw-loading.is-fullscreen .bw-loading__text {
  color: #ffffff;
}

.bw-loading.is-fullscreen .spinner-circle {
  border-color: rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
}

.bw-loading.is-fullscreen .spinner-dots span,
.bw-loading.is-fullscreen .spinner-bars span {
  background: #ffffff;
}
</style>
