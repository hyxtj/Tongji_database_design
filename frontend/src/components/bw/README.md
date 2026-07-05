# 黑白主题组件库使用指南

## 概述

这是一套为城市交通监控系统设计的黑白主题组件库,所有组件都完美支持明暗双模式切换。

## 组件列表

### 1. BWCard - 卡片组件

通用卡片容器,支持头部、内容、底部插槽。

#### 使用示例

```vue
<template>
  <!-- 基础卡片 -->
  <BWCard title="交通状态">
    <p>这是卡片内容</p>
  </BWCard>

  <!-- 可点击卡片 -->
  <BWCard title="统计数据" variant="stat" hoverable @click="handleClick">
    <h2>1,234</h2>
    <p>今日流量</p>
  </BWCard>

  <!-- 带额外内容的卡片 -->
  <BWCard title="事件列表">
    <template #extra>
      <BWButton size="small">查看更多</BWButton>
    </template>
    <ul>...</ul>
    <template #footer>
      <p>最后更新: 2025-01-11 10:00</p>
    </template>
  </BWCard>
</template>
```

#### Props

- `title`: String - 卡片标题
- `variant`: 'default' | 'accent' | 'stat' - 卡片样式
- `hoverable`: Boolean - 是否显示悬停效果

### 2. BWButton - 按钮组件

多种样式和尺寸的按钮,支持加载状态。

#### 使用示例

```vue
<template>
  <!-- 不同类型 -->
  <BWButton>默认按钮</BWButton>
  <BWButton type="primary">主要按钮</BWButton>
  <BWButton type="text">文本按钮</BWButton>
  <BWButton type="danger">危险按钮</BWButton>

  <!-- 不同尺寸 -->
  <BWButton size="small">小按钮</BWButton>
  <BWButton size="medium">中按钮</BWButton>
  <BWButton size="large">大按钮</BWButton>

  <!-- 加载和禁用 -->
  <BWButton :loading="loading" @click="submit">提交</BWButton>
  <BWButton disabled>禁用按钮</BWButton>
</template>
```

#### Props

- `type`: 'default' | 'primary' | 'text' | 'danger'
- `size`: 'small' | 'medium' | 'large'
- `loading`: Boolean - 加载状态
- `disabled`: Boolean - 禁用状态

### 3. BWInput - 输入框组件

带标签、图标、清除功能的输入框。

#### 使用示例

```vue
<template>
  <!-- 基础输入框 -->
  <BWInput 
    v-model="email" 
    label="邮箱地址"
    placeholder="请输入邮箱"
    required
  />

  <!-- 带图标 -->
  <BWInput 
    v-model="search"
    placeholder="搜索..."
    prefix-icon="🔍"
    clearable
  />

  <!-- 密码输入 -->
  <BWInput 
    v-model="password"
    type="password"
    label="密码"
    :error="passwordError"
  />
</template>
```

#### Props

- `modelValue`: String | Number - 绑定值
- `type`: String - 输入类型
- `label`: String - 标签文本
- `placeholder`: String - 占位符
- `prefixIcon` / `suffixIcon`: String - 图标
- `clearable`: Boolean - 显示清除按钮
- `required`: Boolean - 必填标记
- `error`: String - 错误信息

### 4. BWStatusBadge - 状态徽章

显示交通状态或系统状态的彩色徽章。

#### 使用示例

```vue
<template>
  <!-- 交通状态 -->
  <BWStatusBadge status="smooth" />  <!-- 畅通 -->
  <BWStatusBadge status="slow" />    <!-- 缓慢 -->
  <BWStatusBadge status="congested" /> <!-- 拥堵 -->
  <BWStatusBadge status="severe" />  <!-- 严重拥堵 -->

  <!-- 系统状态 -->
  <BWStatusBadge status="success">操作成功</BWStatusBadge>
  <BWStatusBadge status="warning">需要注意</BWStatusBadge>
  <BWStatusBadge status="error">发生错误</BWStatusBadge>

  <!-- 无指示点 -->
  <BWStatusBadge status="info" :show-dot="false">信息</BWStatusBadge>
</template>
```

#### Props

- `status`: 'smooth' | 'slow' | 'congested' | 'severe' | 'success' | 'warning' | 'error' | 'info' | 'default'
- `showDot`: Boolean - 显示动态指示点

### 5. BWProgressBar - 进度条

显示进度或完成度的进度条组件。

#### 使用示例

```vue
<template>
  <!-- 基础进度条 -->
  <BWProgressBar :percentage="60" label="数据加载" />

  <!-- 不同状态 -->
  <BWProgressBar :percentage="100" status="success" />
  <BWProgressBar :percentage="80" status="warning" />
  <BWProgressBar :percentage="45" status="error" />

  <!-- 动画条纹 -->
  <BWProgressBar 
    :percentage="processing" 
    label="处理中..."
    animated 
  />

  <!-- 无信息显示 -->
  <BWProgressBar :percentage="75" :show-info="false" />
</template>
```

#### Props

- `percentage`: Number (0-100) - 进度百分比
- `status`: 'default' | 'success' | 'warning' | 'error'
- `label`: String - 进度标签
- `showInfo`: Boolean - 显示百分比信息
- `animated`: Boolean - 条纹动画

### 6. BWModal - 模态对话框

灵活的对话框组件,支持自定义内容。

#### 使用示例

```vue
<template>
  <BWButton @click="modalVisible = true">打开对话框</BWButton>

  <!-- 基础对话框 -->
  <BWModal 
    v-model="modalVisible" 
    title="确认操作"
    @confirm="handleConfirm"
  >
    <p>您确定要执行此操作吗?</p>
  </BWModal>

  <!-- 自定义对话框 -->
  <BWModal 
    v-model="customModal"
    size="large"
    :mask-closable="false"
    :show-footer="false"
  >
    <template #header>
      <h3>自定义标题</h3>
    </template>
    
    <div>自定义内容区域</div>
    
    <template #footer>
      <BWButton @click="customModal = false">取消</BWButton>
      <BWButton type="primary" :loading="submitting" @click="submit">
        提交
      </BWButton>
    </template>
  </BWModal>
</template>

<script setup>
import { ref } from 'vue'

const modalVisible = ref(false)
const customModal = ref(false)
const submitting = ref(false)

const handleConfirm = () => {
  console.log('已确认')
  modalVisible.value = false
}

const submit = async () => {
  submitting.value = true
  // 执行提交逻辑
  await new Promise(resolve => setTimeout(resolve, 2000))
  submitting.value = false
  customModal.value = false
}
</script>
```

#### Props

- `modelValue`: Boolean - 显示/隐藏
- `title`: String - 标题
- `size`: 'small' | 'medium' | 'large'
- `closable`: Boolean - 显示关闭按钮
- `maskClosable`: Boolean - 点击遮罩关闭
- `showFooter`: Boolean - 显示底部
- `loading`: Boolean - 确认按钮加载状态

### 7. BWLoading - 加载指示器

多种样式的加载动画。

#### 使用示例

```vue
<template>
  <!-- 内联加载 -->
  <BWLoading type="circle" text="加载中..." />
  <BWLoading type="dots" />
  <BWLoading type="bars" />

  <!-- 全屏加载 -->
  <BWLoading v-if="loading" type="circle" text="正在处理..." fullscreen />
</template>

<script setup>
import { ref } from 'vue'

const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    // 加载数据
    await fetchData()
  } finally {
    loading.value = false
  }
}
</script>
```

#### Props

- `type`: 'circle' | 'dots' | 'bars' - 加载样式
- `text`: String - 加载文本
- `fullscreen`: Boolean - 全屏模式

## 导入方式

### 单个组件导入

```javascript
import { BWCard, BWButton } from '@/components/bw'
```

### 全部导入

```javascript
import * as BWComponents from '@/components/bw'
```

## 主题适配

所有组件都使用 CSS 变量,自动适配明暗主题:

```css
/* 在 theme-bw.css 中定义的变量 */
--bg-primary      /* 主背景色 */
--bg-secondary    /* 次级背景 */
--bg-elevated     /* 浮层背景 */
--text-primary    /* 主文本 */
--text-secondary  /* 次要文本 */
--border-primary  /* 边框颜色 */
/* ... 更多变量 */
```

## 组合使用示例

```vue
<template>
  <BWCard title="用户信息" hoverable>
    <template #extra>
      <BWStatusBadge status="success">在线</BWStatusBadge>
    </template>
    
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
    />
    
    <BWProgressBar 
      :percentage="profileCompletion" 
      label="资料完整度"
      :status="profileCompletion === 100 ? 'success' : 'warning'"
    />
    
    <template #footer>
      <div style="display: flex; gap: 12px; justify-content: flex-end;">
        <BWButton @click="reset">重置</BWButton>
        <BWButton type="primary" :loading="saving" @click="save">
          保存
        </BWButton>
      </div>
    </template>
  </BWCard>

  <!-- 确认对话框 -->
  <BWModal 
    v-model="showConfirm"
    title="保存确认"
    @confirm="handleSave"
  >
    <p>确定要保存这些更改吗?</p>
  </BWModal>

  <!-- 全屏加载 -->
  <BWLoading v-if="loading" text="保存中..." fullscreen />
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  BWCard, 
  BWButton, 
  BWInput, 
  BWStatusBadge, 
  BWProgressBar, 
  BWModal, 
  BWLoading 
} from '@/components/bw'

const form = ref({ name: '', email: '' })
const errors = ref({})
const saving = ref(false)
const loading = ref(false)
const showConfirm = ref(false)

const profileCompletion = computed(() => {
  let completion = 0
  if (form.value.name) completion += 50
  if (form.value.email) completion += 50
  return completion
})

const save = () => {
  if (validateForm()) {
    showConfirm.value = true
  }
}

const handleSave = async () => {
  showConfirm.value = false
  loading.value = true
  try {
    // 保存逻辑
    await api.saveProfile(form.value)
  } finally {
    loading.value = false
  }
}

const reset = () => {
  form.value = { name: '', email: '' }
  errors.value = {}
}

const validateForm = () => {
  errors.value = {}
  if (!form.value.name) {
    errors.value.name = '请输入姓名'
    return false
  }
  return true
}
</script>
```

## 样式定制

如果需要调整组件样式,可以通过 CSS 变量或深度选择器:

```vue
<style>
/* 修改主题变量 */
:root {
  --text-primary: #000000;
  --bg-elevated: #ffffff;
}

/* 深度选择器 */
.my-component :deep(.bw-button) {
  border-radius: 20px;
}
</style>
```

## 注意事项

1. **主题变量**: 所有组件依赖 `theme-bw.css` 中定义的 CSS 变量
2. **响应式**: 大部分组件已内置响应式设计
3. **无障碍**: 组件遵循基本的无障碍设计原则
4. **性能**: 使用 `<Transition>` 确保动画流畅
5. **TypeScript**: 如需 TS 支持,可添加 `.d.ts` 类型定义文件

## 更新日志

### v1.0.0 (2025-01-11)
- ✅ 初始版本发布
- ✅ 7个核心组件
- ✅ 完整明暗主题支持
- ✅ 响应式设计
- ✅ 动画效果
