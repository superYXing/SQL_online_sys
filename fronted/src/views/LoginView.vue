<template>
  <div class="login-container">
    <!-- 顶部标题 -->
    <div class="header-section">
      <div class="platform-icon">
        <el-icon size="32"><DataBoard /></el-icon>
      </div>
      <h1 class="platform-title">SQL在线测试平台</h1>
      <p class="platform-subtitle">选择您的身份开始学习之旅</p>
    </div>

    <!-- 主要内容区 -->
    <div class="main-section">
      <!-- 左侧角色选择 -->
      <div class="role-selection">
        <h2 class="selection-title">选择登录身份</h2>
        <div class="role-cards">
          <div 
            class="role-card" 
            :class="{ active: loginForm.role === 'student' }"
            @click="selectRole('student')"
          >
            <div class="role-icon student-icon">
              <el-icon size="24"><User /></el-icon>
            </div>
            <div class="role-info">
              <h3>学生</h3>
              <p>完成SQL练习题目，查看学习进度</p>
            </div>
          </div>

          <div 
            class="role-card" 
            :class="{ active: loginForm.role === 'teacher' }"
            @click="selectRole('teacher')"
          >
            <div class="role-icon teacher-icon">
              <el-icon size="24"><Reading /></el-icon>
            </div>
            <div class="role-info">
              <h3>教师</h3>
              <p>管理学生，创建题目，查看答题情况</p>
            </div>
          </div>

          <div 
            class="role-card" 
            :class="{ active: loginForm.role === 'admin' }"
            @click="selectRole('admin')"
          >
            <div class="role-icon admin-icon">
              <el-icon size="24"><Setting /></el-icon>
            </div>
            <div class="role-info">
              <h3>管理员</h3>
              <p>系统管理，用户管理，数据统计</p>
            </div>
            <div class="role-check" v-if="loginForm.role === 'admin'">
              <el-icon size="20"><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-form-section">
        <div class="login-box">
          <div class="login-header">
            <div class="login-icon">
              <el-icon size="32"><Setting /></el-icon>
            </div>
            <h2>{{ getRoleTitle() }}登录</h2>
          </div>
          
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <!-- 账号输入 -->
            <el-form-item prop="account">
              <el-input
                v-model="loginForm.account"
                :placeholder="getAccountPlaceholder()"
                size="large"
                :prefix-icon="User"
                clearable
              />
            </el-form-item>

            <!-- 密码输入 -->
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                clearable
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <!-- 记住密码 -->
            <div class="form-options">
              <el-checkbox v-model="rememberPassword">记住密码</el-checkbox>
              <a href="#" class="forgot-password">忘记密码?</a>
            </div>

            <!-- 登录按钮 -->
            <el-form-item>
              <el-button
                type="primary"
                class="login-btn"
                size="large"
                :loading="loading"
                @click="handleLogin"
              >
                {{ loading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="footer-section">
      <p>© 版权所有 · 教育机构 · 网站备案</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import {
  User,
  Lock,
  Setting,
  DataBoard,
  Reading,
  Check
} from '@element-plus/icons-vue'

const router = useRouter()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const rememberPassword = ref(false)

// 表单数据
const loginForm = reactive({
  account: '',
  password: '',
  role: 'student'
})

// 表单验证规则
const loginRules: FormRules = {
  role: [
    { required: true, message: '请选择登录身份', trigger: 'change' }
  ],
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 1, max: 50, message: '账号长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 1, max: 100, message: '密码长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 选择角色
const selectRole = (role: string) => {
  loginForm.role = role
  // 清空表单数据
  loginForm.account = ''
  loginForm.password = ''
}

// 获取角色标题
const getRoleTitle = () => {
  switch (loginForm.role) {
    case 'student':
      return '学生'
    case 'teacher':
      return '教师'
    case 'admin':
      return '管理员'
    default:
      return '用户'
  }
}

// 获取账号输入框占位符
const getAccountPlaceholder = () => {
  switch (loginForm.role) {
    case 'student':
      return '学号'
    case 'teacher':
      return '教职工号'
    case 'admin':
      return '账号'
    default:
      return '账号'
  }
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 表单验证
    await loginFormRef.value.validate()
    
    loading.value = true
    
    // 调用登录接口
    const response = await axios.post('/auth/login', {
      account: loginForm.account,
      password: loginForm.password,
      role: loginForm.role
    })
    
    if (response.data.code === 200) {
      // 登录成功
      ElMessage.success(response.data.message || '登录成功')
      
      // 保存token和用户信息
      localStorage.setItem('token', response.data.data.token)
      localStorage.setItem('userInfo', JSON.stringify(response.data.data.user))
      
      // 根据角色跳转到不同页面
      if (loginForm.role === 'admin') {
        router.push('/admin/semester')
      } else if (loginForm.role === 'student') {
        router.push('/student/home')
      } else if (loginForm.role === 'teacher') {
        router.push('/teacher/home')
      } else {
        router.push('/home')
      }
    } else {
      ElMessage.error(response.data.detail || response.data.message || '登录失败')
    }
  } catch (error: unknown) {
    console.error('登录错误:', error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string; message?: string } } }
      if (axiosError.response?.data?.detail) {
        ElMessage.error(axiosError.response.data.detail)
      } else if (axiosError.response?.data?.message) {
        ElMessage.error(axiosError.response.data.message)
      } else {
        ElMessage.error('登录失败，请检查网络连接')
      }
    } else {
      ElMessage.error('登录失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 20%), url('@/assets/login.png');
 
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* 顶部标题区域 */
.header-section {
  text-align: center;
  padding: 40px 20px 20px;
  color: white;
}

.platform-icon {
  margin-bottom: 16px;
}

.platform-title {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.platform-subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
  color: white;
}

/* 主要内容区域 */
.main-section {
  flex: 1;
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  gap: 40px;
  align-items: flex-start;
}

/* 左侧角色选择 */
.role-selection {
  flex: 1;
  max-width: 500px;
}

.selection-title {
  color: white;
  font-size: 20px;
  font-weight: 500;
  margin: 0 0 30px 0;
  text-align: center;
}

.role-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.role-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  border: 2px solid transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.role-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.role-card.active {
  border-color: #8b5cf6;
  background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
}

.role-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.student-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.teacher-icon {
  background: linear-gradient(135deg, #10b981 0%, #047857 100%);
}

.admin-icon {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.role-info {
  flex: 1;
}

.role-info h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.role-info p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

.role-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: #8b5cf6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

/* 右侧登录表单 */
.login-form-section {
  flex: 0 0 400px;
  display: flex;
  align-items: center;
}

.login-box {
  width: 100%;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
}

.login-header h2 {
  color: #1f2937;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.login-form {
  width: 100%;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.forgot-password {
  color: #8b5cf6;
  text-decoration: none;
  font-size: 14px;
}

.forgot-password:hover {
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-btn:hover {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
}

/* 底部信息 */
.footer-section {
  text-align: center;
  padding: 20px;
  color: white;
  opacity: 0.8;
}

.footer-section p {
  margin: 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-section {
    flex-direction: column;
    gap: 20px;
    padding: 20px 16px;
  }
  
  .login-form-section {
    flex: none;
  }
  
  .login-box {
    padding: 24px;
  }
  
  .platform-title {
    font-size: 24px;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e5e7eb;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #8b5cf6;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #8b5cf6;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #8b5cf6;
  border-color: #8b5cf6;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>