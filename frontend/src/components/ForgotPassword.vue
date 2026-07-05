<template>
  <el-dialog
    v-model="visible"
    title="重置密码"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="forgot-password-container">
      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps">
        <el-step title="输入邮箱" />
        <el-step title="验证码" />
        <el-step title="设置新密码" />
      </el-steps>

      <!-- 步骤1: 输入邮箱 -->
      <div v-show="currentStep === 0" class="step-content">
        <el-form :model="form" :rules="rules" ref="emailFormRef">
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              placeholder="请输入注册邮箱"
              size="large"
              :prefix-icon="Message"
            />
          </el-form-item>
        </el-form>
        <div class="form-actions">
          <el-button @click="handleClose" size="large">取消</el-button>
          <el-button type="primary" @click="sendCode" :loading="loading" size="large">
            发送验证码
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 输入验证码 -->
      <div v-show="currentStep === 1" class="step-content">
        <el-alert
          title="验证码已发送"
          :description="`验证码已发送到 ${form.email},请查收邮件`"
          type="success"
          :closable="false"
          show-icon
          class="alert"
        />
        <el-form :model="form" :rules="rules" ref="codeFormRef">
          <el-form-item prop="code">
            <el-input
              v-model="form.code"
              placeholder="请输入6位验证码"
              size="large"
              maxlength="6"
              :prefix-icon="Key"
            />
          </el-form-item>
        </el-form>
        <div class="form-actions">
          <el-button @click="currentStep = 0" size="large">上一步</el-button>
          <el-button type="primary" @click="verifyCode" size="large">
            下一步
          </el-button>
        </div>
        <div class="resend-container">
          <el-button
            link
            type="primary"
            @click="sendCode"
            :disabled="countdown > 0"
          >
            {{ countdown > 0 ? `${countdown}秒后重新发送` : '重新发送验证码' }}
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 设置新密码 -->
      <div v-show="currentStep === 2" class="step-content">
        <el-form :model="form" :rules="rules" ref="passwordFormRef">
          <el-form-item prop="newPassword">
            <el-input
              v-model="form.newPassword"
              type="password"
              placeholder="请输入新密码(8-20位,含字母和数字)"
              size="large"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              size="large"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>
        </el-form>
        <div class="form-actions">
          <el-button @click="currentStep = 1" size="large">上一步</el-button>
          <el-button type="primary" @click="resetPassword" :loading="loading" size="large">
            完成重置
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Message, Key, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const userStore = useUserStore()

const visible = ref(props.modelValue)
const currentStep = ref(0)
const loading = ref(false)
const countdown = ref(0)
let countdownTimer = null

const form = reactive({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})

const emailFormRef = ref(null)
const codeFormRef = ref(null)
const passwordFormRef = ref(null)

// 验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度为8-20位', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d).+$/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 监听 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
  if (!newVal) {
    resetForm()
  }
})

// 发送验证码
const sendCode = async () => {
  try {
    await emailFormRef.value?.validate()
    loading.value = true

    await userStore.forgotPassword(form.email)
    
    ElMessage.success('验证码已发送,请查收邮件')
    currentStep.value = 1
    startCountdown()
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else if (error.errors) {
      // 表单验证错误,不需要显示消息
    } else {
      ElMessage.error('发送验证码失败,请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

// 验证验证码(直接进入下一步)
const verifyCode = () => {
  if (!form.code || form.code.length !== 6) {
    ElMessage.warning('请输入6位验证码')
    return
  }
  currentStep.value = 2
}

// 重置密码
const resetPassword = async () => {
  try {
    await passwordFormRef.value?.validate()
    loading.value = true

    await userStore.resetPassword(form.email, form.code, form.newPassword)
    
    ElMessage.success('密码重置成功,请使用新密码登录')
    emit('success')
    visible.value = false
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('密码重置失败,请检查验证码是否正确')
    }
  } finally {
    loading.value = false
  }
}

// 倒计时
const startCountdown = () => {
  countdown.value = 60
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

// 重置表单
const resetForm = () => {
  currentStep.value = 0
  form.email = ''
  form.code = ''
  form.newPassword = ''
  form.confirmPassword = ''
  countdown.value = 0
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  emailFormRef.value?.resetFields()
  codeFormRef.value?.resetFields()
  passwordFormRef.value?.resetFields()
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.forgot-password-container {
  padding: 20px 0;
}

.steps {
  margin-bottom: 40px;
}

.step-content {
  margin-top: 20px;
}

.alert {
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.form-actions .el-button {
  min-width: 100px;
}

.resend-container {
  text-align: center;
  margin-top: 15px;
}

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

:deep(.el-step__title) {
  color: var(--text-secondary);
}

:deep(.el-step__title.is-process) {
  color: var(--primary-color);
}

:deep(.el-step__title.is-success) {
  color: var(--color-success);
}

:deep(.el-step__head.is-process) {
  color: var(--primary-color);
  border-color: var(--primary-color);
}

:deep(.el-step__head.is-success) {
  color: var(--color-success);
  border-color: var(--color-success);
}

:deep(.el-input__wrapper) {
  background-color: rgba(0, 243, 255, 0.05);
  box-shadow: 0 0 0 1px var(--border-primary) inset;
}

[data-theme='light'] :deep(.el-input__wrapper) {
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

:deep(.el-alert--success) {
  background-color: rgba(0, 255, 157, 0.1);
  color: var(--text-primary);
  border: 1px solid rgba(0, 255, 157, 0.2);
}

:deep(.el-alert__title) {
  color: var(--color-success);
}

:deep(.el-alert__description) {
  color: var(--text-secondary);
}
</style>
