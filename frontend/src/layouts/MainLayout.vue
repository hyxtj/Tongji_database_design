<template>
  <div class="layout-wrapper">
    <!-- Tech Background Effects -->
    <div class="tech-background">
      <div class="grid-overlay"></div>
      <div class="particles">
        <div v-for="n in 20" :key="n" class="particle" :style="getParticleStyle(n)"></div>
      </div>
      <div class="meteors">
        <div v-for="n in 15" :key="n" class="meteor" :style="getMeteorStyle(n)"></div>
      </div>
      <div class="scan-line"></div>
    </div>

    <el-container class="main-layout">
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <el-icon><Location /></el-icon>
          <span>交通查询系统</span>
        </div>
        <el-menu
          :default-active="currentRoute"
          router
          :background-color="menuBgColor"
          :text-color="menuTextColor"
          :active-text-color="menuActiveColor"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据总览</span>
          </el-menu-item>
          <el-menu-item index="/roads">
            <el-icon><MapLocation /></el-icon>
            <span>道路管理</span>
          </el-menu-item>
          <el-menu-item index="/traffic">
            <el-icon><Odometer /></el-icon>
            <span>交通状态</span>
          </el-menu-item>
          <el-menu-item index="/smart-traffic">
            <el-icon><Cpu /></el-icon>
            <span>智能交通</span>
          </el-menu-item>
          <el-menu-item index="/route-plan">
            <el-icon><Guide /></el-icon>
            <span>路线估算</span>
          </el-menu-item>
          <el-menu-item index="/events">
            <el-icon><Warning /></el-icon>
            <span>交通事件</span>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>
          <el-divider style="margin: 10px 0; border-color: var(--border-secondary);" />
          <el-menu-item index="/analytics">
            <el-icon><BarChart /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
          <el-menu-item index="/advanced-analytics">
            <el-icon><Histogram /></el-icon>
            <span>高级分析</span>
          </el-menu-item>
          <el-menu-item index="/data-export">
            <el-icon><DocumentDownload /></el-icon>
            <span>数据导出</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-left">
            <h2>{{ currentTitle }}</h2>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><User /></el-icon>
                <span>{{ userStore.user && userStore.user.username }}</span>
                <el-icon class="el-icon--right"><ArrowDownIcon /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import {
  Location,
  Sort,
  Odometer,
  Warning,
  Tools,
  Histogram,
  Download,
  User,
  ArrowDown,
  Cpu
} from '@element-plus/icons-vue'

// 使用兼容的图标名称
const DataAnalysis = Sort
const BarChart = Histogram
const DocumentDownload = Download
const MapLocation = Location
const Setting = Tools
const ArrowDownIcon = ArrowDown

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 监听主题变化
const theme = ref(localStorage.getItem('theme') || 'dark')

// 应用主题
const applyTheme = (newTheme) => {
  document.documentElement.setAttribute('data-theme', newTheme)
  if (newTheme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  theme.value = newTheme
  localStorage.setItem('theme', newTheme)
}

// 切换主题
// const toggleTheme = () => {
//   const newTheme = theme.value === 'dark' ? 'light' : 'dark'
//   applyTheme(newTheme)
// }

// 更新主题 (from storage event)
const updateTheme = () => {
  const newTheme = localStorage.getItem('theme') || 'dark'
  if (newTheme !== theme.value) {
    applyTheme(newTheme)
  }
}

// 组件挂载时监听事件
onMounted(() => {
  applyTheme(theme.value)
  window.addEventListener('storage', updateTheme)
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  window.removeEventListener('storage', updateTheme)
  window.removeEventListener('theme-change', updateTheme)
})

// 动态菜单颜色
const menuBgColor = computed(() => {
  return 'transparent'
})

const menuTextColor = computed(() => {
  return 'var(--text-secondary)'
})

const menuActiveColor = computed(() => {
  return 'var(--primary-color)'
})

const currentRoute = computed(() => route.path)

const currentTitle = computed(() => {
  const titleMap = {
    '/dashboard': '数据总览',
    '/roads': '道路管理',
    '/traffic': '交通状态',
    '/smart-traffic': '智能交通',
    '/events': '交通事件',
    '/admin': '系统管理',
    '/analytics': '数据分析',
    '/advanced-analytics': '高级分析',
    '/data-export': '数据导出'
  }
  return titleMap[route.path] || '交通查询系统'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

// Background Effects
const getParticleStyle = (n) => {
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 5}s`,
    opacity: Math.random() * 0.5 + 0.1
  }
}

const getMeteorStyle = (n) => {
  const top = Math.random() * 100 // Cover full height
  const left = Math.random() * 100
  const delay = Math.random() * 5 // Shorter delay for more frequency
  const duration = Math.random() * 2 + 2
  return {
    top: `${top}%`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}
</script>

<style scoped>
.layout-wrapper {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--layout-bg);
}

/* Tech Background */
.tech-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  overflow: hidden; /* Prevent scrollbars */
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(var(--grid-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
  background-size: 40px 40px;
  perspective: 1000px;
  transform-style: preserve-3d;
  animation: gridMove 60s linear infinite;
  opacity: 0.5;
}

@keyframes gridMove {
  0% { transform: translateY(0); }
  100% { transform: translateY(40px); }
}

.particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  width: 2px;
  height: 2px;
  background: var(--particle-color);
  border-radius: 50%;
  animation: twinkle 4s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.5); }
}

.meteors {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.meteor {
  position: absolute;
  width: 150px; /* Longer tail */
  height: 2px;
  background: linear-gradient(to right, transparent, var(--primary-color));
  transform: rotate(-45deg);
  opacity: 0;
  animation: meteor 4s linear infinite; /* Faster animation */
  filter: drop-shadow(0 0 8px var(--primary-color)); /* Stronger glow */
  z-index: 1; /* Ensure visibility */
}

@keyframes meteor {
  0% { opacity: 1; transform: rotate(-45deg) translateX(0); }
  100% { opacity: 0; transform: rotate(-45deg) translateX(-500px); }
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, transparent, var(--grid-color), transparent);
  opacity: 0.1;
  animation: scan 10s linear infinite;
  pointer-events: none;
}

@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

/* Layout */
.main-layout {
  position: relative;
  height: 100vh;
  z-index: 1;
}

.sidebar {
  background: var(--sidebar-bg);
  backdrop-filter: blur(10px);
  border-right: 1px solid var(--border-primary);
  transition: all 0.3s ease;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-size: 18px;
  font-weight: bold;
  gap: 8px;
  background: var(--bg-overlay);
  border-bottom: 1px solid var(--border-primary);
  text-shadow: 0 0 10px var(--border-secondary);
}

.logo .el-icon {
  font-size: 24px;
  filter: drop-shadow(0 0 5px var(--primary-color));
}

.el-menu {
  border: none;
  background: transparent;
}

.header {
  background: var(--header-bg);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-sm);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-primary);
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
  text-shadow: 0 0 10px var(--border-secondary);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s;
  color: var(--text-primary);
  border: 1px solid transparent;
}

.user-info:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-primary);
  color: var(--primary-color);
}

.main-content {
  background: transparent; /* Transparent to show effects */
  padding: 20px;
  overflow-y: auto;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
