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
        <el-dropdown @command="handleCommand" trigger="click">
          <span class="username-dropdown">
            {{ studentInfo['姓名'] || '' }}
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
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
          <!-- 左侧：知识点 -->
          <div class="left-section">
            <el-card class="knowledge-card">
              <template #header>
                <div class="card-header">
                  <span>知识点</span>
                </div>
              </template>
              <div class="knowledge-content">
                <p>暂无数据</p>
              </div>
            </el-card>
          </div>

          <!-- 右侧：题目部分 -->
          <div class="right-section">
            <el-card class="problem-card">
              <template #header>
                <div class="card-header">
                  <span>题目</span>
                </div>
              </template>
              <div class="problem-content">
                <!-- 数据库模式选择 -->
                <div class="form-section">
                  <el-form :model="formData" label-width="120px">
                    <el-form-item label="数据库模式：">
                      <el-select 
                        v-model="formData.selectedSchema" 
                        placeholder="请选择数据库模式"
                        @change="onSchemaChange"
                        style="width: 200px"
                      >
                        <el-option
                          v-for="schema in schemaList"
                          :key="schema"
                          :label="schema"
                          :value="schema"
                        />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item label="题目序号：">
                      <el-select 
                        v-model="formData.selectedProblem" 
                        placeholder="请选择题目序号"
                        @change="onProblemChange"
                        style="width: 200px"
                        :disabled="!formData.selectedSchema"
                      >
                        <el-option
                          v-for="problem in problemList"
                          :key="problem.problem_id"
                          :label="`题目${problem.display_index}${problem.is_required ? ' (必做)' : ' (选做)'}`"
                          :value="problem.problem_id"
                        />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item>
                      <el-button 
                        type="primary" 
                        @click="viewData"
                        :disabled="!formData.selectedProblem"
                        :loading="dataLoading"
                      >
                        查看数据
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>

                <!-- 数据展示区域 -->
                <div v-if="dashboardData" class="data-section">
                  <el-divider>答题统计</el-divider>
                  
                  <!-- 统计数据概览 -->
                  <div class="stats-overview">
                    <div class="stat-card">
                      <div class="stat-number">{{ dashboardData.submit_count }}</div>
                      <div class="stat-title">总提交次数</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number correct">{{ dashboardData.correct_count }}</div>
                      <div class="stat-title">正确次数</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number wrong">{{ dashboardData.wrong_count }}</div>
                      <div class="stat-title">错误次数</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number method">{{ dashboardData.correct_method_count }}</div>
                      <div class="stat-title">方法次数</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number repeat">{{ dashboardData.repeat_method_count }}</div>
                      <div class="stat-title">重复方法数</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number syntax-error">{{ dashboardData.syntax_error_count }}</div>
                      <div class="stat-title">语法错误数</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number result-error">{{ dashboardData.result_error_count }}</div>
                      <div class="stat-title">结果错误数</div>
                    </div>
                  </div>

                  <!-- 图表展示区域 -->
                  <div class="charts-container">
                    <!-- 正确率饼图 -->
                    <div class="chart-item">
                      <h4 class="chart-title">答题正确率分布</h4>
                      <v-chart 
                        class="chart" 
                        :option="pieChartOption" 
                        autoresize
                      />
                    </div>
                    
                    <!-- 错误类型柱状图 -->
                    <div class="chart-item">
                      <h4 class="chart-title">错误类型统计</h4>
                      <v-chart 
                        class="chart" 
                        :option="barChartOption" 
                        autoresize
                      />
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="changePassword" :loading="passwordLoading">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
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
  ElSelect,
  ElOption,
  ElCard,
  ElDivider,
  type FormInstance,
  type FormRules
} from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import {
  CanvasRenderer
} from 'echarts/renderers'
import {
  PieChart,
  BarChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

// 注册必要的组件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()

// 学生信息
const studentInfo = ref<Record<string, unknown>>({})

// 表单数据
const formData = reactive({
  selectedSchema: '',
  selectedProblem: null as number | null
})

// 数据列表
const schemaList = ref<string[]>([])
const problemList = ref<Array<Record<string, unknown>>>([])
const allProblemsData = ref<Array<Record<string, unknown>>>([])
const dashboardData = ref<Record<string, unknown> | null>(null)

// 加载状态
const dataLoading = ref(false)

// 密码修改相关
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码验证规则
const validateConfirmPassword = (rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度必须在 6 到 50 个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 页面初始化
onMounted(() => {
  fetchStudentInfo()
  fetchProblemList()
})

// 获取学生信息
const fetchStudentInfo = async () => {
  try {
    const response = await axios.get('/student/profile')
    if (response.data) {
      studentInfo.value = response.data
    }
  } catch (error) {
    console.error('获取学生信息失败:', error)
  }
}

// 获取题目列表
const fetchProblemList = async () => {
  try {
    const response = await axios.get('/public/problem/list')
    if (response.data && Array.isArray(response.data)) {
      // 存储完整数据
      allProblemsData.value = response.data
      
      // 提取所有唯一的schema_name
      const schemas = response.data.map(item => item.schema_name)
      schemaList.value = [...new Set(schemas)]
      
      // 默认选择第一个schema
      if (schemaList.value.length > 0) {
        formData.selectedSchema = schemaList.value[0]
        updateProblemList()
      }
    }
  } catch (error) {
    console.error('获取题目列表失败:', error)
    ElMessage.error('获取题目列表失败')
  }
}

// 更新题目列表
const updateProblemList = () => {
  const selectedSchemaData = allProblemsData.value.find(item => item.schema_name === formData.selectedSchema)
  if (selectedSchemaData && selectedSchemaData.problems) {
    // 为题目添加前端映射的序号（从1开始）
    problemList.value = selectedSchemaData.problems.map((problem, index) => ({
      ...problem,
      display_index: index + 1
    }))
    
    // 默认选择第一个题目
    if (problemList.value.length > 0) {
      formData.selectedProblem = problemList.value[0].problem_id
    }
  } else {
    problemList.value = []
    formData.selectedProblem = null
  }
}

// 数据库模式改变
const onSchemaChange = () => {
  formData.selectedProblem = null
  dashboardData.value = null
  updateProblemList()
}

// 题目改变
const onProblemChange = () => {
  dashboardData.value = null
}

// 查看数据
const viewData = async () => {
  if (!formData.selectedProblem) {
    ElMessage.warning('请选择题目序号')
    return
  }
  
  try {
    dataLoading.value = true
    const response = await axios.get('/student/dashboard', {
      params: {
        problem_id: formData.selectedProblem
      }
    })
    
    if (response.data) {
      console.log('后端返回的原始数据:', response.data)
      // 处理后端返回的数据结构 {"problems": [{...}]}
      if (response.data.problems && Array.isArray(response.data.problems) && response.data.problems.length > 0) {
        dashboardData.value = response.data.problems[0]
        console.log('解析后的数据面板数据:', dashboardData.value)
      } else {
        dashboardData.value = response.data
        console.log('直接使用的数据面板数据:', dashboardData.value)
      }
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    dataLoading.value = false
  }
}

// 导航方法
const goToHome = () => {
  router.push('/student/home')
}

const goToTask = () => {
  router.push('/student/task')
}

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
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
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
          ElMessage.error(detail[0])
        } else {
          ElMessage.error(detail)
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
    
    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch {
    // 用户取消退出
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

// 饼图配置
const pieChartOption = computed(() => {
  if (!dashboardData.value) return {}
  
  const correctCount = dashboardData.value.correct_count || 0
  const wrongCount = dashboardData.value.wrong_count || 0
  const total = correctCount + wrongCount
  
  if (total === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    }
  }
  
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '答题统计',
        type: 'pie',
        radius: '50%',
        data: [
          {
            value: correctCount,
            name: '正确',
            itemStyle: {
              color: '#67C23A'
            }
          },
          {
            value: wrongCount,
            name: '错误',
            itemStyle: {
              color: '#F56C6C'
            }
          }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

// 柱状图配置
const barChartOption = computed(() => {
  if (!dashboardData.value) return {}
  
  const syntaxErrorCount = dashboardData.value.syntax_error_count || 0
  const resultErrorCount = dashboardData.value.result_error_count || 0
  const correctMethodCount = dashboardData.value.correct_method_count || 0
  const repeatMethodCount = dashboardData.value.repeat_method_count || 0
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['语法错误', '结果错误', '正确方法', '重复方法'],
      axisLabel: {
        interval: 0,
        rotate: 0
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '次数',
        type: 'bar',
        data: [
          {
            value: syntaxErrorCount,
            itemStyle: {
              color: '#F56C6C'
            }
          },
          {
            value: resultErrorCount,
            itemStyle: {
              color: '#E6A23C'
            }
          },
          {
            value: correctMethodCount,
            itemStyle: {
              color: '#67C23A'
            }
          },
          {
            value: repeatMethodCount,
            itemStyle: {
              color: '#909399'
            }
          }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
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
  width: 100%;
}

/* 左侧知识点区域 */
.left-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.knowledge-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.knowledge-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

/* 右侧题目区域 */
.right-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.problem-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.problem-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-section {
  margin-bottom: 20px;
}

.data-section {
  flex: 1;
}

/* 统计数据概览样式 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 15px;
  margin: 20px 0;
  max-width: 100%;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  color: white;
  min-width: 120px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-number.correct {
  color: #67C23A;
}

.stat-number.wrong {
  color: #F56C6C;
}

.stat-number.method {
  color: #409EFF;
}

.stat-number.repeat {
  color: #909399;
}

.stat-number.syntax-error {
  color: #E6A23C;
}

.stat-number.result-error {
  color: #F56C6C;
}

.stat-title {
  font-size: 14px;
  opacity: 0.9;
}

/* 图表容器样式 */
.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.chart-item {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
}

.chart-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.chart {
  width: 100%;
  height: 300px;
}

/* 卡片通用样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
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
  
  .nav-buttons {
    display: none;
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .stats-overview {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
  }
  
  .stat-card {
    min-width: 160px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0 10px;
  }
  
  .main-content {
    padding: 10px;
  }
  
  .charts-container {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .chart {
    height: 250px;
  }
  
  .stats-overview {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px;
  }
  
  .stat-card {
    min-width: 120px;
    padding: 12px;
  }
  
  .stat-number {
    font-size: 24px;
  }
}
</style>