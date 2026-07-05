<template>
  <el-dialog
    :model-value="visible"
    title="添加交通状态"
    width="500px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <el-form :model="form" label-width="120px">
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
      <el-form-item label="拥堵指数" required>
        <el-input-number
          v-model="form.congestion_index"
          :min="0"
          :max="10"
          :step="0.1"
        />
      </el-form-item>
      <el-form-item label="平均速度">
        <el-input-number
          v-model="form.speed"
          :min="0"
          :step="1"
        />
        <span style="margin-left: 10px;">km/h</span>
      </el-form-item>
      <el-form-item label="车辆数量">
        <el-input-number v-model="form.vehicle_count" :min="0" />
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
  roads: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'saved'])

const saving = ref(false)
const form = reactive({
  road_id: null,
  congestion_index: 0,
  speed: null,
  vehicle_count: null
})

watch(() => props.visible, (newVal) => {
  if (newVal) {
    Object.assign(form, {
      road_id: null,
      congestion_index: 0,
      speed: null,
      vehicle_count: null
    })
  }
})

const handleSave = async () => {
  if (!form.road_id || form.congestion_index === null) {
    ElMessage.warning('请填写必填字段')
    return
  }

  saving.value = true
  try {
    await api.post('/traffic/status', form)
    ElMessage.success('添加成功')
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
:deep(.el-select__wrapper),
:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  background-color: rgba(0, 243, 255, 0.05);
  box-shadow: 0 0 0 1px var(--border-primary) inset;
  color: var(--text-primary);
}

[data-theme='light'] :deep(.el-input__wrapper),
[data-theme='light'] :deep(.el-select__wrapper),
[data-theme='light'] :deep(.el-input-number__decrease),
[data-theme='light'] :deep(.el-input-number__increase) {
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

span {
  color: var(--text-secondary);
}
</style>
