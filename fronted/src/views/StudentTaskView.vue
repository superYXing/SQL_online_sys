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
            {{ studentInfo['姓名'] || '未登录' }}
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
        <div class="task-wrapper">
          <!-- 左侧：数据库模式列表 -->
          <div class="left-panel">
            <div class="panel-header">
              <h3>
                <el-icon><DataAnalysis /></el-icon> 数据库模式
              </h3>
            </div>
            <div class="schema-list">
              <div
                v-for="schema in schemaList"
                :key="schema.schema_name"
                class="schema-item"
                :class="{ active: selectedSchema === schema.schema_name }"
                @click="selectSchema(schema)"
              >
                <div class="schema-name">{{ schema.schema_name }}</div>
                <div class="schema-author">{{ schema.schema_author }}</div>
              </div>
            </div>
          </div>

          <!-- 中间：可用题目列表 -->
          <div class="middle-panel" v-if="selectedSchema && !selectedProblem">
            <div class="problems-section">
              <h3>
                <el-icon><Files /></el-icon> 可用题目列表
              </h3>
              <div class="problem-list">
                <div
                  v-for="(problem, index) in currentProblems"
                  :key="problem.problem_id"
                  class="problem-item"
                  @click="selectProblem(problem)"
                >
                  <div class="problem-header">
                    <span class="problem-number">NO.{{ index + 1 }}</span>
                    <span
                      class="problem-status"
                      :class="problem.is_required ? 'required' : 'optional'"
                    >
                      {{ problem.is_required ? '必做题' : '选做题' }}
                    </span>
                  </div>
                  <div class="problem-title">
                    {{ problem.problem_title || `题目 ${index + 1}` }}
                  </div>
                  <div class="problem-meta">
                    <span class="problem-date">{{ formatDate(new Date()) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：数据库模式描述 -->
          <div class="right-panel" v-if="selectedSchema && !selectedProblem">
            <div class="schema-detail-page">
              <div class="schema-header">
                <h2>{{ selectedSchema }}</h2>
                <p class="author">作者：{{ selectedSchemaInfo?.schema_author }}</p>
              </div>

              <!-- 描述部分 -->
              <div class="schema-description" v-if="selectedSchemaInfo">
                <h3>
                  <el-icon><CollectionTag /></el-icon> 模式描述
                </h3>
                <div v-html="selectedSchemaInfo.schema_description"></div>
              </div>
            </div>
          </div>

          <!-- 题目详情页面（全屏显示） -->
          <div class="problem-detail-page wide" v-if="selectedProblem">
            <!-- 返回按钮 -->
            <div class="back-button">
              <el-button @click="backToSchema" icon="ArrowLeft">返回模式</el-button>
            </div>

            <!-- 题目信息 -->
            <div class="problem-detail">
              <div class="problem-header">
                <div class="problem-title-section">
                  <h2>{{ selectedProblem.problem_title || '题目详情' }}</h2>
                  <div class="problem-stats" v-if="problemStats">
                    <span class="stat-item">
                      <i class="el-icon-user"></i>
                      {{ problemStats.completed_student_count }} 人完成
                    </span>
                    <span class="stat-item">
                      <i class="el-icon-document"></i>
                      {{ problemStats.total_submission_count }} 次提交
                    </span>
                  </div>
                </div>
              </div>

              <!-- 题目内容 -->
              <div class="problem-content">
                <div v-html="selectedProblem.problem_content"></div>
              </div>

              <!-- 知识点 -->
              <div class="knowledge-points-section" v-if="selectedProblem">
                <h4>📚 知识点</h4>
                <div class="knowledge-points">
                  <el-tag
                    v-for="point in knowledgePoints"
                    :key="point"
                    type="info"
                    size="small"
                    class="knowledge-tag"
                  >
                    {{ point }}
                  </el-tag>
                  <span v-if="knowledgePoints.length === 0" class="no-knowledge">暂无知识点</span>
                </div>
              </div>
            </div>

            <!-- SQL编辑器 -->
            <div class="sql-editor-section">
              <div class="editor-header">
                <h4>SQL编辑器</h4>
                <div class="engine-selector">
                  <el-select v-model="selectedEngine" size="small" style="width: 120px">
                    <el-option label="MySQL" value="mysql" />
                    <el-option label="PostgreSQL" value="postgresql" />
                    <el-option label="OpenGauss" value="opengauss" />
                  </el-select>
                </div>
              </div>
              <div class="editor-container">
                <Codemirror v-model:value="sqlCode" :options="cmOptions" border height="200" />
              </div>
              <div class="editor-actions">
                <!-- 提交结果消息显示区域 -->
                <div
                  v-if="submitMessage"
                  class="submit-message-inline"
                  :class="`submit-message-${submitMessageType}`"
                >
                  {{ submitMessage }}
                </div>
                <div class="action-buttons">
                  <el-button type="primary" @click="submitSQL" :loading="submitting"
                    >提交</el-button
                  >
                  <el-button @click="clearSQL">清空</el-button>
                </div>
              </div>
            </div>

            <!-- 答题记录 -->
            <div class="answer-records">
              <h4>答题记录</h4>
              <!-- 移除暂无答题记录的提示 -->
              <div v-if="answerRecords.length > 0" class="records-list">
                <div
                  v-for="record in answerRecords"
                  :key="record.answer_record_id"
                  class="record-item"
                >
                  <div class="record-header">
                    <span class="record-id">#{{ record.answer_record_id }}</span>
                    <span class="record-time">{{ record.timestep }}</span>
                    <span class="record-status" :class="getStatusClass(record.result_type)">
                      {{ getStatusText(record.result_type) }}
                    </span>
                  </div>
                  <div class="record-content">
                    <code>{{ record.answer_content }}</code>
                  </div>
                  <div class="record-actions">
                    <el-button
                      type="primary"
                      size="small"
                      @click="analyzeWithAI(record)"
                      class="ai-analyze-btn"
                    >
                      <el-icon><DataAnalysis /></el-icon>
                      AI分析
                    </el-button>
                  </div>
                  <div v-if="record.aiAnalysis" class="ai-analysis">
                    <div class="ai-analysis-header">
                      <el-icon><DataAnalysis /></el-icon>
                      AI分析结果
                    </div>
                    <div class="ai-analysis-content">
                      {{ record.aiAnalysis }}
                    </div>
                  </div>
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
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="80px"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            placeholder="请输入原密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
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

    <!-- AI分析对话框 -->
    <el-dialog
      v-model="aiDialogVisible"
      title="AI分析结果"
      width="600px"
      :close-on-click-modal="false"
      class="modern-dialog ai-dialog"
    >
      <div class="ai-dialog-content">
        <div v-if="aiAnalyzing" class="ai-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>AI正在分析中，请稍候...</span>
        </div>
        <div class="ai-result">
          <div class="ai-result-content">
            {{ aiAnalysisResult }}
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeAiDialog">关闭</el-button>
          <el-button
            v-if="!aiAnalyzing && aiAnalysisResult && currentAnalyzingRecord"
            type="primary"
            @click="
              currentAnalyzingRecord.aiAnalysis = aiAnalysisResult;
              closeAiDialog();
            "
          >
            保存到记录
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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
  type FormInstance,
  type FormRules,
} from 'element-plus'
import {
  ArrowDown,
  ArrowLeft,
  DataAnalysis,
  Files,
  CollectionTag,
  Loading,
  SuccessFilled,
  WarningFilled,
} from '@element-plus/icons-vue'
import Codemirror from 'codemirror-editor-vue3'
import 'codemirror/mode/sql/sql.js'
import 'codemirror/theme/dracula.css'

const router = useRouter()

// 学生信息
const studentInfo = ref<any>({})

// 数据库模式相关
const schemaList = ref<any[]>([])
const selectedSchema = ref<string>('')
const selectedSchemaInfo = ref<any>(null)

// 题目相关
const allProblemsData = ref<any[]>([])
const currentProblems = ref<any[]>([])
const selectedProblem = ref<any>(null)
const problemStats = ref<any>(null)

// SQL编辑器
const selectedEngine = ref('mysql')
const sqlCode = ref('')
const cmOptions = {
  mode: 'text/x-sql',
  theme: 'dracula',
  lineNumbers: true,
  smartIndent: true,
  indentUnit: 2,
  foldGutter: true,
  gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
  autofocus: true,
  matchBrackets: true,
  autoCloseBrackets: true,
  extraKeys: { 'Ctrl-Space': 'autocomplete' },
}
const submitting = ref(false)

// 答题记录
const answerRecords = ref<any[]>([])

// 提交结果消息
const submitMessage = ref('')
const submitMessageType = ref<'success' | 'error' | 'warning' | ''>('')



// 密码修改相关
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// AI分析对话框相关
const aiDialogVisible = ref(false)
const aiAnalyzing = ref(false)
const aiAnalysisResult = ref('')
const currentAnalyzingRecord = ref<any>(null)

// 知识点计算属性
const knowledgePoints = computed(() => {
  if (!selectedProblem.value || !selectedProblem.value.knowledge) {
    return []
  }
  
  return selectedProblem.value.knowledge
    .split(/[,，;；、]/) // 支持中英文逗号、分号、顿号
    .map((point: string) => point.trim())
    .filter((point: string) => point.length > 0)
})

// 密码验证规则
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度必须在 6 到 50 个字符之间', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

// 页面初始化
onMounted(() => {
  fetchStudentInfo()
  fetchSchemaList()
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

// 获取数据库模式列表（学生版）
const fetchSchemaList = async () => {
  try {
    const response = await axios.get('/student/schema/list')
    if (response.data && Array.isArray(response.data)) {
      schemaList.value = response.data
    }
  } catch (error) {
    console.error('获取数据库模式列表失败:', error)
    ElMessage.error('获取数据库模式列表失败')
  }
}

// 获取题目列表
const fetchProblemList = async () => {
  try {
    const response = await axios.get('/public/problem/list')
    if (response.data && Array.isArray(response.data)) {
      allProblemsData.value = response.data
    }
  } catch (error) {
    console.error('获取题目列表失败:', error)
    ElMessage.error('获取题目列表失败')
  }
}

// 选择数据库模式
const selectSchema = (schema: any) => {
  selectedSchema.value = schema.schema_name
  selectedSchemaInfo.value = schema
  selectedProblem.value = null
  answerRecords.value = []

  // 找到对应的题目列表
  const schemaData = allProblemsData.value.find((item) => item.schema_name === schema.schema_name)
  if (schemaData && schemaData.problems) {
    currentProblems.value = schemaData.problems
  } else {
    currentProblems.value = []
  }
}

// 选择题目
const selectProblem = async (problem: any) => {
  selectedProblem.value = problem
  sqlCode.value = ''
  await fetchAnswerRecords(problem.problem_id)
  await fetchProblemStats(problem.problem_id)
}

// 返回模式页面
const backToSchema = () => {
  selectedProblem.value = null
  problemStats.value = null
}

// 获取题目统计信息
const fetchProblemStats = async (problemId: number) => {
  try {
    const response = await axios.get('/teacher/problem/summary', {
      params: { problem_id: problemId },
    })
    if (response.data && response.data.data) {
      problemStats.value = response.data.data
    }
  } catch (error) {
    console.error('获取题目统计失败:', error)
    problemStats.value = null
  }
}

// 获取答题记录
const fetchAnswerRecords = async (problemId: number) => {
  try {
    const response = await axios.get('/student/answers', {
      params: { problem_id: problemId },
    })
    if (response.data && response.data.records) {
      answerRecords.value = response.data.records
    } else {
      answerRecords.value = []
    }
  } catch (error) {
    // 未找到答题记录是正常情况，不显示任何错误提示
    answerRecords.value = []
  }
}

// 提交SQL
const submitSQL = async () => {
  if (!sqlCode.value.trim()) {
    ElMessage.warning('请输入SQL语句')
    return
  }

  if (!selectedProblem.value) {
    ElMessage.warning('请选择题目')
    return
  }

  try {
    submitting.value = true
    
    // 清除之前的提交消息
    submitMessage.value = ''
    submitMessageType.value = ''
    
    const response = await axios.post('/student/answer/submit', {
      problem_id: selectedProblem.value.problem_id,
      answer_content: sqlCode.value,
      engine_type: selectedEngine.value,
    })

    if (response.data) {
      const { result_type, message } = response.data
      if (result_type === 0) {
        submitMessage.value = message || 'SQL提交成功，答案正确！'
        submitMessageType.value = 'success'
        ElMessage.success(message || 'SQL提交成功，答案正确！')
      } else if (result_type === 1) {
        // 在编辑器下方显示语法错误
        submitMessage.value = message || 'SQL语法错误'
        submitMessageType.value = 'error'
        ElMessage.error(message || 'SQL语法错误')
      } else if (result_type === 2) {
        submitMessage.value = message || 'SQL结果错误'
        submitMessageType.value = 'warning'
        ElMessage.warning(message || 'SQL结果错误')
      }
    }

    // 重新获取答题记录
    await fetchAnswerRecords(selectedProblem.value.problem_id)
  } catch (error) {
    console.error('提交SQL失败:', error)
    ElMessage.error('提交SQL失败')
  } finally {
    submitting.value = false
  }
}

// 清空SQL
const clearSQL = () => {
  sqlCode.value = ''
}

// 格式化日期
const formatDate = (date: Date) => {
  return date.toISOString().slice(0, 19).replace('T', ' ')
}

// 获取状态样式类
const getStatusClass = (resultType: number) => {
  switch (resultType) {
    case 0:
      return 'success'
    case 1:
      return 'syntax-error'
    case 2:
      return 'result-error'
    default:
      return ''
  }
}

// 获取状态文本
const getStatusText = (resultType: number) => {
  switch (resultType) {
    case 0:
      return '正确'
    case 1:
      return '语法错误'
    case 2:
      return '结果错误'
    default:
      return '未知'
  }
}

// AI分析功能（流式输出）
const analyzeWithAI = async (record: any) => {
  if (!selectedProblem.value) {
    ElMessage.warning('请选择题目')
    return
  }

  // 打开对话框并设置初始状态
  currentAnalyzingRecord.value = record
  aiDialogVisible.value = true
  aiAnalyzing.value = true
  aiAnalysisResult.value = '正在连接AI服务，请稍候...'

  try {
    // 获取token
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      aiDialogVisible.value = false
      return
    }

    // 使用fetch进行流式请求
    const response = await fetch('http://wyaaa.gnway.cc:8000/student/answer/ai-analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        problem_id: selectedProblem.value.problem_id,
        answer_content: record.answer_content,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 处理流式响应
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (reader) {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === 'start') {
                // 开始分析
                aiAnalysisResult.value = data.message || '开始AI分析...'
              } else if (data.type === 'content') {
                // 追加内容
                aiAnalysisResult.value += data.content
              } else if (data.type === 'error') {
                // 错误处理
                aiAnalysisResult.value = data.message || 'AI分析失败'
                ElMessage.error('AI分析失败')
              } else if (data.type === 'done') {
                // 分析完成
                aiAnalyzing.value = false
                // 将结果保存到记录中
                record.aiAnalysis = aiAnalysisResult.value
                ElMessage.success('AI分析完成')
              }
            } catch (e) {
              // 忽略JSON解析错误
              console.warn('解析流式数据失败:', e)
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('AI分析失败:', error)
    aiAnalysisResult.value = 'AI分析失败，请稍后重试'
    aiAnalyzing.value = false
    ElMessage.error('AI分析失败，请稍后重试')
  }
}

// 关闭AI分析对话框
const closeAiDialog = () => {
  aiDialogVisible.value = false
  currentAnalyzingRecord.value = null
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
      new_password: passwordForm.value.newPassword,
    })

    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    resetPasswordForm()
  } catch (error: any) {
    console.error('修改密码失败:', error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: any; message?: string } } }
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
      type: 'warning',
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
  } catch (error) {
    // 用户取消退出
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  }
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}
</script>

<style scoped>
.modern-dialog .el-dialog__header {
  background-color: #f0f5ff;
  border-bottom: 1px solid #d9ecff;
  padding: 16px 24px;
}

/* AI分析对话框样式 */
.ai-dialog .el-dialog__header {
  background-color: #f0f9ff;
  border-bottom: 1px solid #bae6fd;
}

.ai-dialog-content {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}

.ai-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #409eff;
  font-size: 16px;
}

.ai-loading .el-icon {
  margin-right: 8px;
  font-size: 20px;
}

.ai-result {
  padding: 20px;
}

.ai-result-content {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  white-space: pre-wrap;
  line-height: 1.6;
  font-family: 'Courier New', monospace;
  color: #334155;
  min-height: 100px;
}

.ai-result-content:empty::before {
  content: '等待AI分析结果...';
  color: #94a3b8;
  font-style: italic;
}

.modern-dialog .el-dialog__title {
  color: #337ecc;
  font-weight: 600;
}

.modern-dialog .el-dialog__body {
  padding: 24px;
}

.modern-dialog .el-dialog__footer {
  padding: 16px 24px;
  background-color: #f8faff;
  border-top: 1px solid #d9ecff;
}

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
  background-color: #eef2f7; /* 浅蓝色调背景 */
}



/* 顶部导航栏 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #545c64;
  padding: 0 24px;
  height: 64px;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  margin-left: 24px;
  font-size: 16px;
  color: #ffffff;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-btn:hover {
  color: #cce5ff;
}

.logo {
  font-size: 22px;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
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
  padding: 0;
  overflow: hidden;
  margin: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 100%;
  box-sizing: border-box;
}

/* 任务页面布局 */
.task-wrapper {
  display: grid;
  grid-template-columns: 250px 300px 1fr;
  height: 100%;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel,
.middle-panel,
.right-panel {
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  height: calc(100vh - 104px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  background-color: white;
}

.panel-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 16px 20px;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #f0f0f0;
  color: #262626;
}

.schema-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.schema-item {
  padding: 16px 20px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition:
    background-color 0.3s,
    border-left 0.3s;
  border-left: 4px solid transparent;
}

.schema-item:hover {
  background-color: #f0f9ff;
  border-color: #409eff;
}

.schema-item.active {
  background-color: #d9ecff;
  border-left-color: #409eff;
  font-weight: 600;
  color: #337ecc;
}

.schema-name {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 4px;
}

.schema-author {
  font-size: 12px;
  opacity: 0.8;
}

/* 中间面板 */
.middle-panel {
  background-color: white;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.middle-panel .panel-header {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.schema-info h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.author {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

/* 数据库模式详情页面样式 */
.schema-detail-page {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.schema-header {
  margin-bottom: 30px;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 20px;
}

.schema-header h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1a1a1a;
}

.schema-header .author {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.schema-description {
  margin: 30px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #409eff;
}

.schema-description h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.schema-description div {
  color: #666;
  line-height: 1.8;
  font-size: 14px;
}

.schema-tables {
  margin: 30px 0;
}

.schema-tables h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.table-item {
  padding: 15px;
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.table-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.table-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.table-desc {
  color: #666;
  font-size: 12px;
}

/* 题目详情页面样式 */
.problem-detail-page {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  width: 100%;
}

.problem-detail-page.wide {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #fff;
  z-index: 100;
  padding: 20px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.back-button .el-button {
  background-color: #f0f5ff;
  color: #409eff;
  border-color: #d9ecff;
}

.back-button .el-button:hover {
  background-color: #d9ecff;
  border-color: #b3d8ff;
}

.problem-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.problem-title-section h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
  flex: 1;
}

.problem-stats {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #595959;
  margin-top: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: #f0f5ff;
  padding: 6px 12px;
  border-radius: 16px;
  color: #409eff;
  font-weight: 500;
}

.middle-panel .problems-section {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.right-panel .problems-section {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.problems-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 15px;
}

.problem-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.problem-item {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
  border-radius: 4px;
  margin-bottom: 8px;
}

.problem-item:hover {
  background-color: #f5f5f5;
}

.problem-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.problem-number {
  font-weight: 600;
  color: #409eff;
  font-size: 16px;
}

.problem-title {
  font-weight: 600;
  color: #333;
  font-size: 16px;
  margin: 10px 0;
  line-height: 1.4;
}

.problem-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.problem-date {
  color: #999;
}

.problem-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.problem-status.required {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.problem-status.optional {
  background-color: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

/* 右侧面板 */
.right-panel {
  background-color: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
}

.problem-detail {
  margin-bottom: 20px;
}

.problem-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}

.problem-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.problem-actions {
  display: flex;
  gap: 8px;
}

.schema-description {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.schema-description h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.problem-content {
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  line-height: 1.6;
}

/* SQL编辑器 */
.sql-editor-section {
  margin-bottom: 20px;
  padding: 24px;
  background-color: #1e1e1e;
  border-radius: 8px;
}

/* 编辑器操作区域 */
.editor-actions {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

/* 内联提交结果消息 */
.submit-message-inline {
  flex: 1;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 成功消息样式 */
.submit-message-success {
  color: #67c23a;
}

/* 错误消息样式 */
.submit-message-error {
  color: #f56c6c;
}

/* 警告消息样式 */
.submit-message-warning {
  color: #e6a23c;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.editor-header h4 {
  margin: 0;
  font-size: 14px;
  color: #fff;
}

.editor-container {
  margin-bottom: 16px;
}

.sql-textarea {
  font-family: 'Courier New', monospace;
}

/* 答题记录 */
.answer-records {
  flex: 1;
  overflow-y: auto;
  min-height: 360px; /* 原来300px增加20%: 300px * 1.2 = 360px */
}

.answer-records h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #333;
}

.no-records {
  text-align: center;
  color: #999;
  padding: 20px;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.record-item {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

.record-id {
  font-weight: bold;
  color: #333;
}

.record-time {
  color: #666;
}

.record-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
  border: 1px solid;
}

.record-status.success {
  color: #67c23a; /* 绿色 */
  background-color: #f0f9eb;
  border-color: #e1f3d8;
}

.record-status.syntax-error {
  color: #f56c6c; /* 红色 */
  background-color: #fef0f0;
  border-color: #fde2e2;
}

.record-status.result-error {
  color: #e6a23c; /* 橙色 */
  background-color: #fdf6ec;
  border-color: #faecd8;
}

.record-content {
  background-color: white;
  padding: 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  border: 1px solid #e9ecef;
}

.record-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.ai-analyze-btn {
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
}

.ai-analysis {
  margin-top: 12px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.ai-analysis-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
  font-size: 13px;
}

.ai-analysis-content {
  color: #333;
  line-height: 1.5;
  font-size: 13px;
  white-space: pre-wrap;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .task-wrapper {
    grid-template-columns: 200px 250px 1fr;
  }
}

@media (max-width: 768px) {
  .task-wrapper {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
  }

  .nav-buttons {
    display: none;
  }

  .left-panel,
  .middle-panel {
    max-height: 300px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0 10px;
  }

  .right-panel {
    padding: 10px;
  }

  .problem-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

/* 知识点样式 */
.knowledge-points-section {
  margin-top: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.knowledge-points-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.knowledge-points {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.knowledge-tag {
  margin: 0;
}

.no-knowledge {
  color: #999;
  font-size: 13px;
  font-style: italic;
}
</style>
