<template>
  <div class="roads-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>道路管理</span>
          <el-button
            v-if="userStore.isAdmin"
            type="primary"
            @click="showAddDialog = true"
          >
            <el-icon><Plus /></el-icon>
            添加道路
          </el-button>
        </div>
      </template>

      <div class="toolbar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item>
            <el-input
              v-model="searchForm.search"
              placeholder="搜索道路名称..."
              clearable
              @clear="handleSearch"
              style="width: 240px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-select
              v-model="searchForm.type"
              placeholder="道路类型"
              clearable
              @change="handleSearch"
              style="width: 160px"
            >
              <template #prefix>
                <el-icon><Guide /></el-icon>
              </template>
              <el-option label="高速" value="高速" />
              <el-option label="主干道" value="主干道" />
              <el-option label="次干道" value="次干道" />
              <el-option label="支路" value="支路" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-select
              v-model="searchForm.status"
              placeholder="当前状态"
              clearable
              @change="handleSearch"
              style="width: 160px"
            >
              <template #prefix>
                <el-icon><Monitor /></el-icon>
              </template>
              <el-option label="畅通" value="畅通" />
              <el-option label="缓行" value="缓行" />
              <el-option label="拥堵" value="拥堵" />
              <el-option label="严重拥堵" value="严重拥堵" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" plain @click="handleSearch">
              <el-icon><Search /></el-icon> 查询
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="actions">
          <el-button
            v-if="userStore.isAdmin"
            type="primary"
            @click="showAddDialog = true"
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>
            添加道路
          </el-button>
        </div>
      </div>

      <el-table :data="roads" stripe v-loading="loading" class="custom-table">
        <el-table-column prop="name" label="道路名称" min-width="120">
          <template #default="{ row }">
            <span class="road-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="road_code" label="道路编码" width="120">
          <template #default="{ row }">
            <el-tag type="info" effect="plain" class="code-tag">{{ row.road_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_point" label="起点" min-width="100" />
        <el-table-column prop="end_point" label="终点" min-width="100" />
        <el-table-column prop="length" label="长度" width="100" align="center">
          <template #default="{ row }">
            {{ row.length }} km
          </template>
        </el-table-column>
        <el-table-column prop="lanes" label="车道数" width="80" align="center" />
        <el-table-column prop="road_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getRoadTypeTag(row.road_type)" effect="plain">
              {{ row.road_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" v-if="userStore.isAdmin">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              link
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadRoads"
        @current-change="loadRoads"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingRoad ? '编辑道路' : '添加道路'"
      width="600px"
    >
      <el-form :model="roadForm" label-width="120px">
        <el-form-item label="道路名称" required>
          <el-input v-model="roadForm.name" />
        </el-form-item>
        <el-form-item label="道路编码" required>
          <el-input v-model="roadForm.road_code" :disabled="!!editingRoad" />
        </el-form-item>
        <el-form-item label="起点" required>
          <el-input v-model="roadForm.start_point" />
        </el-form-item>
        <el-form-item label="终点" required>
          <el-input v-model="roadForm.end_point" />
        </el-form-item>
        <el-form-item label="长度(km)">
          <el-input-number v-model="roadForm.length" :min="0" :step="0.1" />
        </el-form-item>
        <el-form-item label="车道数">
          <el-input-number v-model="roadForm.lanes" :min="1" />
        </el-form-item>
        <el-form-item label="道路类型">
          <el-select v-model="roadForm.road_type">
            <el-option label="高速" value="高速" />
            <el-option label="主干道" value="主干道" />
            <el-option label="次干道" value="次干道" />
            <el-option label="支路" value="支路" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="roadForm.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Guide, Monitor, Edit, Delete } from '@element-plus/icons-vue'

const userStore = useUserStore()

const getRoadTypeTag = (type) => {
  const map = {
    '高速': 'danger',
    '主干道': 'primary',
    '次干道': 'success',
    '支路': 'info'
  }
  return map[type] || 'info'
}

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingRoad = ref(null)
const roads = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = reactive({
  search: '',
  type: '',
  status: ''
})

const roadForm = reactive({
  name: '',
  road_code: '',
  start_point: '',
  end_point: '',
  length: null,
  lanes: null,
  road_type: '',
  description: ''
})

const loadRoads = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      ...searchForm
    }
    const response = await api.get('/roads', { params })
    roads.value = response.data.roads
    total.value = response.data.total
  } catch (error) {
    console.error('加载道路列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadRoads()
}

const handleEdit = (row) => {
  editingRoad.value = row
  Object.assign(roadForm, row)
  showAddDialog.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除道路"${row.name}"吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/roads/${row.id}`)
      ElMessage.success('删除成功')
      loadRoads()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

const handleSave = async () => {
  if (!roadForm.name || !roadForm.road_code || !roadForm.start_point || !roadForm.end_point) {
    ElMessage.warning('请填写必填字段')
    return
  }

  saving.value = true
  try {
    if (editingRoad.value) {
      await api.put(`/roads/${editingRoad.value.id}`, roadForm)
      ElMessage.success('更新成功')
    } else {
      await api.post('/roads', roadForm)
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    resetForm()
    loadRoads()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  editingRoad.value = null
  Object.assign(roadForm, {
    name: '',
    road_code: '',
    start_point: '',
    end_point: '',
    length: null,
    lanes: null,
    road_type: '',
    description: ''
  })
}

onMounted(() => {
  loadRoads()
})
</script>

<style scoped>
.roads-page {
  padding: 20px;
  background-color: var(--bg-color);
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.02);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.search-form {
  margin-bottom: 0;
}

.search-form .el-form-item {
  margin-bottom: 0;
  margin-right: 15px;
}

.custom-table {
  margin-top: 10px;
  border-radius: 8px;
  overflow: hidden;
}

.road-name {
  font-weight: 600;
  color: var(--text-primary);
}

.code-tag {
  font-family: monospace;
  letter-spacing: 0.5px;
}

/* 覆盖 Element Plus 样式以适应暗色主题 */
:deep(.el-card) {
  background-color: var(--bg-card);
  border-color: var(--border-color);
  color: var(--text-primary);
}

:deep(.el-card__header) {
  border-bottom-color: var(--border-color);
  padding: 15px 20px;
}

:deep(.el-table) {
  background-color: transparent;
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: rgba(255, 255, 255, 0.05);
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.05);
  --el-table-tr-bg-color: transparent;
  color: var(--text-primary);
}

:deep(.el-table th),
:deep(.el-table tr) {
  background-color: transparent;
}

:deep(.el-table td) {
  border-bottom-color: var(--border-color);
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  background-color: var(--bg-input);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

:deep(.el-input__inner) {
  color: var(--text-primary);
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-button-color: var(--text-secondary);
  --el-pagination-hover-color: var(--primary-color);
}

:deep(.el-dialog) {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
}

:deep(.el-dialog__title) {
  color: var(--text-primary);
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

:deep(.el-button--danger) {
  background-color: var(--danger-color);
  border-color: var(--danger-color);
}
</style>
