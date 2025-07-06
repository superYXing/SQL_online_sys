<template>
  <div class="teacher-score-calculate">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToHome">SQL在线实践平台</span>
        <div class="nav-buttons">
          <el-button type="text" @click="goToHome" class="nav-btn">首页</el-button>
          <el-button type="text" @click="goToDashboard" class="nav-btn">数据面板</el-button>
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
              <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="main-container">
      <el-main class="main-content">
        <div class="score-calculate-layout">
          <!-- 左侧题目选择区域 -->
          <div class="left-panel">
            <div class="problem-selection-card">
              <div class="section-header">
                <h3>📝 选择核算题目</h3>
                <el-button size="small" @click="refreshProblems" :loading="problemsLoading">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
              
              <div class="problems-container" v-loading="problemsLoading">
                <div v-for="schema in problemSchemas" :key="schema.schema_name" class="schema-group">
                  <div class="schema-title">
                    <el-checkbox 
                      :model-value="isSchemaAllSelected(schema.schema_name)"
                      :indeterminate="isSchemaIndeterminate(schema.schema_name)"
                      @change="handleSchemaSelectAll(schema.schema_name, ($event as boolean))"
                    >
                      {{ schema.schema_name }}
                    </el-checkbox>
                  </div>
                  
                  <div class="problems-list">
                    <el-checkbox-group v-model="selectedProblemIds">
                      <div v-for="(problem, index) in schema.problems" :key="problem.problem_id" class="problem-item">
                        <el-checkbox :label="problem.problem_id" class="problem-checkbox">
                          <div class="problem-content">
                            <span class="problem-id">题目 {{ index + 1 }}</span>
                            <span v-if="problem.is_required" class="required-tag">必做</span>
                          </div>
                        </el-checkbox>
                      </div>
                    </el-checkbox-group>
                  </div>
                </div>
              </div>
              
              <div class="calculate-actions">
                <el-button 
                  type="primary" 
                  size="large" 
                  @click="calculateScores" 
                  :loading="calculatingLoading"
                  :disabled="selectedProblemIds.length === 0"
                >
                  核算分数 ({{ selectedProblemIds.length }}题)
                </el-button>
              </div>
            </div>
          </div>

          <!-- 右侧学生成绩显示区域 -->
          <div class="right-panel">
            <div class="scores-display-card">
              <div class="section-header">
                <h3>📈 学生成绩</h3>
                <div class="header-actions">
                  <el-button size="small" @click="refreshScores" :loading="scoresLoading">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                  <el-button type="success" size="small" @click="exportExcel">
                    <el-icon><Download /></el-icon>
                    导出Excel
                  </el-button>
                </div>
              </div>
              
              <div class="scores-container" v-loading="scoresLoading">
                <div v-for="(courseGroup, index) in groupedScores" :key="courseGroup.courseId" class="course-group">
                  <div class="course-title" :class="`course-color-${index % 6}`">
                    <h4>{{ courseGroup.courseName }} ({{ courseGroup.students.length }}人)</h4>
                  </div>
                  
                  <el-table 
                    :data="courseGroup.students" 
                    border 
                    stripe
                    class="scores-table text-base"
                    size="default"
                    :header-cell-style="{ background: '#f8fafc', color: '#374151', fontWeight: '600', fontSize: '16px', padding: '16px 12px' }"
                    :cell-style="{ fontSize: '15px', padding: '14px 12px' }"
                  >
                    <el-table-column prop="student_id" label="学号" width="150" class-name="font-medium" />
                    <el-table-column prop="student_name" label="姓名" width="130" class-name="font-medium" />
                    <el-table-column prop="class_" label="班级" width="130" class-name="font-medium" />
                    <el-table-column prop="total_score" label="总分" width="120" align="center" class-name="font-semibold">
                      <template #default="scope">
                        <el-tag 
                          :type="getScoreTagType(scope.row.total_score)"
                          size="small"
                        >
                          {{ scope.row.total_score }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                
                <div v-if="groupedScores.length === 0 && !scoresLoading" class="empty-scores">
                  <el-empty description="暂无学生成绩数据" />
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
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
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
  ElTable,
  ElTableColumn,
  ElTag,
  ElCheckbox,
  ElCheckboxGroup,
  ElEmpty,
  type FormInstance,
  type FormRules
} from 'element-plus'
import { ArrowDown, Refresh, Download } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

// 类型定义
interface TeacherInfo {
  teacher_id?: string
  teacher_name?: string
  semester_name?: string
}

interface Problem {
  problem_id: number
  is_required: number
  problem_content: string
}

interface ProblemSchema {
  schema_name: string
  problems: Problem[]
}

interface StudentScore {
  course_id: string
  student_id: string
  student_name: string
  class_: string
  total_score: number
}

interface CourseGroup {
  courseId: string
  courseName: string
  students: StudentScore[]
}

const router = useRouter()
const route = useRoute()

// 响应式数据
const teacherInfo = ref<TeacherInfo>({})
const currentSemesterName = ref<string>('')
const problemSchemas = ref<ProblemSchema[]>([])
const selectedProblemIds = ref<number[]>([])
const studentScores = ref<StudentScore[]>([])

// 加载状态
const problemsLoading = ref(false)
const scoresLoading = ref(false)
const calculatingLoading = ref(false)

// 密码修改相关
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

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

// 计算属性：按课程分组的学生成绩
const groupedScores = computed(() => {
  const groups: { [courseId: string]: StudentScore[] } = {}
  
  studentScores.value.forEach(score => {
    if (!groups[score.course_id]) {
      groups[score.course_id] = []
    }
    groups[score.course_id].push(score)
  })
  
  return Object.keys(groups).map(courseId => ({
    courseId,
    courseName: `课序号：${courseId}`,
    students: groups[courseId].sort((a, b) => b.total_score - a.total_score)
  })).sort((a, b) => a.courseId.localeCompare(b.courseId))
})

// 获取教师信息
const fetchTeacherInfo = async () => {
  try {
    const response = await axios.get('/teacher/profile')
    if (response.data) {
      teacherInfo.value = response.data
    }
  } catch (error) {
    console.error('获取教师信息失败:', error)
    ElMessage.error('获取教师信息失败')
  }
}

// 获取当前学期信息
const fetchCurrentSemester = async () => {
  try {
    const semesterId = route.params.semester_id
    const response = await axios.get('/public/semesters')
    if (response.data && response.data.semesters) {
      const semester = response.data.semesters.find((s: any) => s.semester_id == semesterId)
      if (semester) {
        currentSemesterName.value = semester.semester_name
      }
    }
  } catch (error) {
    console.error('获取学期信息失败:', error)
    ElMessage.error('获取学期信息失败')
  }
}

// 获取所有题目列表
const fetchProblems = async () => {
  try {
    problemsLoading.value = true
    const response = await axios.get('/public/problem/list')
    if (response.data && Array.isArray(response.data)) {
      problemSchemas.value = response.data
    }
  } catch (error) {
    console.error('获取题目列表失败:', error)
    ElMessage.error('获取题目列表失败')
  } finally {
    problemsLoading.value = false
  }
}

// 获取学生分数
const fetchStudentScores = async () => {
  try {
    scoresLoading.value = true
    const response = await axios.get('/teacher/score')
    if (response.data && response.data.code === 200 && response.data.scorelist) {
      studentScores.value = response.data.scorelist
    }
  } catch (error) {
    console.error('获取学生分数失败:', error)
    ElMessage.error('获取学生分数失败')
  } finally {
    scoresLoading.value = false
  }
}

// 检查数据库模式是否全选
const isSchemaAllSelected = (schemaName: string) => {
  const schema = problemSchemas.value.find(s => s.schema_name === schemaName)
  if (!schema) return false
  
  const schemaProblemIds = schema.problems.map(p => p.problem_id)
  return schemaProblemIds.every(id => selectedProblemIds.value.includes(id))
}

// 检查数据库模式是否部分选中
const isSchemaIndeterminate = (schemaName: string) => {
  const schema = problemSchemas.value.find(s => s.schema_name === schemaName)
  if (!schema) return false
  
  const schemaProblemIds = schema.problems.map(p => p.problem_id)
  const selectedCount = schemaProblemIds.filter(id => selectedProblemIds.value.includes(id)).length
  return selectedCount > 0 && selectedCount < schemaProblemIds.length
}

// 处理数据库模式全选/取消全选
const handleSchemaSelectAll = (schemaName: string, checked: boolean) => {
  const schema = problemSchemas.value.find(s => s.schema_name === schemaName)
  if (!schema) return
  
  const schemaProblemIds = schema.problems.map(p => p.problem_id)
  
  if (checked) {
    // 添加该模式下所有题目
    schemaProblemIds.forEach(id => {
      if (!selectedProblemIds.value.includes(id)) {
        selectedProblemIds.value.push(id)
      }
    })
  } else {
    // 移除该模式下所有题目
    selectedProblemIds.value = selectedProblemIds.value.filter(id => !schemaProblemIds.includes(id))
  }
}

// 核算分数
const calculateScores = async () => {
  if (selectedProblemIds.value.length === 0) {
    ElMessage.warning('请先选择要核算的题目')
    return
  }
  
  try {
    calculatingLoading.value = true
    const response = await axios.put('/teacher/score/calculate', {
      problem_ids: selectedProblemIds.value
    })
    
    if (response.data && response.data.code === 200) {
      ElMessage.success('分数核算成功')
      // 重新获取学生分数
      await fetchStudentScores()
    } else {
      ElMessage.error(response.data.msg || '分数核算失败')
    }
  } catch (error: any) {
    console.error('分数核算失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('分数核算失败')
    }
  } finally {
    calculatingLoading.value = false
  }
}



// 获取分数标签类型
const getScoreTagType = (score: number) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'info'
  return 'danger'
}

// 刷新函数
const refreshProblems = () => {
  fetchProblems()
}

const refreshScores = () => {
  fetchStudentScores()
}

// 导出Excel
const exportExcel = () => {
  if (groupedScores.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  try {
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    
    // 为每个课程创建一个工作表
    groupedScores.value.forEach((courseGroup, index) => {
      const wsData = [
        ['学号', '姓名', '班级', '总分'] // 表头
      ]
      
      // 添加学生数据
      courseGroup.students.forEach(student => {
        wsData.push([
          student.student_id,
          student.student_name,
          student.class_,
          student.total_score
        ])
      })
      
      // 创建工作表
      const ws = XLSX.utils.aoa_to_sheet(wsData)
      
      // 设置列宽
      ws['!cols'] = [
        { wch: 15 }, // 学号
        { wch: 12 }, // 姓名
        { wch: 20 }, // 班级
        { wch: 10 }  // 总分
      ]
      
      // 添加工作表到工作簿
      const sheetName = `${courseGroup.courseName}`.replace(/[\\/:*?"<>|]/g, '_')
      XLSX.utils.book_append_sheet(wb, ws, sheetName)
    })
    
    // 创建汇总工作表
    const summaryData = [
      ['课程', '学号', '姓名', '班级', '总分'] // 表头
    ]
    
    // 添加所有学生数据到汇总表
    groupedScores.value.forEach(courseGroup => {
      courseGroup.students.forEach(student => {
        summaryData.push([
          courseGroup.courseName,
          student.student_id,
          student.student_name,
          student.class_,
          student.total_score
        ])
      })
    })
    
    // 创建汇总工作表
    const summaryWs = XLSX.utils.aoa_to_sheet(summaryData)
    
    // 设置汇总表列宽
    summaryWs['!cols'] = [
      { wch: 20 }, // 课程
      { wch: 15 }, // 学号
      { wch: 12 }, // 姓名
      { wch: 20 }, // 班级
      { wch: 10 }  // 总分
    ]
    
    // 将汇总表添加到工作簿的第一个位置
    XLSX.utils.book_append_sheet(wb, summaryWs, '汇总')
    
    // 重新排序工作表，将汇总表放在第一位
    const sheetNames = wb.SheetNames
    const summaryIndex = sheetNames.indexOf('汇总')
    if (summaryIndex > 0) {
      sheetNames.splice(summaryIndex, 1)
      sheetNames.unshift('汇总')
      wb.SheetNames = sheetNames
    }
    
    // 生成文件名
    const now = new Date()
    const dateStr = now.getFullYear() + 
      String(now.getMonth() + 1).padStart(2, '0') + 
      String(now.getDate()).padStart(2, '0') + 
      '_' + 
      String(now.getHours()).padStart(2, '0') + 
      String(now.getMinutes()).padStart(2, '0')
    
    const fileName = `学生成绩_${currentSemesterName.value || '未知学期'}_${dateStr}.xlsx`
    
    // 导出文件
    XLSX.writeFile(wb, fileName)
    
    ElMessage.success('Excel导出成功！')
  } catch (error) {
    console.error('导出Excel失败:', error)
    ElMessage.error('导出Excel失败，请重试')
  }
}

// 导航函数
const goToHome = () => {
  router.push('/teacher/home')
}

const goToDashboard = () => {
  router.push('/teacher/dashboard')
}

const goToDatabaseSchema = () => {
  router.push('/teacher/database-schema')
}

const goToProblem = () => {
  ElMessage.info('题目管理功能正在开发中，敬请期待！')
}

const goToStudentInfo = () => {
  router.push('/teacher/student-info')
}

// 下拉菜单命令处理
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
    
    const response = await axios.put('/auth/password', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    
    if (response.data.code === 200) {
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
      resetPasswordForm()
    } else {
      ElMessage.error(response.data.message || '密码修改失败')
    }
  } catch (error: any) {
    console.error('修改密码失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('修改密码失败')
    }
  } finally {
    passwordLoading.value = false
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
  passwordFormRef.value?.clearValidate()
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    router.push('/login')
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消退出
  }
}

// 页面初始化
onMounted(() => {
  fetchTeacherInfo()
  fetchCurrentSemester()
  fetchProblems()
  fetchStudentScores()
})
</script>

<style scoped>
.teacher-score-calculate {
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
  background: #f5f7fa;
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
  gap: 32px;
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

.nav-btn.active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.username-dropdown {
  font-size: 14px;
  font-weight: bold;
  color: white !important;
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



.main-content {
  padding: 24px;
  height: 100%;
  overflow: auto;
}

.score-calculate-layout {
  display: flex;
  gap: 24px;
  height: 100%;
  min-height: calc(100vh - 108px);
}

/* 左侧题目选择区域 */
.left-panel {
  flex: 0 0 350px;
  display: flex;
  flex-direction: column;
}

.problem-selection-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.problems-container {
  flex: 1;
  overflow-y: auto;
}

.schema-group {
  margin-bottom: 32px;
}

.schema-title {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.schema-title .el-checkbox {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.problems-list {
  padding-left: 24px;
}

.problem-item {
  margin-bottom: 12px;
  padding: 16px;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  background: #fff;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.problem-item:hover {
  border-color: #409eff;
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.problem-checkbox {
  width: 100%;
}

.problem-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  margin-left: 8px;
}

.problem-id {
  font-weight: 700;
  color: #409eff;
  font-size: 14px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  padding: 4px 12px;
  border-radius: 20px;
  display: inline-block;
  width: fit-content;
}

.required-tag {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  align-self: flex-start;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}



.calculate-actions {
  margin-top: 20px;
}

.calculate-actions .el-button {
  width: 100%;
}

/* 右侧学生成绩区域 */
.right-panel {
  flex: 1;
  min-width: 0;
  margin-right: -24px;
  padding-right: 24px;
}

.scores-display-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.scores-container {
  flex: 1;
  overflow-y: auto;
}

.scores-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.scores-table .el-table__header-wrapper {
  border-radius: 8px 8px 0 0;
}

.scores-table .el-table__body-wrapper {
  border-radius: 0 0 8px 8px;
}

.scores-table .el-table__row:hover {
  background-color: #f8fafc !important;
}

.scores-table .el-table__cell {
  border-bottom: 1px solid #e5e7eb;
}

.scores-table .el-tag {
  font-weight: 600;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 6px;
}

.course-group {
  margin-bottom: 24px;
}

.course-title {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
}

.course-title h4 {
  margin: 0;
  color: #409eff;
  font-size: 14px;
}

/* 课序号颜色区分 */
.course-color-0 {
  background: #f0f9ff;
  border-left-color: #409eff;
}

.course-color-0 h4 {
  color: #409eff;
}

.course-color-1 {
  background: #f0f9f0;
  border-left-color: #67c23a;
}

.course-color-1 h4 {
  color: #67c23a;
}

.course-color-2 {
  background: #fef0f0;
  border-left-color: #f56c6c;
}

.course-color-2 h4 {
  color: #f56c6c;
}

.course-color-3 {
  background: #fdf6ec;
  border-left-color: #e6a23c;
}

.course-color-3 h4 {
  color: #e6a23c;
}

.course-color-4 {
  background: #f4f4f5;
  border-left-color: #909399;
}

.course-color-4 h4 {
  color: #909399;
}

.course-color-5 {
  background: #f5f0ff;
  border-left-color: #9c27b0;
}

.course-color-5 h4 {
  color: #9c27b0;
}

.scores-table {
  margin-bottom: 16px;
}

.empty-scores {
  padding: 40px;
  text-align: center;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .score-calculate-layout {
    flex-direction: column;
  }
  
  .left-panel,
  .right-panel {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }
  
  .score-calculate-layout {
    gap: 16px;
  }
  
  .nav-buttons {
    display: none;
  }
}
</style>