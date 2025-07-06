<template>
  <div class="student-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToHome">SQL在线实践平台</span>
        <div class="nav-buttons">
          <el-button type="text" @click="goToTask" class="nav-btn">题目·任务</el-button>
          <el-button type="text" @click="goToDashboard" class="nav-btn">数据面板</el-button>
        </div>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="username-dropdown">
            {{ studentInfo.姓名 || '加载中...' }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="content-wrapper">
          <!-- 左侧排行榜 -->
          <div class="left-section">
            <div class="ranking-card">
              <h3>🏆 排行榜</h3>
              <div class="ranking-list" v-loading="rankingLoading">
                <div 
                  v-for="(item, index) in rankingData" 
                  :key="index"
                  class="ranking-item"
                  :class="{ 'top-three': item.名次 <= 3 }"
                >
                  <div class="rank-number">
                    <span v-if="item.名次 === 1" class="gold">🥇</span>
                    <span v-else-if="item.名次 === 2" class="silver">🥈</span>
                    <span v-else-if="item.名次 === 3" class="bronze">🥉</span>
                    <span v-else class="normal">{{ item.名次 }}</span>
                  </div>
                  <div class="student-info">
                    <div class="student-name">{{ item.姓名 }}</div>
                    <div class="student-stats">
                      <span class="stat-item">题目数: {{ item.题目数 }}</span>
                      <span class="stat-item">方法数: {{ item.方法数 }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧主要内容区 -->
          <div class="right-section">
            <!-- 个人信息卡片 -->
            <div class="student-card" v-loading="studentLoading">
              <h3>📋 个人信息</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>学号:</label>
                  <span>{{ studentInfo.学号 || '-' }}</span>
                </div>
                <div class="info-item">
                  <label>姓名:</label>
                  <span>{{ studentInfo.姓名 || '-' }}</span>
                </div>
                <div class="info-item">
                  <label>班级:</label>
                  <span>{{ studentInfo.班级 || '-' }}</span>
                </div>
                <div class="info-item">
                  <label>当前学期:</label>
                  <span>{{ studentInfo.当前学期 || '-' }}</span>
                </div>
                <div class="info-item">
                  <label>课序号:</label>
                  <span>{{ studentInfo.课序号 || '-' }}</span>
                </div>
                <div class="info-item">
                  <label>任课教师:</label>
                  <span>{{ studentInfo.任课教师 || '-' }}</span>
                </div>
              </div>
            </div>
            
            <!-- 当前排名卡片 -->
            <div class="current-rank-card">
              <h3>📊 我的排名</h3>
              <div class="current-rank">
                <div class="rank-display">
                  <span class="rank-text">当前排名</span>
                  <span class="rank-value">无</span>
                </div>
                <div class="timestamp">
                  <span class="time-label">更新时间:</span>
                  <span class="time-value">{{ currentTimestamp }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      :before-close="() => { passwordDialogVisible = false; resetPasswordForm(); }"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="原密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入原密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请确认新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false; resetPasswordForm();">取消</el-button>
          <el-button type="primary" @click="changePassword" :loading="passwordLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { 
  ElMessage, 
  ElMessageBox, 
  ElDropdown, 
  ElDropdownMenu, 
  ElDropdownItem, 
  ElIcon,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElButton,
  type FormInstance,
  type FormRules
} from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

// 类型定义
interface RankingItem {
  名次: number
  姓名: string
  题目数: number
  方法数: number
}

interface StudentInfo {
  学号?: string
  姓名?: string
  班级?: string
  当前学期?: string
  课序号?: string
  任课教师?: string
}

const router = useRouter()

// 响应式数据
const rankingData = ref<RankingItem[]>([])
const studentInfo = ref<StudentInfo>({})
const rankingLoading = ref(false)
const studentLoading = ref(false)
const currentTimestamp = ref('')

// 修改密码相关
const passwordDialogVisible = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordLoading = ref(false)

// 生成当前时间戳
const generateTimestamp = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  currentTimestamp.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 获取排行榜数据
const fetchRankingData = async () => {
  rankingLoading.value = true
  try {
    const response = await axios.get('/student/rank')
    
    if (response.data) {
      rankingData.value = response.data
      console.log('排行榜数据加载成功:', response.data)
    }
  } catch (error: unknown) {
    console.error('获取排行榜数据失败:', error)
    ElMessage.error('获取排行榜数据失败')
  } finally {
    rankingLoading.value = false
  }
}

// 获取学生个人信息
const fetchStudentInfo = async () => {
  studentLoading.value = true
  try {
    const response = await axios.get('/student/profile')
    
    if (response.data) {
      studentInfo.value = response.data
      console.log('学生信息加载成功:', response.data)
    }
  } catch (error: unknown) {
    console.error('获取学生信息失败:', error)
    ElMessage.error('获取学生信息失败')
  } finally {
    studentLoading.value = false
  }
}

// 点击logo跳转到首页
const goToHome = () => {
  router.push('/student/home')
}

// 跳转到任务页面
const goToTask = () => {
  router.push('/student/task')
}

// 跳转到数据面板
const goToDashboard = () => {
  router.push('/student/dashboard')
}

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  if (command === 'changePassword') {
    passwordDialogVisible.value = true
  } else if (command === 'logout') {
    handleLogout()
  }
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    await axios.put('/auth/password', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    resetPasswordForm()
  } catch (error: unknown) {
    console.error('修改密码失败:', error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: unknown; message?: string } } }
      if (axiosError.response?.data?.detail) {
        const detail = axiosError.response.data.detail
        if (Array.isArray(detail) && detail.length > 0) {
          ElMessage.error(detail[0].msg || '修改密码失败')
        } else if (typeof detail === 'string') {
          ElMessage.error(detail)
        } else {
          ElMessage.error('修改密码失败')
        }
      } else if (axiosError.response?.data?.message) {
        ElMessage.error(axiosError.response.data.message)
      } else {
        ElMessage.error('修改密码失败，请检查网络连接')
      }
    } else {
      ElMessage.error('修改密码失败，请检查网络连接')
    }
  } finally {
    passwordLoading.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    try {
      await axios.post('/auth/logout')
    } catch (error) {
      console.warn('登出接口调用失败，但仍然清除本地token:', error)
    }
    
    localStorage.removeItem('token')
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch {
    // 用户取消退出
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

// 密码验证规则
const validateConfirmPassword = (rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value !== passwordForm.value.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 组件挂载时获取数据
onMounted(() => {
  generateTimestamp()
  fetchRankingData()
  fetchStudentInfo()
  
  // 每秒更新时间戳
  setInterval(generateTimestamp, 1000)
})
</script>

<style scoped>
.student-layout {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
  background-color: #f5f7fa;
}

/* 顶部导航栏 */
.header {
  background-color: #545c64;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
}

.nav-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 30px;
}

.nav-btn {
  color: #ffffff !important;
  padding: 0 20px;
  height: 40px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.nav-btn:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.8;
}

.header-right {
  display: flex;
  align-items: center;
}

.username-dropdown {
  font-size: 14px;
  font-weight: bold;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.username-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 主容器 */
.main-container {
  flex: 1;
  height: calc(100vh - 60px);
  width: 100%;
  display: flex;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
}

/* 主内容区 */
.main-content {
  background-color: white;
  padding: 20px;
  overflow-y: auto;
  margin: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 100%;
  box-sizing: border-box;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
  height: 100%;
  padding: 0;
}

/* 左侧排行榜区域 */
.left-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 右侧主要内容区域 */
.right-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

/* 卡片通用样式 */
.ranking-card,
.student-card,
.current-rank-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.ranking-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.student-card {
  flex: 1;
}

.current-rank-card {
  flex-shrink: 0;
}

.ranking-card:hover,
.student-card:hover,
.current-rank-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.ranking-card h3,
.student-card h3,
.current-rank-card h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

/* 排行榜样式 */
.ranking-list {
  flex: 1;
  overflow-y: auto;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
  transition: background-color 0.3s;
}

.ranking-item:hover {
  background-color: #f8f9fa;
}

.ranking-item.top-three {
  background: linear-gradient(135deg, #fff8e1 0%, #fff3c4 100%);
  border-radius: 8px;
  margin-bottom: 8px;
  padding: 12px;
}

.rank-number {
  width: 40px;
  text-align: center;
  font-weight: bold;
  margin-right: 15px;
}

.gold, .silver, .bronze {
  font-size: 20px;
}

.normal {
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.student-info {
  flex: 1;
}

.student-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.student-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  font-size: 12px;
  color: #666;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 12px;
}

/* 学生信息样式 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.info-item label {
  font-weight: 600;
  color: #555;
  margin-right: 10px;
}

.info-item span {
  color: #333;
  font-weight: 500;
}

/* 当前排名样式 */
.current-rank {
  text-align: center;
}

.rank-display {
  margin-bottom: 20px;
}

.rank-text {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.rank-value {
  display: block;
  font-size: 36px;
  font-weight: bold;
  color: #667eea;
}

.timestamp {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.time-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.time-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .main-content {
    padding: 15px;
  }
  
  .ranking-card,
  .student-card,
  .current-rank-card {
    padding: 15px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>