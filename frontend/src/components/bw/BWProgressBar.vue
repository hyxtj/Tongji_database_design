<template>
  <div class="bw-progress">
    <div v-if="showInfo" class="bw-progress__info">
      <span class="bw-progress__label">{{ label }}</span>
      <span class="bw-progress__percentage">{{ percentage }}%</span>
    </div>
    
    <div class="bw-progress__outer">
      <div 
        :class="['bw-progress__inner', `bw-progress__inner--${status}`]"
        :style="{ width: `${percentage}%` }"
      >
        <div v-if="animated" class="bw-progress__stripe"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  percentage: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  status: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'error'].includes(value)
  },
  label: String,
  showInfo: {
    type: Boolean,
    default: true
  },
  animated: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.bw-progress {
  width: 100%;
}

.bw-progress__info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.bw-progress__label {
  color: var(--text-primary);
  font-weight: 500;
}

.bw-progress__percentage {
  color: var(--text-secondary);
  font-weight: 600;
}

.bw-progress__outer {
  width: 100%;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.bw-progress__inner {
  height: 100%;
  border-radius: 4px;
  transition: width var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.bw-progress__inner--default {
  background: var(--text-primary);
}

.bw-progress__inner--success {
  background: #52c41a;
}

.bw-progress__inner--warning {
  background: #faad14;
}

.bw-progress__inner--error {
  background: #ff4d4f;
}

.bw-progress__stripe {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 20px 20px;
  animation: progress-stripe 1s linear infinite;
}

@keyframes progress-stripe {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 20px 0;
  }
}
</style>
