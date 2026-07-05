<template>
  <span :class="['status-tag', tagClass]">
    <slot>{{ text }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: { type: String, required: true },
  category: { type: String, default: 'status' }
})

const tagClass = computed(() => {
  const val = props.text
  let color = 'info'
  
  if (props.category === 'traffic') {
    const map = {
      '畅通': 'success',
      '缓行': 'warning',
      '拥堵': 'danger',
      '严重拥堵': 'purple'
    }
    color = map[val] || 'info'
  } else if (props.category === 'severity') {
    const map = {
      '轻微': 'success',
      '一般': 'warning',
      '严重': 'danger',
      '低': 'success',
      '中': 'warning',
      '高': 'danger'
    }
    color = map[val] || 'info'
  } else if (props.category === 'status') {
    if (val === 'active' || val === '活跃') color = 'orange'
    else if (val === 'resolved' || val === '已解决') color = 'success'
  } else if (props.category === 'event_type') {
    const map = {
      '事故': 'danger',
      '故障': 'orange',
      '施工': 'warning',
      '管制': 'purple',
      '积水': 'cyan',
      '障碍物': 'pink',
      '恶劣天气': 'blue',
      '其他': 'info'
    }
    color = map[val] || 'info'
  }
  
  return `tag-${color}`
})
</script>

<style scoped>
.status-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid;
  white-space: nowrap;
  line-height: 20px;
}

/* Success (Green) */
.tag-success {
  color: #00ff9d;
  border-color: #00ff9d;
  background-color: rgba(0, 255, 157, 0.1);
  box-shadow: 0 0 5px rgba(0, 255, 157, 0.2);
}

/* Warning (Yellow) */
.tag-warning {
  color: #ffbd2e;
  border-color: #ffbd2e;
  background-color: rgba(255, 189, 46, 0.1);
  box-shadow: 0 0 5px rgba(255, 189, 46, 0.2);
}

/* Danger (Red) */
.tag-danger {
  color: #ff3860;
  border-color: #ff3860;
  background-color: rgba(255, 56, 96, 0.1);
  box-shadow: 0 0 5px rgba(255, 56, 96, 0.2);
}

/* Info (Grey) */
.tag-info {
  color: #a0a0a0;
  border-color: #a0a0a0;
  background-color: rgba(160, 160, 160, 0.1);
}

/* Cyan (Primary) */
.tag-cyan {
  color: #00f3ff;
  border-color: #00f3ff;
  background-color: rgba(0, 243, 255, 0.1);
  box-shadow: 0 0 5px rgba(0, 243, 255, 0.2);
}

/* Purple */
.tag-purple {
  color: #bc13fe;
  border-color: #bc13fe;
  background-color: rgba(188, 19, 254, 0.1);
  box-shadow: 0 0 5px rgba(188, 19, 254, 0.2);
}

/* Orange */
.tag-orange {
  color: #ff8800;
  border-color: #ff8800;
  background-color: rgba(255, 136, 0, 0.1);
  box-shadow: 0 0 5px rgba(255, 136, 0, 0.2);
}

/* Pink */
.tag-pink {
  color: #ff0099;
  border-color: #ff0099;
  background-color: rgba(255, 0, 153, 0.1);
  box-shadow: 0 0 5px rgba(255, 0, 153, 0.2);
}

/* Blue */
.tag-blue {
  color: #2979ff;
  border-color: #2979ff;
  background-color: rgba(41, 121, 255, 0.1);
  box-shadow: 0 0 5px rgba(41, 121, 255, 0.2);
}
</style>
