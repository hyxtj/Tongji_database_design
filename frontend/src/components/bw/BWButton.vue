<template>
  <button
    :class="[
      'bw-button',
      `bw-button--${type}`,
      `bw-button--${size}`,
      { 'is-loading': loading, 'is-disabled': disabled }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="bw-button__loading">
      <i class="loading-icon"></i>
    </span>
    <span class="bw-button__content">
      <slot></slot>
    </span>
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'text', 'danger'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  emit('click', event)
}
</script>

<style scoped>
.bw-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  user-select: none;
  outline: none;
}

/* 尺寸 */
.bw-button--small {
  padding: 6px 12px;
  font-size: 13px;
  height: 28px;
}

.bw-button--medium {
  padding: 8px 16px;
  font-size: 14px;
  height: 36px;
}

.bw-button--large {
  padding: 10px 20px;
  font-size: 15px;
  height: 44px;
}

/* 类型 */
.bw-button--default {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--border-primary);
}

.bw-button--default:hover:not(.is-disabled):not(.is-loading) {
  background: var(--bg-secondary);
  border-color: var(--text-primary);
}

.bw-button--primary {
  background: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

.bw-button--primary:hover:not(.is-disabled):not(.is-loading) {
  background: var(--text-secondary);
  border-color: var(--text-secondary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.bw-button--text {
  background: transparent;
  color: var(--text-primary);
  border-color: transparent;
}

.bw-button--text:hover:not(.is-disabled):not(.is-loading) {
  background: var(--bg-secondary);
}

.bw-button--danger {
  background: #ff4d4f;
  color: #ffffff;
  border-color: #ff4d4f;
}

.bw-button--danger:hover:not(.is-disabled):not(.is-loading) {
  background: #ff7875;
  border-color: #ff7875;
}

/* 状态 */
.bw-button.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bw-button.is-loading {
  cursor: wait;
  opacity: 0.8;
}

.bw-button__loading {
  display: inline-flex;
  align-items: center;
}

.loading-icon {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: rotate 0.6s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.bw-button__content {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
</style>
