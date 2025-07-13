<template>
  <div class="matrix-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToHome">SQL在线实践平台</span>
        <div class="nav-buttons">
          <el-button type="text" @click="goBack" class="nav-btn">数据面板</el-button>
          <el-button type="text" @click="goToDatabaseSchema" class="nav-btn">数据库模式</el-button>
          <el-button type="text" @click="goToProblem" class="nav-btn">题目</el-button>
          <el-button type="text" @click="goToStudentInfo" class="nav-btn">学生信息</el-button>
        </div>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="username-dropdown">
            {{ teacherInfo.teacher_name || '加载中...' }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="main-container">

      <el-main class="main-content">
        <!-- 筛选控制栏 -->
        <div class="filter-bar">
          <div class="filter-left">
            <div class="page-title">
              <el-button @click="goBack" type="text" class="back-btn">
                <el-icon><ArrowLeft /></el-icon>
              </el-button>
              <span class="title-text">态势矩阵</span>
            </div>
            <el-select v-model="selectedClass" placeholder="选择班级" clearable @change="handleClassChange" class="class-select">
              <el-option label="全部班级" value="" />
              <el-option 
                v-for="cls in classList" 
                :key="cls" 
                :label="cls" 
                :value="cls" 
              />
            </el-select>
            <el-button @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
          <div class="filter-right">
            <el-button @click="openAiAnalysisDialog" type="primary" :loading="aiAnalysisLoading">
              <el-icon><ChatDotRound /></el-icon>
              AI助教分析
            </el-button>
            <span class="data-info">共 {{ filteredStudents.length }} 名学生</span>
          </div>
        </div>

        <!-- 矩阵表格 -->
        <div class="matrix-container" v-if="(filteredStudents.length > 0 && problemList.length > 0) || loading" v-loading="loading">
          <el-table 
            :data="filteredStudents" 
            border 
            stripe
            class="matrix-table"
            height="calc(100vh - 180px)"
            :scroll-y="{ gt: 20 }"
          >
            <!-- 固定左侧学生信息列 -->
            <el-table-column label="学生信息" width="200" fixed="left">
              <template #default="scope">
                <div 
                  class="student-info-cell"
                  @mouseenter="startHoverTimer(scope.row.student_id, $event)"
                  @mouseleave="clearHoverTimer"
                >
                  <div class="student-name">{{ scope.row.student_name }}</div>
                  <div class="student-class">{{ scope.row.class_ }}</div>
                </div>
              </template>
            </el-table-column>
            
            <!-- 动态题目列 -->
            <el-table-column 
              v-for="(problem, index) in problemList" 
              :key="problem.problem_id"
              :label="`NO.${index + 1}`"
              :prop="`problem_${problem.problem_id}`"
              width="100"
              align="center"
            >
              <template #header>
                <div 
                  class="task-header"
                  @mouseenter="startProblemHoverTimer(problem.problem_id, $event)"
                  @mouseleave="clearProblemHoverTimer"
                >
                  <div class="task-name">NO.{{ index + 1 }}</div>
                  <div class="task-type">{{ problem.is_required ? '必做' : '选做' }}</div>
                </div>
              </template>
              <template #default="scope">
                <div 
                  class="matrix-cell"
                  :style="{ backgroundColor: getCellColor(scope.row.student_id, problem.problem_id) }"
                >
                  <span class="cell-content">
                    {{ getCellContent(scope.row.student_id, problem.problem_id) }}
                  </span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 无数据状态 -->
        <div v-else class="empty-state-container">
          <EmptyState 
            v-if="filteredStudents.length === 0 && problemList.length === 0"
            title="暂无学生和题目数据" 
            description="当前没有学生信息和题目数据，请检查数据源或联系管理员。"
          />
          <EmptyState 
            v-else-if="filteredStudents.length === 0"
            title="暂无学生数据" 
            description="当前没有学生信息，请检查班级筛选条件或联系管理员。"
          />
          <EmptyState 
            v-else-if="problemList.length === 0"
            title="暂无题目数据" 
            description="当前没有题目信息，请联系管理员添加题目。"
          />
        </div>

        <!-- 学生详情悬浮卡片 -->
        <div 
          v-if="hoveredStudentInfo"
          class="student-tooltip"
          :style="tooltipStyle"
        >
          <div class="tooltip-header">
            <div class="student-avatar">{{ hoveredStudentInfo.student_name?.charAt(0) || '学' }}</div>
            <div class="student-basic">
              <h4>{{ hoveredStudentInfo.student_name }}</h4>
              <span class="student-id">{{ hoveredStudentInfo.student_id }}</span>
            </div>
          </div>
          <div class="tooltip-content">
            <div class="info-item">
              <span class="label">班级</span>
              <span class="value">{{ hoveredStudentInfo.class_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">课序号</span>
              <span class="value">{{ hoveredStudentInfo.course_id }}</span>
            </div>
            <div class="info-item">
              <span class="label">解题数</span>
              <span class="value">{{ hoveredStudentInfo.correct_count }}</span>
            </div>
            <div class="info-item">
              <span class="label">提交数</span>
              <span class="value">{{ hoveredStudentInfo.submit_count }}</span>
            </div>
            <div class="info-item">
              <span class="label">修读方式</span>
              <span class="value">{{ hoveredStudentInfo.status === 0 ? '正常' : '重修' }}</span>
            </div>
          </div>
        </div>

        <!-- 题目详情悬浮卡片 -->
        <div 
          v-if="hoveredProblemInfo"
          class="problem-tooltip"
          :style="problemTooltipStyle"
        >
          <div class="tooltip-header">
            <div class="problem-icon">题</div>
            <div class="problem-basic">
              <h4>题目 {{ hoveredProblemInfo.problem_id }}</h4>
              <span class="problem-type">{{ hoveredProblemInfo.is_required ? '必做题' : '选做题' }}</span>
            </div>
          </div>
          <div class="tooltip-content">
            <div class="info-item">
              <span class="label">完成人数</span>
              <span class="value">{{ hoveredProblemInfo.completed_student_count || 0 }}</span>
            </div>
            <div class="info-item">
              <span class="label">总提交数</span>
              <span class="value">{{ hoveredProblemInfo.total_submission_count || 0 }}</span>
            </div>
            <div class="info-item">
              <span class="label">数据库模式</span>
              <span class="value">{{ hoveredProblemInfo.schema_name || 'HR' }}</span>
            </div>
            <div class="info-item">
              <span class="label">题目类型</span>
              <span class="value">{{ hoveredProblemInfo.is_required ? '必做题' : '选做题' }}</span>
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
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="changePassword" :loading="passwordLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- AI助教分析对话框 -->
    <el-dialog
      v-model="aiAnalysisDialogVisible"
      title="AI助教分析"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="ai-analysis-content">
        <div v-if="aiAnalysisLoading" class="loading-container">
           <el-icon class="is-loading"><Loading /></el-icon>
           <p>AI正在分析学生作答情况，请稍候...</p>
           <div class="countdown-display">
             <span class="countdown-text">预计还需等待：</span>
             <span class="countdown-number">{{ countdown }}</span>
             <span class="countdown-unit">秒</span>
           </div>
         </div>
        <div v-else-if="aiAnalysisResult" class="analysis-result">
          <div class="result-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI分析结果</span>
          </div>
          <div class="result-content">
            <pre>{{ aiAnalysisResult }}</pre>
          </div>
        </div>
        <div v-else class="no-result">
          <el-icon><Warning /></el-icon>
          <p>暂无分析结果</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="aiAnalysisDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="performAiAnalysis" :loading="aiAnalysisLoading">
            重新分析
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/utils/axios'
import { 
  ElMessage, 
  ElMessageBox,
  ElContainer,
  ElHeader,
  ElMain,
  ElButton,
  ElIcon,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElSelect,
  ElOption,
  ElTable,
  ElTableColumn,
  ElTag,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  type FormInstance,
  type FormRules
} from 'element-plus'
import { ArrowLeft, ArrowDown, Refresh, ChatDotRound, Loading, Warning } from '@element-plus/icons-vue'
import EmptyState from '@/components/EmptyState.vue'

// 类型定义
interface Student {
  student_id: string
  student_name: string
  class_: string
  teacher_name: string
  semester_name: string
  course_id: string
  [key: string]: any
}

interface StudentProfile {
  student_id: string
  student_name: string
  class_name: string
  course_id: number
  status: number
  correct_count: number
  submit_count: number
}

interface Problem {
  problem_id: number
  is_required: number
  is_ordered: number
  problem_content: string
  example_sql: string
}

interface ProblemStats {
  student_id: string
  problem_id: string
  submit_count: number
  correct_count: number
  syntax_error_count: number
  result_error_count: number
}

interface TeacherInfo {
  teacher_id?: string
  teacher_name?: string
  semester_name?: string
}

const router = useRouter()
const route = useRoute()

// 获取路由参数
const semesterId = ref(route.params.semester_id as string)

// 响应式数据
const students = ref<Student[]>([])
const problemList = ref<Problem[]>([])
const problemStats = ref<ProblemStats[]>([])
const teacherInfo = ref<TeacherInfo>({})
const selectedClass = ref('')
const loading = ref(false)
const hoveredStudentInfo = ref<StudentProfile | null>(null)
const tooltipStyle = ref({})
const hoverTimer = ref<number | null>(null)

// 题目悬浮相关
const hoveredProblemInfo = ref<any>(null)
const problemTooltipStyle = ref({})
const problemHoverTimer = ref<number | null>(null)

// 密码修改相关
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// AI分析相关
const aiAnalysisDialogVisible = ref(false)
const aiAnalysisLoading = ref(false)
const aiAnalysisResult = ref('')
const countdown = ref(60)
const countdownTimer = ref<number | null>(null)

// 密码验证规则
const passwordRules: FormRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 计算属性
const classList = computed(() => {
  const classes = [...new Set(students.value.map(s => s.class_))]
  return classes.sort()
})

const filteredStudents = computed(() => {
  if (!selectedClass.value) {
    return students.value
  }
  return students.value.filter(s => s.class_ === selectedClass.value)
})

// 获取学生列表
const fetchStudents = async () => {
  try {
    loading.value = true
    const response = await axios.get('/teacher/students', {
      params: {
        semester_id: semesterId.value,
        page: 1,
        limit: 100
      }
    })
    if (response.data && response.data.students) {
      students.value = response.data.students
      // 获取题目列表并获取统计数据
      await fetchProblems()
      await fetchProblemStats()
    }
  } catch (error) {
    console.error('获取学生列表失败:', error)
    ElMessage.error('获取学生列表失败')
  } finally {
    loading.value = false
  }
}

// 获取教师信息
const fetchTeacherInfo = async () => {
  try {
    const response = await axios.get('/teacher/profile')
    if (response.data) {
      teacherInfo.value = response.data
    }
  } catch (error) {
    console.error('获取教师信息失败:', error)
  }
}

// 获取题目列表
const fetchProblems = async () => {
  try {
    const schemaId = localStorage.getItem('selectedSchemaId') || '1'
    const response = await axios.get('/teacher/problem/list', {
      params: {
        schema_id: schemaId
      }
    })
    if (response.data && response.data.data) {
      problemList.value = response.data.data
    }
  } catch (error) {
    console.error('获取题目列表失败:', error)
    ElMessage.error('获取题目列表失败，请检查网络连接')
    problemList.value = []
  }
}

// 获取学生题目提交统计数据
const fetchProblemStats = async () => {
  try {
    if (students.value.length === 0 || problemList.value.length === 0) {
      return
    }
    
    const studentIds = students.value.map(s => s.student_id)
    const problemIds = problemList.value.map(p => p.problem_id.toString())
    
    const response = await axios.post('/teacher/student/problem-stats', {
      student_ids: studentIds,
      problem_ids: problemIds
    })
    
    if (response.data && response.data.data) {
      problemStats.value = response.data.data
    }
  } catch (error) {
    console.error('获取学生题目统计数据失败:', error)
    ElMessage.error('获取学生题目统计数据失败')
  }
}

// 获取单元格数据
const getCellData = (studentId: string, problemId: number) => {
  const stats = problemStats.value.find(
    s => s.student_id === studentId && s.problem_id === problemId.toString()
  )
  return stats || {
    student_id: studentId,
    problem_id: problemId.toString(),
    submit_count: 0,
    correct_count: 0,
    syntax_error_count: 0,
    result_error_count: 0
  }
}

// 获取单元格显示内容
const getCellContent = (studentId: string, problemId: number) => {
  const data = getCellData(studentId, problemId)
  let content = `${data.correct_count}/${data.submit_count}`
  
  // 添加错误信息
  const errors = []
  if (data.syntax_error_count > 0) {
    errors.push(`(-${data.syntax_error_count})`)
  }
  if (data.result_error_count > 0) {
    errors.push(`(-${data.result_error_count})`)
  }
  
  if (errors.length > 0) {
    content += ` ${errors.join(' ')}`
  }
  
  return content
}

// 获取单元格颜色
const getCellColor = (studentId: string, problemId: number) => {
  const data = getCellData(studentId, problemId)
  
  // 绿色：正常完成（正确次数>=1）
  if (data.correct_count >= 1) {
    return '#67C23A' // 绿色
  }
  
  // 红色：存在语法错误（正确次数为0并且存在语法错误）
  if (data.correct_count === 0 && data.syntax_error_count > 0) {
    return '#F56C6C' // 红色
  }
  
  // 橙色：只存在结果错误（正确次数为0并且不存在语法错误）
  if (data.correct_count === 0 && data.syntax_error_count === 0 && data.result_error_count > 0) {
    return '#E6A23C' // 橙色
  }
  
  // 默认颜色（没有提交）
  return '#F5F7FA' // 浅灰色
}

// 获取学生详情
const fetchStudentProfile = async (studentId: string) => {
  try {
    // 从localStorage或其他地方获取选中的schema_id
    const schemaId = localStorage.getItem('selectedSchemaId') || '1'
    
    const response = await axios.get('/teacher/student-profile', {
      params: {
        student_id: studentId,
        schema_id: schemaId
      }
    })
    if (response.data) {
      return response.data
    }
  } catch (error) {
    console.error('获取学生详情失败:', error)
    return null
  }
}

// 处理学生悬浮事件
const startHoverTimer = (studentId: string, event: MouseEvent) => {
  // 清除之前的定时器
  if (hoverTimer.value) {
    clearTimeout(hoverTimer.value)
  }
  
  // 设置1秒延迟
  hoverTimer.value = setTimeout(async () => {
    const profile = await fetchStudentProfile(studentId)
    if (profile) {
      hoveredStudentInfo.value = profile
      const rect = (event.target as HTMLElement).getBoundingClientRect()
      tooltipStyle.value = {
        position: 'fixed',
        left: `${rect.right + 10}px`,
        top: `${rect.top}px`,
        zIndex: 1000
      }
    }
  }, 1000)
}

const clearHoverTimer = () => {
  // 清除定时器
  if (hoverTimer.value) {
    clearTimeout(hoverTimer.value)
    hoverTimer.value = null
  }
  hoveredStudentInfo.value = null
}

// 获取题目完成情况统计
const fetchProblemSummary = async (problemId: number) => {
  try {
    const response = await axios.get('/teacher/problem/summary', {
      params: {
        problem_id: problemId
      }
    })
    if (response.data && response.data.code === 200) {
      return response.data.data
    }
  } catch (error) {
    console.error('获取题目统计信息失败:', error)
    return null
  }
}

// 处理题目悬浮事件
const startProblemHoverTimer = (problemId: number, event: MouseEvent) => {
  // 清除之前的定时器
  if (problemHoverTimer.value) {
    clearTimeout(problemHoverTimer.value)
  }
  
  // 设置1秒延迟
  problemHoverTimer.value = setTimeout(async () => {
    const summary = await fetchProblemSummary(problemId)
    const problem = problemList.value.find(p => p.problem_id === problemId)
    
    if (summary && problem) {
      hoveredProblemInfo.value = {
        ...problem,
        ...summary,
        schema_name: 'HR' // 可以从其他地方获取实际的schema名称
      }
      
      const rect = (event.target as HTMLElement).getBoundingClientRect()
      problemTooltipStyle.value = {
        position: 'fixed',
        left: `${rect.right + 10}px`,
        top: `${rect.top}px`,
        zIndex: 1000
      }
    }
  }, 1000)
}

const clearProblemHoverTimer = () => {
  // 清除定时器
  if (problemHoverTimer.value) {
    clearTimeout(problemHoverTimer.value)
    problemHoverTimer.value = null
  }
  hoveredProblemInfo.value = null
}





// 事件处理
const goBack = () => {
  router.push('/teacher/dashboard')
}

const goToHome = () => {
  router.push('/teacher/home')
}

const goToDatabaseSchema = () => {
  router.push('/teacher/database-schema')
}

const goToProblem = () => {
  router.push('/teacher/problem')
}

const goToStudentInfo = () => {
  router.push('/teacher/student-info')
}

const handleClassChange = () => {
  // 班级筛选逻辑已通过计算属性实现
}

const refreshData = () => {
  fetchStudents()
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能正在开发中')
      break
    case 'password':
      passwordDialogVisible.value = true
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('token')
        router.push('/login')
      })
      break
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    // 调用修改密码接口
    await axios.post('/teacher/change-password', passwordForm.value)
    
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    passwordForm.value = {
      old_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  } finally {
    passwordLoading.value = false
  }
}

// AI分析相关函数
const openAiAnalysisDialog = () => {
  aiAnalysisDialogVisible.value = true
  // 打开对话框时自动执行分析
  performAiAnalysis()
}

// 启动倒计时
const startCountdown = () => {
  countdown.value = 60
  countdownTimer.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer.value!)
      countdownTimer.value = null
    }
  }, 1000)
}

// 停止倒计时
const stopCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
    countdownTimer.value = null
  }
}

const performAiAnalysis = async () => {
  if (problemList.value.length === 0) {
    ElMessage.warning('暂无题目数据，无法进行分析')
    return
  }
  
  try {
    aiAnalysisLoading.value = true
    aiAnalysisResult.value = ''
    startCountdown()
    
    // 准备分析数据，直接使用前端已有的数据
    const analysisData = []
    
    for (const problem of problemList.value) {
      // 统计该题目的完成情况
      const problemId = problem.problem_id.toString()
      const problemStats_filtered = problemStats.value.filter(stat => stat.problem_id === problemId)
      
      // 计算完成人数（正确次数 >= 1 的学生数）
      const completedStudentCount = problemStats_filtered.filter(stat => stat.correct_count >= 1).length
      
      // 计算总提交次数
      const totalSubmissionCount = problemStats_filtered.reduce((sum, stat) => sum + stat.submit_count, 0)
      
      analysisData.push({
        problem_id: problem.problem_id,
        completed_student_count: completedStudentCount,
        total_submission_count: totalSubmissionCount
      })
    }
    
    if (analysisData.length === 0) {
      ElMessage.warning('暂无有效的题目统计数据')
      return
    }
    
    // 调用AI分析接口
    const response = await axios.post('/teacher/problem/ai-analyze', analysisData)
    
    if (response.data && response.data.code === 200) {
      aiAnalysisResult.value = response.data.data.ai_result || '分析完成，但未返回结果'
      ElMessage.success('AI分析完成')
    } else {
      throw new Error(response.data?.msg || 'AI分析失败')
    }
  } catch (error) {
    console.error('AI分析失败:', error)
    ElMessage.error('AI分析失败，请稍后重试')
    aiAnalysisResult.value = '分析失败，请稍后重试'
  } finally {
    aiAnalysisLoading.value = false
    stopCountdown()
  }
}

// 生命周期
onMounted(() => {
  fetchStudents()
  fetchTeacherInfo()
})

// 组件销毁时清理定时器
onBeforeUnmount(() => {
  stopCountdown()
})
</script>

<style scoped>
.matrix-layout {
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
  overflow: hidden;
}

/* 主内容样式 */
.main-content {
  padding: 20px;
  height: 100%;
  overflow: auto;
}

/* 筛选栏样式 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-right {
  color: #6b7280;
  font-size: 14px;
}

/* 矩阵容器样式 */
.matrix-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.matrix-table {
  width: 100%;
}

/* 任务头部样式 */
.task-header {
  text-align: center;
}

.task-name {
  font-weight: 600;
  margin-bottom: 2px;
}

.task-type {
  font-size: 11px;
  color: #6b7280;
}

/* 矩阵单元格样式 */
.matrix-cell {
  cursor: pointer;
  transition: all 0.3s;
  padding: 8px;
  border-radius: 4px;
  text-align: center;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.matrix-cell:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.cell-content {
  font-size: 12px;
  font-weight: 500;
  color: #333;
  line-height: 1.2;
  white-space: nowrap;
}

/* 学生详情悬浮卡片 */
.student-tooltip {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  min-width: 280px;
  max-width: 320px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.tooltip-header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f0f2f5;
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.student-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.student-basic h4 {
  margin: 0 0 4px 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.2;
}

.student-id {
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f9fafb;
  font-size: 14px;
}

.info-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.info-item .label {
  color: #6b7280;
  font-weight: 500;
  min-width: 60px;
}

.info-item .value {
  color: #1f2937;
  font-weight: 600;
  text-align: right;
}

/* 页面标题样式 */
.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 16px;
}

.back-btn {
  color: #409eff !important;
  font-size: 16px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: #ecf5ff !important;
}

.title-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 2px;
  white-space: nowrap;
}

.class-select {
  min-width: 150px;
}

/* 题目详情悬浮卡片 */
.problem-tooltip {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  min-width: 280px;
  max-width: 320px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.problem-tooltip-header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f0f2f5;
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.problem-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.problem-basic h4 {
  margin: 0 0 4px 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.2;
}

.problem-id {
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
}

/* 空状态容器 */
.empty-state-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 180px);
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* AI分析对话框样式 */
.ai-analysis-content {
  min-height: 300px;
  display: flex;
  flex-direction: column;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #606266;
}

.loading-container .el-icon {
  font-size: 32px;
  margin-bottom: 16px;
  color: #409eff;
}

.loading-container p {
  margin: 0 0 20px 0;
  font-size: 14px;
}

.countdown-display {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  margin-top: 10px;
}

.countdown-text {
  font-size: 14px;
  color: #909399;
}

.countdown-number {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
  min-width: 30px;
  text-align: center;
}

.countdown-unit {
  font-size: 14px;
  color: #909399;
}

.analysis-result {
  flex: 1;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.result-header .el-icon {
  color: #409eff;
  font-size: 18px;
}

.result-header span {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.result-content {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.result-content pre {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #495057;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.no-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #909399;
}

.no-result .el-icon {
  font-size: 32px;
  margin-bottom: 16px;
  color: #e6a23c;
}

.no-result p {
  margin: 0;
  font-size: 14px;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.data-info {
  color: #606266;
  font-size: 14px;
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .header-left h2 {
    font-size: 16px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .filter-left {
    justify-content: center;
  }
}
</style>