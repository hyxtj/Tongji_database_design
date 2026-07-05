<template>
  <div 
    :class="['bw-card', `bw-card--${variant}`, { 'bw-card--hoverable': hoverable }]"
    @click="handleClick"
  >
    <div v-if="$slots.header || title" class="bw-card__header">
      <slot name="header">
        <h3 class="bw-card__title">{{ title }}</h3>
      </slot>
      <div v-if="$slots.extra" class="bw-card__extra">
        <slot name="extra"></slot>
      </div>
    </div>
    
    <div class="bw-card__body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="bw-card__footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'accent', 'stat'].includes(value)
  },
  hoverable: {
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
.bw-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  padding: 20px;
  transition: all var(--transition-normal);
}

.bw-card--hoverable {
  cursor: pointer;
}

.bw-card--hoverable:hover {
  border-color: var(--border-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.bw-card--accent {
  border-color: var(--text-primary);
  background: var(--bg-secondary);
}

.bw-card--stat {
  text-align: center;
  padding: 24px 20px;
}

.bw-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-secondary);
}

.bw-card__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.bw-card__extra {
  color: var(--text-secondary);
}

.bw-card__body {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.bw-card__footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-secondary);
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
