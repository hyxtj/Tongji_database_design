<template>
  <el-dialog
    :model-value="visible"
    :title="eventData ? '编辑事件' : '添加事件'"
    width="600px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <el-form :model="form" label-width="100px">
      <el-form-item label="道路" required>
        <el-select v-model="form.road_id" filterable style="width: 100%">
          <el-option
            v-for="road in roads"
            :key="road.id"
            :label="road.name"
            :value="road.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="事件类型" required>
        <el-select v-model="form.event_type" style="width: 100%">
          <el-option label="事故" value="事故" />
          <el-option label="故障" value="故障" />
          <el-option label="施工" value="施工" />
          <el-option label="管制" value="管制" />
          <el-option label="积水" value="积水" />
          <el-option label="障碍物" value="障碍物" />
          <el-option label="恶劣天气" value="恶劣天气" />
          <el-option label="其他" value="其他" />
        </el-select>
      </el-form-item>
      <el-form-item label="严重程度">
        <el-select v-model="form.severity" style="width: 100%">
          <el-option label="轻微" value="低" />
          <el-option label="一般" value="中" />
          <el-option label="严重" value="高" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述" required>
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
        />
      </el-form-item>
      <el-form-item label="受影响车道">
        <el-input v-model="form.affected_lanes" placeholder="例如: 左侧两车道" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  eventData: {
    type: Object,
    default: null
  },
  roads: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'saved'])

const saving = ref(false)
const form = reactive({
  road_id: null,
  event_type: '',
  severity: '中',
  description: '',
  affected_lanes: ''
})

watch(() => props.visible, (newVal) => {
  if (newVal) {
    if (props.eventData) {
      Object.assign(form, {
        road_id: props.eventData.road_id,
        event_type: props.eventData.event_type,
        severity: props.eventData.severity,
        description: props.eventData.description,
        affected_lanes: props.eventData.affected_lanes
      })
    } else {
      Object.assign(form, {
        road_id: null,
        event_type: '',
        severity: '中',
        description: '',
        affected_lanes: ''
      })
    }
  }
})

const handleSave = async () => {
  if (!form.road_id || !form.event_type || !form.description) {
    ElMessage.warning('请填写必填字段')
    return
  }

  saving.value = true
  try {
    if (props.eventData) {
      await api.put(`/events/${props.eventData.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/events', form)
      ElMessage.success('添加成功')
    }
    emit('update:visible', false)
    emit('saved')
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
:deep(.el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--primary-color);
  box-shadow: 0 0 30px var(--shadow-sm);
  backdrop-filter: blur(16px);
}

:deep(.el-dialog__title) {
  color: var(--primary-color);
  font-weight: bold;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: var(--primary-color);
}

:deep(.el-form-item__label) {
  color: var(--primary-color);
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  background-color: rgba(0, 243, 255, 0.05);
  box-shadow: 0 0 0 1px var(--border-primary) inset;
}

[data-theme='light'] :deep(.el-input__wrapper),
[data-theme='light'] :deep(.el-select__wrapper) {
  background-color: rgba(0, 0, 0, 0.05);
  box-shadow: 0 0 0 1px var(--border-primary) inset;
}

:deep(.el-input__inner) {
  color: var(--text-primary);
}

:deep(.el-button--primary) {
  background: linear-gradient(45deg, var(--primary-color), var(--primary-hover));
  border: none;
  box-shadow: 0 0 10px var(--shadow-sm);
  color: #fff;
}

:deep(.el-button--primary:hover) {
  box-shadow: 0 0 20px var(--shadow-md);
  transform: translateY(-1px);
}
</style>
