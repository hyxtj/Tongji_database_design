<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="profile-card tech-border">
          <div class="profile-header">
            <div class="avatar-wrapper">
              <div class="avatar-ring"></div>
              <el-avatar :size="100" class="user-avatar">
                {{ userInitial }}
              </el-avatar>
            </div>
            <h2 class="username">{{ userStore.user?.username || 'User' }}</h2>
            <el-tag :type="userStore.isAdmin ? 'danger' : 'primary'" class="role-tag">
              {{ userStore.isAdmin ? 'ADMINISTRATOR' : 'OPERATOR' }}
            </el-tag>
          </div>
          
          <div class="profile-stats">
            <div class="stat-item">
              <div class="stat-value">Active</div>
              <div class="stat-label">Status</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">Level {{ userStore.isAdmin ? '99' : '1' }}</div>
              <div class="stat-label">Access</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card class="info-card tech-border">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon><User /></el-icon> PERSONNEL FILE
              </span>
              <el-button type="primary" link @click="openEditProfile">EDIT PROFILE</el-button>
            </div>
          </template>
          
          <el-descriptions :column="1" border class="tech-descriptions">
            <el-descriptions-item label="USER ID">
              <span class="tech-text">{{ userStore.user?.id || 'UNKNOWN' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="EMAIL ADDRESS">
              <span class="tech-text">{{ userStore.user?.email || 'UNKNOWN' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="DEPARTMENT">
              <span class="tech-text">Traffic Control Center</span>
            </el-descriptions-item>
            <el-descriptions-item label="CLEARANCE">
              <span class="tech-text">{{ userStore.isAdmin ? 'Level 5 (Top Secret)' : 'Level 1 (Standard)' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="LAST LOGIN">
              <span class="tech-text">{{ new Date().toLocaleString() }}</span>
            </el-descriptions-item>
          </el-descriptions>

          <div class="security-section">
            <h3 class="section-title">SECURITY SETTINGS</h3>
            <div class="security-actions">
              <el-button type="warning" plain @click="openChangePassword">CHANGE PASSWORD</el-button>
              <el-button type="danger" plain @click="handleEnable2FA">ENABLE 2FA</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Edit Profile Dialog -->
    <el-dialog
      v-model="editProfileVisible"
      title="Edit Profile"
      width="30%"
      class="tech-dialog"
    >
      <el-form :model="editProfileForm" label-position="top">
        <el-form-item label="Email Address">
          <el-input v-model="editProfileForm.email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editProfileVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitEditProfile" :loading="loading">Save</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Change Password Dialog -->
    <el-dialog
      v-model="changePasswordVisible"
      title="Change Password"
      width="30%"
      class="tech-dialog"
    >
      <el-form :model="changePasswordForm" label-position="top">
        <el-form-item label="Current Password">
          <el-input v-model="changePasswordForm.current_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="New Password">
          <el-input v-model="changePasswordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="Confirm New Password">
          <el-input v-model="changePasswordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="changePasswordVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitChangePassword" :loading="loading">Change Password</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import { User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const userStore = useUserStore()
const loading = ref(false)

const userInitial = computed(() => {
  const username = userStore.user?.username || 'U'
  return username.charAt(0).toUpperCase()
})

// Edit Profile
const editProfileVisible = ref(false)
const editProfileForm = reactive({
  email: ''
})

const openEditProfile = () => {
  editProfileForm.email = userStore.user?.email || ''
  editProfileVisible.value = true
}

const submitEditProfile = async () => {
  if (!editProfileForm.email) {
    ElMessage.warning('Please enter email address')
    return
  }
  
  loading.value = true
  try {
    const res = await api.put('/auth/profile', {
      email: editProfileForm.email
    })
    ElMessage.success(res.data.message)
    userStore.user = res.data.user // Update local store
    editProfileVisible.value = false
  } catch (error) {
    console.error(error)
    ElMessage.error(error.response?.data?.error || 'Failed to update profile')
  } finally {
    loading.value = false
  }
}

// Change Password
const changePasswordVisible = ref(false)
const changePasswordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const openChangePassword = () => {
  changePasswordForm.current_password = ''
  changePasswordForm.new_password = ''
  changePasswordForm.confirm_password = ''
  changePasswordVisible.value = true
}

const submitChangePassword = async () => {
  if (!changePasswordForm.current_password || !changePasswordForm.new_password) {
    ElMessage.warning('Please fill in all fields')
    return
  }
  
  if (changePasswordForm.new_password !== changePasswordForm.confirm_password) {
    ElMessage.error('New passwords do not match')
    return
  }
  
  loading.value = true
  try {
    await api.post('/auth/change-password', {
      current_password: changePasswordForm.current_password,
      new_password: changePasswordForm.new_password
    })
    ElMessage.success('Password changed successfully')
    changePasswordVisible.value = false
  } catch (error) {
    console.error(error)
    ElMessage.error(error.response?.data?.error || 'Failed to change password')
  } finally {
    loading.value = false
  }
}

// 2FA
const handleEnable2FA = () => {
  ElMessageBox.confirm(
    'Two-Factor Authentication (2FA) adds an extra layer of security to your account. Are you sure you want to enable it?',
    'Enable 2FA',
    {
      confirmButtonText: 'Enable',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(() => {
      // Mock implementation
      setTimeout(() => {
        ElMessage({
          type: 'success',
          message: '2FA has been enabled successfully (Mock)',
        })
      }, 1000)
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: 'Operation canceled',
      })
    })
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  text-align: center;
  padding: 20px;
  height: 100%;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
}

.avatar-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px dashed var(--primary-color);
  border-radius: 50%;
  animation: rotate 10s linear infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.user-avatar {
  background: var(--bg-tertiary);
  color: var(--primary-color);
  font-size: 40px;
  font-weight: bold;
  border: 2px solid var(--primary-color);
}

.username {
  margin: 10px 0;
  color: var(--text-primary);
  font-family: 'Segoe UI', sans-serif;
  letter-spacing: 1px;
}

.role-tag {
  font-weight: bold;
  letter-spacing: 1px;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  border-top: 1px solid var(--border-secondary);
  padding-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.info-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
  color: var(--primary-color);
  letter-spacing: 1px;
}

.tech-descriptions :deep(.el-descriptions__label) {
  background: rgba(0, 243, 255, 0.05) !important;
  color: var(--text-secondary) !important;
  font-weight: bold;
}

.tech-descriptions :deep(.el-descriptions__content) {
  background: transparent !important;
  color: var(--text-primary) !important;
}

.tech-text {
  font-family: 'Consolas', monospace;
  color: var(--text-primary);
}

.security-section {
  margin-top: 30px;
  border-top: 1px solid var(--border-secondary);
  padding-top: 20px;
}

.section-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 15px;
  letter-spacing: 1px;
}

.security-actions {
  display: flex;
  gap: 15px;
}
</style>
