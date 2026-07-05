<template>
  <div 
    class="login-container" 
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

    <!-- 登录卡片 -->
    <div class="login-card-wrapper">
      <div class="login-card glass-effect" :style="cardStyle">
        <!-- 装饰角标 -->
        <div class="corner corner-tl"></div>
        <div class="corner corner-tr"></div>
        <div class="corner corner-bl"></div>
        <div class="corner corner-br"></div>

        <!-- Logo区域 -->
        <div class="logo-section">
          <div class="logo-wrapper">
            <div class="logo-ring"></div>
            <!-- 环绕星星 -->
            <div class="logo-orbit">
              <div class="orbit-dot dot-1">✦</div>
              <div class="orbit-dot dot-2">✦</div>
              <div class="orbit-dot dot-3">✦</div>
            </div>
            <div class="logo-icon">🚦</div>
          </div>
          <h1 class="logo-title">城市交通监控<span class="highlight">系统</span></h1>
          <p class="logo-subtitle">URBAN TRAFFIC MONITOR </p>
        </div>

        <!-- 登录表单 -->
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="email">
            <div class="input-wrapper">
              <el-input
                v-model="loginForm.email"
                placeholder="用户名 / 邮箱"
                clearable
                class="tech-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><User /></el-icon>
                </template>
              </el-input>
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
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

          <div class="form-footer">
            <el-checkbox v-model="loginForm.remember" class="tech-checkbox">保持连接</el-checkbox>
            <a href="#" class="forgot-link" @click.prevent="showForgotPassword">忘记密钥?</a>
          </div>

          <el-button
            type="primary"
            class="login-button tech-button"
            :loading="loading"
            @click="handleLogin"
          >
            <span class="btn-content">
              <span v-if="!loading">登录系统</span>
              <span v-else>登录中...</span>
            </span>
          </el-button>

          <div class="register-link">
            <span class="text-muted">还没有账号?</span>
            <router-link to="/register" class="tech-link">立即注册</router-link>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="footer">
      <p class="footer-text">SYSTEM VERSION 2.5.0 | SECURE CONNECTION ESTABLISHED</p>
    </div>

    <!-- 忘记密码对话框 -->
    <ForgotPassword
      v-model="showForgotPasswordDialog"
      @success="handleForgotPasswordSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Sunny, Moon } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import ForgotPassword from '@/components/ForgotPassword.vue'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)
const showForgotPasswordDialog = ref(false)

// 鼠标交互状态
const mouseX = ref(0)
const mouseY = ref(0)

const handleMouseMove = (e) => {
  const { clientX, clientY, currentTarget } = e
  const { width, height } = currentTarget.getBoundingClientRect()
  
  // 计算归一化坐标 (-1 到 1)
  mouseX.value = (clientX / width) * 2 - 1
  mouseY.value = (clientY / height) * 2 - 1
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
    transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`
  }
})

const containerStyle = computed(() => {
  return {
    '--mouse-x': mouseX.value,
    '--mouse-y': mouseY.value
  }
})

const loginForm = reactive({
  email: '',
  password: '',
  remember: false
})

const loginRules = {
  email: [
    { required: true, message: '请输入邮箱或用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
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

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    await userStore.login({
      email: loginForm.email,
      password: loginForm.password,
      remember: loginForm.remember
    })

    ElMessage.success('身份验证成功 / ACCESS GRANTED')
    router.push('/dashboard')
  } catch (error) {
    if (error !== false) {
      console.error('Login error:', error)
      ElMessage.error(error.response?.data?.message || '登录失败,请检查用户名和密码')
    }
  } finally {
    loading.value = false
  }
}

// 显示忘记密码对话框
const showForgotPassword = () => {
  showForgotPasswordDialog.value = true
}

// 忘记密码成功回调
const handleForgotPasswordSuccess = () => {
  // 可以选择性地自动填充邮箱
  // loginForm.email = xxx
}

// 页面加载动画
onMounted(() => {
  const card = document.querySelector('.login-card-wrapper')
  if (card) {
    setTimeout(() => {
      card.classList.add('active')
    }, 100)
  }
  
  // 加载记住的邮箱
  const rememberedEmail = userStore.getRememberedEmail()
  if (rememberedEmail) {
    loginForm.email = rememberedEmail
    loginForm.remember = true
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
[data-theme='light'] .login-container {
  background-color: #f0f2f5 !important;
  color: #333 !important;
}

[data-theme='light'] .tech-background {
  background: #f0f2f5 !important;
  display: block !important;
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

[data-theme='light'] .login-card {
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

[data-theme='light'] .login-container .tech-input .el-input__wrapper {
  background: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  color: #333 !important;
}

[data-theme='light'] .login-container .tech-input .el-input__inner {
  color: #333 !important;
}

[data-theme='light'] .login-container .tech-input .el-input__inner::placeholder {
  color: rgba(0, 0, 0, 0.4) !important;
}

[data-theme='light'] .login-container .input-icon {
  color: rgba(0, 0, 0, 0.4) !important;
}

[data-theme='light'] .tech-checkbox .el-checkbox__label {
  color: rgba(0, 0, 0, 0.6) !important;
}

[data-theme='light'] .forgot-link {
  color: rgba(0, 0, 0, 0.5) !important;
}

[data-theme='light'] .forgot-link:hover {
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
</style>

<style scoped>
.login-container {
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
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(circle at 50% 50%, black 40%, transparent 80%);
  transform: translate(calc(var(--mouse-x, 0) * 20px), calc(var(--mouse-y, 0) * 20px));
  transition: transform 0.1s ease-out;
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
  transform: translate(calc(var(--mouse-x, 0) * -30px), calc(var(--mouse-y, 0) * -30px));
  transition: transform 0.1s ease-out;
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

/* 登录卡片容器 - 处理入场动画 */
.login-card-wrapper {
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 100;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
  perspective: 1000px;
  pointer-events: auto;
}

.login-card-wrapper.active {
  opacity: 1;
  transform: translateY(0);
}

/* 登录卡片 - 高级磨砂玻璃质感 & 3D倾斜 */
.login-card {
  width: 100%;
  padding: 40px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  transform-style: preserve-3d;
  transition: transform 0.1s ease-out;
  pointer-events: auto;
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 40px;
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
  border-radius: 50%; /* Changed to circle to match the ring effect better */
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
  border: 1px solid rgba(0, 243, 255, 0.2);
}

.logo-ring {
  position: absolute;
  width: 110%; /* Slightly larger */
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

.login-form {
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

[data-theme='light'] .login-container .tech-input :deep(.el-input__inner:-webkit-autofill) {
  -webkit-text-fill-color: #333 !important;
  caret-color: #333;
}

/* 复选框和链接 */
.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 0 5px;
}

.tech-checkbox :deep(.el-checkbox__label) {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.tech-checkbox :deep(.el-checkbox__inner) {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.tech-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: #00f3ff;
  border-color: #00f3ff;
}

.tech-checkbox :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #00f3ff;
}

.forgot-link {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  text-decoration: none;
  transition: all 0.3s;
}

.forgot-link:hover {
  color: #00f3ff;
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

/* 注册链接 */
.register-link {
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

/* 粒子和流星动画保持不变，但颜色调整 */
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
  .login-card {
    padding: 30px 20px;
    margin: 20px;
    border-radius: 20px;
  }
}
</style>
