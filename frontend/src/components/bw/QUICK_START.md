# 黑白主题组件库 - 快速开始

## 5 分钟上手指南

### 1️⃣ 导入组件

在你的 Vue 文件中导入需要的组件:

```vue
<script setup>
import { BWCard, BWButton, BWInput } from '@/components/bw'
</script>
```

### 2️⃣ 使用组件

```vue
<template>
  <BWCard title="Hello World">
    <p>这是我的第一个黑白主题组件!</p>
    <BWButton type="primary">点击我</BWButton>
  </BWCard>
</template>
```

### 3️⃣ 启动项目

```bash
cd frontend
pnpm run dev
```

就是这么简单! 🎉

---

## 常用模式

### 📝 表单示例

```vue
<template>
  <BWCard title="用户注册">
    <form @submit.prevent="handleSubmit">
      <BWInput 
        v-model="form.name" 
        label="姓名"
        required
        :error="errors.name"
      />
      
      <BWInput 
        v-model="form.email" 
        label="邮箱"
        type="email"
        required
        :error="errors.email"
      />
      
      <BWButton type="primary" :loading="submitting">
        提交
      </BWButton>
    </form>
  </BWCard>
</template>

<script setup>
import { ref } from 'vue'
import { BWCard, BWInput, BWButton } from '@/components/bw'

const form = ref({ name: '', email: '' })
const errors = ref({})
const submitting = ref(false)

const handleSubmit = async () => {
  submitting.value = true
  try {
    // 提交逻辑
    await api.submit(form.value)
  } finally {
    submitting.value = false
  }
}
</script>
```

### 📊 统计卡片

```vue
<template>
  <div class="stats-grid">
    <BWCard variant="stat" hoverable>
      <h2>1,234</h2>
      <p>总用户数</p>
      <BWStatusBadge status="success">+12%</BWStatusBadge>
    </BWCard>
    
    <BWCard variant="stat" hoverable>
      <h2>567</h2>
      <p>在线用户</p>
      <BWStatusBadge status="warning">持平</BWStatusBadge>
    </BWCard>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
</style>
```

### 💬 确认对话框

```vue
<template>
  <BWButton @click="showDialog = true">删除</BWButton>
  
  <BWModal 
    v-model="showDialog"
    title="确认删除"
    @confirm="handleDelete"
  >
    <p>确定要删除这条记录吗?此操作不可撤销。</p>
  </BWModal>
</template>

<script setup>
import { ref } from 'vue'
import { BWButton, BWModal } from '@/components/bw'

const showDialog = ref(false)

const handleDelete = async () => {
  await api.delete()
  showDialog.value = false
}
</script>
```

### 📈 进度追踪

```vue
<template>
  <BWCard title="任务进度">
    <BWProgressBar 
      :percentage="taskProgress" 
      label="当前任务"
      :status="taskProgress === 100 ? 'success' : 'default'"
      animated
    />
    
    <BWButton 
      type="primary" 
      :loading="processing"
      @click="startTask"
    >
      开始任务
    </BWButton>
  </BWCard>
</template>

<script setup>
import { ref } from 'vue'
import { BWCard, BWProgressBar, BWButton } from '@/components/bw'

const taskProgress = ref(0)
const processing = ref(false)

const startTask = () => {
  processing.value = true
  const interval = setInterval(() => {
    taskProgress.value += 10
    if (taskProgress.value >= 100) {
      clearInterval(interval)
      processing.value = false
    }
  }, 500)
}
</script>
```

---

## 主题切换

所有组件自动适配明暗主题,无需额外配置!

```vue
<template>
  <!-- 组件会自动响应主题变化 -->
  <BWCard title="自动适配主题">
    <p>切换主题看看效果!</p>
  </BWCard>
</template>
```

主题切换按钮已集成在页面右下角。

---

## 样式定制

### 方式1: CSS 变量

```vue
<style>
/* 全局修改 */
:root {
  --text-primary: #your-color;
}

/* 组件级修改 */
.my-card {
  --bg-elevated: #your-color;
}
</style>
```

### 方式2: 深度选择器

```vue
<style scoped>
.my-component :deep(.bw-button) {
  border-radius: 20px;
  font-size: 16px;
}
</style>
```

---

## 常见搭配

### 加载状态处理

```vue
<template>
  <BWCard title="数据列表">
    <BWLoading v-if="loading" type="dots" text="加载中..." />
    
    <div v-else>
      <div v-for="item in data" :key="item.id">
        {{ item.name }}
      </div>
    </div>
  </BWCard>
</template>
```

### 状态反馈

```vue
<template>
  <BWCard>
    <BWInput v-model="value" label="输入内容" />
    
    <BWStatusBadge 
      :status="value ? 'success' : 'warning'"
      :show-dot="false"
    >
      {{ value ? '已填写' : '待填写' }}
    </BWStatusBadge>
  </BWCard>
</template>
```

---

## 完整示例

一个完整的用户编辑表单:

```vue
<template>
  <BWCard title="编辑用户" hoverable>
    <template #extra>
      <BWStatusBadge :status="user.active ? 'success' : 'warning'">
        {{ user.active ? '激活' : '未激活' }}
      </BWStatusBadge>
    </template>

    <form @submit.prevent="save">
      <BWInput 
        v-model="user.name" 
        label="姓名"
        prefix-icon="👤"
        required
        :error="errors.name"
      />

      <BWInput 
        v-model="user.email" 
        label="邮箱"
        type="email"
        prefix-icon="📧"
        clearable
        required
        :error="errors.email"
      />

      <BWInput 
        v-model="user.phone" 
        label="手机"
        prefix-icon="📱"
        clearable
      />

      <BWProgressBar 
        :percentage="completeness" 
        label="资料完整度"
        :status="completeness === 100 ? 'success' : 'warning'"
      />

      <div class="buttons">
        <BWButton @click="reset">重置</BWButton>
        <BWButton 
          type="primary" 
          :loading="saving"
          @click="save"
        >
          保存
        </BWButton>
      </div>
    </form>

    <template #footer>
      最后更新: {{ user.updatedAt }}
    </template>
  </BWCard>

  <!-- 确认对话框 -->
  <BWModal 
    v-model="confirmVisible"
    title="保存确认"
    @confirm="doSave"
  >
    <p>确定要保存这些更改吗?</p>
  </BWModal>

  <!-- 全屏加载 -->
  <BWLoading 
    v-if="globalLoading" 
    text="处理中..." 
    fullscreen 
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  BWCard,
  BWInput,
  BWButton,
  BWStatusBadge,
  BWProgressBar,
  BWModal,
  BWLoading
} from '@/components/bw'

const user = ref({
  name: '',
  email: '',
  phone: '',
  active: true,
  updatedAt: new Date().toLocaleString()
})

const errors = ref({})
const saving = ref(false)
const confirmVisible = ref(false)
const globalLoading = ref(false)

const completeness = computed(() => {
  let score = 0
  if (user.value.name) score += 40
  if (user.value.email) score += 40
  if (user.value.phone) score += 20
  return score
})

const save = () => {
  if (validate()) {
    confirmVisible.value = true
  }
}

const doSave = async () => {
  confirmVisible.value = false
  globalLoading.value = true
  
  try {
    await api.updateUser(user.value)
    user.value.updatedAt = new Date().toLocaleString()
  } finally {
    globalLoading.value = false
  }
}

const reset = () => {
  user.value = { name: '', email: '', phone: '', active: true }
  errors.value = {}
}

const validate = () => {
  errors.value = {}
  
  if (!user.value.name) {
    errors.value.name = '请输入姓名'
    return false
  }
  
  if (!user.value.email) {
    errors.value.email = '请输入邮箱'
    return false
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(user.value.email)) {
    errors.value.email = '邮箱格式不正确'
    return false
  }
  
  return true
}
</script>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>
```

---

## 下一步

- 📖 查看 [完整文档](./README.md)
- 🎨 浏览 [组件演示](/components-demo)
- 💡 参考 [更新日志](../../UPDATE_LOG.md)

---

**开始构建你的应用吧!** 🚀

有问题? 查看组件源码获取更多灵感!
