<template>
  <div 
    class="register-container"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    @click="handleContainerClick"
    :style="containerStyle"
  >
    <!-- 科技感背景 -->
    <div class="tech-background">
      <div class="grid-overlay"></div>
      
      <!-- 新增：雷达扫描 -->
      <div class="radar-scan"></div>
      <!-- 新增：六边形装饰 -->
      <div class="hexagons">
        <div class="hex hex-1"></div>
        <div class="hex hex-2"></div>
        <div class="hex hex-3"></div>
      </div>

      <div class="particles">
        <div v-for="n in 20" :key="n" class="particle" :style="getParticleStyle(n)"></div>
      </div>
      <div class="meteors">
        <div v-for="n in 10" :key="n" class="meteor" :style="getMeteorStyle(n)"></div>
      </div>
      <div class="glow-orb orb-2"></div>
    </div>

    <!-- 注册卡片 -->
    <div class="register-card-wrapper">
      <div class="register-card" :style="cardStyle">
        <!-- Logo区域 -->
        <div class="logo-section">
          <div class="logo-wrapper">
            <div class="logo-ring"></div>
            <el-icon class="logo-icon"><DataLine /></el-icon>
          </div>
          <h1 class="logo-title">城市交通监控<span class="highlight">系统</span></h1>
          <p class="logo-subtitle">URBAN TRAFFIC MONITOR // NEW USER REGISTRATION</p>
        </div>

        <!-- 第一步:填写注册信息 -->
        <el-form
          v-if="step === 1"
          ref="registerFormRef"
          :model="registerForm"
          :rules="rules"
          class="register-form"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                clearable
                class="tech-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><User /></el-icon>
                </template>
              </el-input>
            </div>
          </el-form-item>

          <el-form-item prop="email">
            <div class="input-wrapper">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱地址"
                clearable
                class="tech-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><Message /></el-icon>
                </template>
              </el-input>
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="设置密码"
                show-password
                clearable
                class="tech-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><Lock /></el-icon>
                </template>
              </el-input>
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <div class="input-wrapper">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                show-password
                clearable
                class="tech-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><Key /></el-icon>
                </template>
              </el-input>
            </div>
          </el-form-item>

          <div class="password-hint tech-hint">
            <p class="hint-title">安全要求:</p>
            <ul class="hint-list">
              <li>长度: 6-20 个字符</li>
              <li>复杂度: 需包含字母、数字或符号中的两种</li>
            </ul>
          </div>

          <el-button
            type="primary"
            class="register-button tech-button"
            :loading="loading"
            @click="handleRegister"
          >
            <span v-if="!loading">立即注册</span>
            <span v-else>处理中...</span>
          </el-button>

          <div class="login-link">
            <span class="text-muted">已有账号?</span>
            <router-link to="/login" class="tech-link">登录系统</router-link>
          </div>
        </el-form>

        <!-- 第二步:验证邮箱 -->
        <div v-if="step === 2" class="verification-step">
          <div class="verification-icon-wrapper">
            <el-icon class="verification-icon"><Message /></el-icon>
          </div>
          <h2 class="verification-title">验证码已发送</h2>
          <p class="verification-subtitle">
            已发送至: <strong class="highlight">{{ registerForm.email }}</strong>
          </p>

          <el-form 
            :model="verificationForm" 
            class="verification-form"
            @submit.prevent="handleVerify"
          >
            <el-form-item>
              <div class="input-wrapper">
                <el-input
                  v-model="verificationForm.code"
                  placeholder="输入6位验证码"
                  maxlength="6"
                  clearable
                  class="tech-input code-input"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><Key /></el-icon>
                  </template>
                </el-input>
              </div>
            </el-form-item>

            <el-button
              type="primary"
              class="verify-button tech-button"
              :loading="verifying"
              @click="handleVerify"
            >
              <span v-if="!verifying">验证身份</span>
              <span v-else>验证中...</span>
            </el-button>

            <el-button
              type="text"
              class="resend-button tech-text-btn"
              :disabled="resendCountdown > 0"
              @click="handleResendCode"
            >
              {{ resendCountdown > 0 ? `${resendCountdown}秒后重试` : '重新发送验证码' }}
            </el-button>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="footer">
      <p class="footer-text">SYSTEM VERSION 2.5.0 | SECURE CONNECTION ESTABLISHED</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Key, DataLine, Sunny, Moon } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const userStore = useUserStore()

// 鼠标移动效果
const mouseX = ref(0)
const mouseY = ref(0)

const handleMouseMove = (e) => {
  const { clientX, clientY, currentTarget } = e
  const { clientWidth, clientHeight } = currentTarget
  
  // 计算归一化坐标 (-1 到 1)
  mouseX.value = (clientX / clientWidth) * 2 - 1
  mouseY.value = (clientY / clientHeight) * 2 - 1
}

const handleMouseLeave = () => {
  mouseX.value = 0
  mouseY.value = 0
}

const handleContainerClick = (e) => {
  createClickEffect(e.clientX, e.clientY)
}

const createClickEffect = (x, y) => {
  const effect = document.createElement('div')
  effect.className = 'click-effect'
  effect.style.left = `${x}px`
  effect.style.top = `${y}px`
  document.body.appendChild(effect)
  
  setTimeout(() => {
    effect.remove()
  }, 1000)
}

const cardStyle = computed(() => {
  const rotateX = mouseY.value * -5 // 最大旋转角度
  const rotateY = mouseX.value * 5
  
  return {
    transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`,
    transition: 'transform 0.1s ease-out'
  }
})

const containerStyle = computed(() => {
  return {
    '--mouse-x': mouseX.value,
    '--mouse-y': mouseY.value
  }
})

const registerFormRef = ref()
const loading = ref(false)
const verifying = ref(false)
const step = ref(1)  // 1: 注册表单, 2: 验证邮箱
const resendCountdown = ref(0)  // 重发倒计时

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const verificationForm = reactive({
  code: ''
})

let userId = null  // 存储注册后的用户ID

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else if (value.length > 20) {
    callback(new Error('密码长度不能超过20位'))
  } else {
    // 检查是否包含至少两种字符类型
    const hasLetter = /[a-zA-Z]/.test(value)
    const hasDigit = /\d/.test(value)
    const hasSymbol = /[!@#$%^&*()_+\-=\[\]{};:'",.<>?/\\|`~]/.test(value)
    
    const typeCount = [hasLetter, hasDigit, hasSymbol].filter(Boolean).length
    
    if (typeCount < 2) {
      callback(new Error('密码必须至少包含字母、数字、符号中的两种'))
    } else {
      // 如果已经输入了确认密码,则重新验证确认密码
      if (registerForm.confirmPassword !== '') {
        registerFormRef.value?.validateField('confirmPassword')
      }
      callback()
    }
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const getParticleStyle = (n) => {
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 5}s`,
    opacity: Math.random() * 0.5 + 0.1
  }
}

const getMeteorStyle = (n) => {
  const top = Math.random() * 60 - 20 // -20% to 40%
  const left = Math.random() * 100 + 20 // 20% to 120%
  const delay = Math.random() * 5
  const duration = Math.random() * 1 + 1.5 // Faster: 1.5s - 2.5s
  return {
    top: `${top}%`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await api.post('/auth/register', {
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password
        })
        
        userId = response.data.user_id
        step.value = 2
        startResendCountdown()
        ElMessage.success('验证码已发送到您的邮箱')
      } catch (error) {
        console.error('注册失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleVerify = async () => {
  if (!verificationForm.code) {
    ElMessage.warning('请输入验证码')
    return
  }

  verifying.value = true
  try {
    const response = await api.post('/auth/verify-email', {
      email: registerForm.email,
      code: verificationForm.code
    })
    
    // 保存token和用户信息
    userStore.token = response.data.access_token
    userStore.user = response.data.user
    localStorage.setItem('token', response.data.access_token)
    
    ElMessage.success('邮箱验证成功!')
    router.push('/')
  } catch (error) {
    console.error('验证失败:', error)
  } finally {
    verifying.value = false
  }
}

const handleResendCode = async () => {
  try {
    await api.post('/auth/resend-code', {
      email: registerForm.email
    })
    
    ElMessage.success('验证码已重新发送')
    startResendCountdown()
  } catch (error) {
    console.error('发送失败:', error)
  }
}

const startResendCountdown = () => {
  resendCountdown.value = 60
  const timer = setInterval(() => {
    resendCountdown.value--
    if (resendCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 页面加载动画
onMounted(() => {
  const card = document.querySelector('.register-card')
  if (card) {
    setTimeout(() => {
      card.classList.add('active')
    }, 100)
  }
})
</script>

<style>
/* 全局点击特效样式 */
.click-effect {
  position: fixed;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: transparent;
  border: 2px solid #00f3ff;
  transform: translate(-50%, -50%) scale(0);
  animation: ripple 0.6s ease-out forwards;
  pointer-events: none;
  z-index: 9999;
  box-shadow: 0 0 10px #00f3ff;
}

@keyframes ripple {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
    border-width: 2px;
  }
  100% {
    transform: translate(-50%, -50%) scale(4);
    opacity: 0;
    border-width: 0;
  }
}
</style>

<!-- 全局样式覆盖 - 解决主题切换问题 -->
<style>
/* 白天模式 - 强制覆盖 */
[data-theme='light'] .register-container {
  background-color: #f0f2f5 !important;
  color: #333 !important;
}

[data-theme='light'] .tech-background {
  background: #f0f2f5 !important;
  display: block !important;
}


[data-theme='light'] .grid-overlay {
  background-image: 
    linear-gradient(rgba(0, 243, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 243, 255, 0.08) 1px, transparent 1px) !important;
  mask-image: radial-gradient(circle at 50% 50%, black 40%, transparent 80%) !important;
}

[data-theme='light'] .particle {
  background: rgba(0, 0, 0, 0.2) !important;
}

[data-theme='light'] .meteor {
  background: linear-gradient(to right, transparent, rgba(0, 0, 0, 0.0)) !important;
}

[data-theme='light'] .glow-orb {
  opacity: 0.1 !important;
  background: #0066ff !important;
}


[data-theme='light'] .grid-overlay {
  background-image: 
    linear-gradient(rgba(0, 243, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 243, 255, 0.08) 1px, transparent 1px) !important;
  mask-image: radial-gradient(circle at 50% 50%, black 40%, transparent 80%) !important;
}

[data-theme='light'] .register-card {
  background: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(0, 102, 255, 0.1) !important;
  box-shadow: 0 20px 40px rgba(0, 102, 255, 0.1) !important;
}

[data-theme='light'] .logo-title {
  color: #333 !important;
}

[data-theme='light'] .logo-subtitle {
  color: rgba(0, 0, 0, 0.5) !important;
}

[data-theme='light'] .register-container .tech-input .el-input__wrapper {
  background: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  color: #333 !important;
}

[data-theme='light'] .register-container .tech-input .el-input__inner {
  color: #333 !important;
}

[data-theme='light'] .register-container .tech-input .el-input__inner::placeholder {
  color: rgba(0, 0, 0, 0.4) !important;
}

[data-theme='light'] .register-container .input-icon {
  color: rgba(0, 0, 0, 0.4) !important;
}

[data-theme='light'] .verification-title {
  color: #333 !important;
}

[data-theme='light'] .verification-subtitle {
  color: rgba(0, 0, 0, 0.6) !important;
}

[data-theme='light'] .tech-text-btn {
  color: rgba(0, 0, 0, 0.5) !important;
}

[data-theme='light'] .tech-text-btn:hover:not(:disabled) {
  color: #0066ff !important;
}

[data-theme='light'] .text-muted {
  color: rgba(0, 0, 0, 0.5) !important;
}

[data-theme='light'] .tech-link {
  color: #0066ff !important;
}

[data-theme='light'] .footer-text {
  color: rgba(0, 0, 0, 0.3) !important;
}

[data-theme='light'] .hint-title {
  color: #0066ff !important;
}

[data-theme='light'] .hint-list {
  color: rgba(0, 0, 0, 0.6) !important;
}

[data-theme='light'] .tech-hint {
  background: rgba(0, 0, 0, 0.03) !important;
  border: 1px solid rgba(0, 0, 0, 0.05) !important;
}
</style>

<style scoped>
.register-container {
  min-height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background-color: #050508;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  color: #fff;
  transition: background-color 0.5s ease;
}

/* 科技感背景 - 升级版 */
.tech-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #050508 100%);
  overflow: hidden;
  pointer-events: none; /* 关键修复：允许点击穿透 */
}

.grid-overlay {
  position: absolute;
  top: -10%;
  left: -10%;
  width: 120%;
  height: 120%;
  background-image: 
    linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(circle at 50% 50%, black 40%, transparent 80%);
  transform: translate(calc(var(--mouse-x, 0) * -20px), calc(var(--mouse-y, 0) * -20px));
  transition: transform 0.1s ease-out;
  pointer-events: none; /* 关键修复：允许点击穿透 */
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  animation: floatOrb 15s ease-in-out infinite alternate;
  pointer-events: none;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: #00f3ff;
  bottom: -150px;
  right: -150px;
  opacity: 0.15;
  transform: translate(calc(var(--mouse-x, 0) * -40px), calc(var(--mouse-y, 0) * -40px));
  transition: transform 0.2s ease-out;
}

@keyframes floatOrb {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-50px, -50px); }
}

/* 雷达扫描 */
.radar-scan {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 150vmax;
  height: 150vmax;
  transform: translate(-50%, -50%);
  background: conic-gradient(from 0deg, transparent 0%, transparent 80%, rgba(0, 243, 255, 0.03) 100%);
  border-radius: 50%;
  animation: radarSpin 15s linear infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes radarSpin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

/* 六边形装饰 */
.hexagons {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.hex {
  position: absolute;
  width: 100px;
  height: 115px;
  background: rgba(0, 243, 255, 0.02);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  animation: floatHex 8s ease-in-out infinite;
  border: 1px solid rgba(0, 243, 255, 0.05);
}

.hex-1 {
  top: 15%;
  left: 10%;
  animation-delay: 0s;
  transform: scale(2);
}

.hex-2 {
  bottom: 20%;
  right: 15%;
  animation-delay: 2s;
  transform: scale(3);
  background: rgba(0, 102, 255, 0.02);
  border-color: rgba(0, 102, 255, 0.05);
}

.hex-3 {
  top: 40%;
  right: 25%;
  animation-delay: 4s;
  transform: scale(1.5);
}

@keyframes floatHex {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

/* 注册卡片包装器 - 用于3D效果 */
.register-card-wrapper {
  position: relative;
  z-index: 100;
  perspective: 1000px;
  pointer-events: auto;
}

/* 注册卡片 - 高级磨砂玻璃质感 */
.register-card {
  width: 100%;
  max-width: 440px;
  padding: 40px;
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  pointer-events: auto;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
  transform-style: preserve-3d; /* 保持子元素3D */
}

.register-card.active {
  opacity: 1;
  transform: translateY(0);
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 30px;
  transform: translateZ(20px); /* 3D 凸起 */
}

.logo-wrapper {
  position: relative;
  width: 70px;
  height: 70px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 243, 255, 0.1), rgba(0, 102, 255, 0.1));
  border-radius: 50%; /* Changed to circle */
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
  border: 1px solid rgba(0, 243, 255, 0.2);
}

.logo-ring {
  position: absolute;
  width: 110%;
  height: 110%;
  border: 2px dashed #00f3ff;
  border-radius: 50%;
  animation: rotate 10s linear infinite;
  pointer-events: none;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.logo-icon {
  font-size: 32px;
  color: #fff;
  filter: drop-shadow(0 0 5px rgba(0, 243, 255, 0.5));
}

.logo-title {
  font-size: 22px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.highlight {
  background: linear-gradient(120deg, #00f3ff, #0066ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}

.logo-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.register-form {
  transform: translateZ(30px); /* 表单悬浮 */
  pointer-events: auto;
}

/* 输入框样式 - 现代简约 */
.input-wrapper {
  margin-bottom: 5px;
  width: 100%;
  box-sizing: border-box;
}

.tech-input {
  width: 100%;
}

:deep(.el-form-item__content) {
  width: 100%;
}

.tech-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: none !important;
  border-radius: 12px !important;
  padding: 0 15px !important;
  height: 48px;
  transition: all 0.3s ease;
  width: 100%; /* 确保宽度一致 */
  box-sizing: border-box; /* 确保盒模型一致 */
}

.tech-input :deep(.el-input__wrapper):hover {
  background: rgba(255, 255, 255, 0.08) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.tech-input :deep(.el-input__wrapper.is-focus) {
  background: rgba(0, 243, 255, 0.05) !important;
  border-color: #00f3ff !important;
  box-shadow: 0 0 0 2px rgba(0, 243, 255, 0.1) !important;
}

.tech-input :deep(.el-input__inner) {
  color: #fff !important;
  font-size: 14px;
}

.tech-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}

.input-icon {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.3s;
}

.tech-input :deep(.el-input__wrapper.is-focus) .input-icon {
  color: #00f3ff;
}

/* 处理浏览器自动填充样式 */
.tech-input :deep(.el-input__inner:-webkit-autofill),
.tech-input :deep(.el-input__inner:-webkit-autofill:hover),
.tech-input :deep(.el-input__inner:-webkit-autofill:focus),
.tech-input :deep(.el-input__inner:-webkit-autofill:active) {
  -webkit-text-fill-color: #fff !important;
  transition: background-color 5000s ease-in-out 0s;
  caret-color: #fff;
}

[data-theme='light'] .register-container .tech-input :deep(.el-input__inner:-webkit-autofill) {
  -webkit-text-fill-color: #333 !important;
  caret-color: #333;
}

/* 密码提示 */
.tech-hint {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 20px;
}

.hint-title {
  font-size: 12px;
  font-weight: 600;
  color: #00f3ff;
  margin: 0 0 8px;
}

.hint-list {
  margin: 0;
  padding-left: 20px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

/* 按钮样式 - 渐变光效 */
.tech-button {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #00f3ff 0%, #0066ff 100%);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 102, 255, 0.4);
  background: linear-gradient(135deg, #33f6ff 0%, #3385ff 100%);
}

.tech-button:active {
  transform: translateY(0);
}

/* 登录链接 */
.login-link {
  text-align: center;
  margin-top: 25px;
  font-size: 13px;
}

.text-muted {
  color: rgba(255, 255, 255, 0.4);
  margin-right: 8px;
}

.tech-link {
  color: #00f3ff;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
}

.tech-link:hover {
  color: #fff;
  text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
}

/* 验证步骤样式 */
.verification-step {
  text-align: center;
  padding: 10px 0;
  transform: translateZ(30px); /* 验证步骤悬浮 */
  pointer-events: auto;
}

.verification-icon-wrapper {
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 243, 255, 0.1);
  border-radius: 50%;
  color: #00f3ff;
}

.verification-icon {
  font-size: 30px;
}

.verification-title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 10px;
}

.verification-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 30px;
}

.code-input :deep(.el-input__inner) {
  text-align: center;
  letter-spacing: 5px;
  font-size: 18px;
  font-weight: 700;
}

.tech-text-btn {
  margin-top: 15px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.tech-text-btn:hover:not(:disabled) {
  color: #00f3ff;
}

/* 页脚 */
.footer {
  position: absolute;
  bottom: 20px;
  width: 100%;
  text-align: center;
}

.footer-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.2);
  letter-spacing: 1px;
}

/* 粒子和流星动画 */
.particles, .meteors {
  pointer-events: none;
}

.particle {
  background: rgba(0, 243, 255, 0.5);
}

.meteor {
  background: linear-gradient(to right, transparent, rgba(0, 243, 255, 0.8));
}

/* 响应式 */
@media (max-width: 480px) {
  .register-card {
    padding: 30px 20px;
    margin: 20px;
    border-radius: 20px;
  }
}
</style>
