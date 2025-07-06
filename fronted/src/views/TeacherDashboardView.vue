<template>
  <div class="teacher-dashboard">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToHome">SQL在线实践平台</span>
        <div class="nav-buttons">
          <el-button type="text" @click="goToHome" class="nav-btn">首页</el-button>
          <el-button type="text" class="nav-btn active">数据面板</el-button>
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
        <div class="dashboard-layout">
          <!-- 左侧排行榜 -->
          <div class="left-panel">
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

          <!-- 中间区域 -->
          <div class="center-panel">
            <!-- 上半部分：态势矩阵 -->
            <div class="matrix-section">
              <div class="section-header">
                <h3>📊 态势矩阵</h3>
                <el-button size="small" @click="refreshMatrix" :loading="matrixLoading">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
              <div class="matrix-container" v-loading="matrixLoading">
                <el-table
                  :data="matrixData"
                  border
                  stripe
                  class="matrix-table"
                  max-height="300"
                >
                  <el-table-column prop="semester_name" label="学期" width="150" fixed="left" />
                  <el-table-column
                    v-for="dataset in datasets"
                    :key="dataset.schema_name"
                    :prop="`schema_${dataset.schema_name}`"
                    :label="dataset.schema_name"
                    width="120"
                    align="center"
                  >
                    <template #default="scope">
                      <el-tag
                        type="primary"
                        size="small"
                        class="matrix-cell"
                        @click="handleMatrixCellClick(dataset.schema_name, scope.row.semester_id)"
                      >
                        {{ dataset.schema_name }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>

            <!-- 下半部分：核算上机课程分数 -->
            <div class="score-section">
              <div class="section-header">
                <h3>📈 核算上机课程分数</h3>
              </div>
              <div class="semester-buttons-container">
                <el-button
                  v-for="semester in semesters"
                  :key="semester.semester_id"
                  type="primary"
                  size="large"
                  class="semester-btn"
                  @click="goToScoreCalculate(semester.semester_id)"
                >
                  {{ semester.semester_name }}
                </el-button>
              </div>
            </div>
          </div>

          <!-- 右侧数据集 -->
          <div class="right-panel">
            <div class="dataset-card">
              <div class="section-header">
                <h3>📁 数据集</h3>
                <el-button type="primary" @click="exportData" :loading="exportLoading">
                  导出数据
                </el-button>
              </div>

              <!-- 选择学期 -->
              <div class="export-section">
                <h4>选择学期（支持多选）</h4>
                <el-checkbox-group v-model="selectedSemesterIds" class="semester-checkbox-group">
                  <el-checkbox
                    v-for="semester in semesters"
                    :key="semester.semester_id"
                    :label="semester.semester_id"
                    class="semester-checkbox"
                  >
                    {{ semester.semester_name }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>

              <!-- 元数据选择 -->
              <div class="export-section">
                <h4>数据类型</h4>
                <el-radio-group v-model="selectedMetadata" class="metadata-radio-group">
                  <el-radio label="基础版" class="metadata-radio">
                    <div class="metadata-option">
                      <div class="option-title">基础版 - 原始答题记录</div>
                      <div class="option-desc">包含：学生ID、题目内容、答题结果、学生答案、提交时间</div>
                    </div>
                  </el-radio>
                  <el-radio label="统计版" class="metadata-radio">
                    <div class="metadata-option">
                      <div class="option-title">统计版 - 按学生统计</div>
                      <div class="option-desc">包含：学生ID、答题题目数、总提交次数、正确次数、错误次数、正确率、最后提交时间</div>
                    </div>
                  </el-radio>
                  <el-radio label="分析版" class="metadata-radio">
                    <div class="metadata-option">
                      <div class="option-title">分析版 - 按题目统计</div>
                      <div class="option-desc">包含：题目内容、参与学生数、总提交次数、正确提交次数、错误提交次数、正确率、首次提交时间、最后提交时间</div>
                    </div>
                  </el-radio>
                </el-radio-group>
              </div>

              <!-- 导出格式 -->
              <div class="export-section">
                <h4>导出格式</h4>
                <el-radio-group v-model="selectedFormat" class="format-radio-group">
                  <el-radio label="JSON" class="format-radio">JSON</el-radio>
                  <el-radio label="XML" class="format-radio">XML</el-radio>
                  <el-radio label="XLSX" class="format-radio">XLSX</el-radio>
                </el-radio-group>
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
  ElTable,
  ElTableColumn,
  ElTag,
  ElRadio,
  ElRadioGroup,
  ElCheckbox,
  ElCheckboxGroup,
  type FormInstance,
  type FormRules
} from 'element-plus'
import { ArrowDown, Refresh, Grid } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

// 类型定义
interface RankingItem {
  名次: number
  姓名: string
  题目数: number
  方法数: number
}

interface TeacherInfo {
  teacher_id?: string
  teacher_name?: string
  semester_name?: string
}

interface Semester {
  semester_id: number
  semester_name: string
  begin_date: string
  end_date: string
  is_current: boolean
}

interface Dataset {
  schema_name: string
  schema_description: string
  schema_author: string
}

interface MatrixRow {
  semester_name: string
  semester_id: number
  [key: string]: any
}

interface ScoreRow {
  course_name: string
  [key: string]: any
}

interface StudentProblemRecord {
  student_id: string
  problem_content: string
  result_type: number
  answer_content: string
  timestep: string
}

const router = useRouter()

// 响应式数据
const rankingData = ref<RankingItem[]>([])
const teacherInfo = ref<TeacherInfo>({})
const semesters = ref<Semester[]>([])
const datasets = ref<Dataset[]>([])
const matrixData = ref<MatrixRow[]>([])
const scoresData = ref<ScoreRow[]>([])
const selectedDataset = ref<Dataset | null>(null)
const selectedSchemaId = ref<number | null>(null)

// 导出相关数据
const selectedSemesterIds = ref<number[]>([])
const selectedMetadata = ref<string>('基础版')
const selectedFormat = ref<string>('XLSX')
const exportLoading = ref(false)

// 加载状态
const rankingLoading = ref(false)
const teacherLoading = ref(false)
const matrixLoading = ref(false)
const scoresLoading = ref(false)
const datasetsLoading = ref(false)

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

// 获取排行榜数据
const fetchRankingData = async () => {
  try {
    rankingLoading.value = true
    const response = await axios.get('/student/rank')
    if (response.data && Array.isArray(response.data)) {
      rankingData.value = response.data
    }
  } catch (error) {
    console.error('获取排行榜数据失败:', error)
    ElMessage.error('获取排行榜数据失败')
  } finally {
    rankingLoading.value = false
  }
}

// 获取教师信息
const fetchTeacherInfo = async () => {
  try {
    teacherLoading.value = true
    const response = await axios.get('/teacher/profile')
    if (response.data) {
      teacherInfo.value = response.data
    }
  } catch (error) {
    console.error('获取教师信息失败:', error)
    ElMessage.error('获取教师信息失败')
  } finally {
    teacherLoading.value = false
  }
}

// 获取所有学期
const fetchSemesters = async () => {
  try {
    const response = await axios.get('/public/semesters')
    if (response.data && response.data.semesters) {
      semesters.value = response.data.semesters
    }
  } catch (error) {
    console.error('获取学期数据失败:', error)
    ElMessage.error('获取学期数据失败')
  }
}

// 获取数据集
const fetchDatasets = async () => {
  try {
    datasetsLoading.value = true
    const response = await axios.get('/public/schema/list')
    if (response.data && Array.isArray(response.data)) {
      datasets.value = response.data
    }
  } catch (error) {
    console.error('获取数据集失败:', error)
    ElMessage.error('获取数据集失败')
  } finally {
    datasetsLoading.value = false
  }
}

// 生成模拟态势矩阵数据
const generateMatrixData = () => {
  matrixLoading.value = true
  setTimeout(() => {
    // 转置矩阵结构：行为学期，列为数据库模式
    const data: MatrixRow[] = []

    // 为每个学期创建一行
    semesters.value.forEach(semester => {
      const row: MatrixRow = {
        semester_name: semester.semester_name,
        semester_id: semester.semester_id
      }
      // 为每个数据库模式创建列，内容填充数据库模式名称
      datasets.value.forEach(dataset => {
        row[`schema_${dataset.schema_name}`] = dataset.schema_name
      })
      data.push(row)
    })

    matrixData.value = data
    matrixLoading.value = false
  }, 1000)
}

// 生成模拟分数数据
const generateScoresData = () => {
  scoresLoading.value = true
  setTimeout(() => {
    const courses = ['数据库原理', 'SQL基础', '高级查询', '数据分析', '系统设计']
    const data: ScoreRow[] = []
    courses.forEach(course => {
      const row: ScoreRow = {
        course_name: course
      }
      semesters.value.forEach(semester => {
        row[`semester_${semester.semester_id}`] = (Math.random() * 40 + 60).toFixed(1)
      })
      data.push(row)
    })
    scoresData.value = data
    scoresLoading.value = false
  }, 800)
}

// 获取矩阵标签类型
const getMatrixTagType = (value: number) => {
  if (value >= 80) return 'success'
  if (value >= 60) return 'warning'
  if (value >= 40) return 'info'
  return 'danger'
}

// 选择数据集
const selectDataset = (dataset: Dataset) => {
  selectedDataset.value = dataset
  // 假设数据集有schema_id字段，如果没有则需要从datasets数组中找到对应的ID
  const schemaIndex = datasets.value.findIndex(d => d.schema_name === dataset.schema_name)
  selectedSchemaId.value = schemaIndex + 1 // 临时使用索引+1作为ID
  ElMessage.success(`已选择数据集: ${dataset.schema_name}`)
}

// 处理态势矩阵单元格点击
const handleMatrixCellClick = (schemaName: string, semesterId: number) => {
  // 记住数据库模式ID
  const schemaIndex = datasets.value.findIndex(d => d.schema_name === schemaName)
  selectedSchemaId.value = schemaIndex + 1 // 临时使用索引+1作为ID

  // 将选中的数据库模式信息和学期信息保存到localStorage
  localStorage.setItem('selectedSchemaId', String(selectedSchemaId.value))
  localStorage.setItem('selectedSchemaName', schemaName)
  localStorage.setItem('selectedSemesterId', String(semesterId))

  // 跳转到态势矩阵详情页面，使用学期ID作为路由参数
  router.push(`/teacher/dashboard/matrix/${semesterId}`)
}

// 刷新函数
const refreshMatrix = () => {
  generateMatrixData()
}

const goToScoreCalculate = (semesterId: number) => {
  router.push(`/teacher/dashboard/score-calculate/${semesterId}`)
}

// 导出数据函数
const exportData = async () => {
  if (!selectedSemesterIds.value || selectedSemesterIds.value.length === 0) {
    ElMessage.warning('请先选择至少一个学期')
    return
  }

  try {
    exportLoading.value = true

    // 调用新的API接口获取学生答题记录
    const response = await axios.post('/teacher/student/answer-records', {
      semester_ids: selectedSemesterIds.value
    })

    if (!response.data || !response.data.data) {
      ElMessage.error('获取学生答题记录失败')
      return
    }

    const studentRecords: StudentProblemRecord[] = response.data.data

    if (studentRecords.length === 0) {
      ElMessage.warning('该学期暂无学生答题记录')
      return
    }

    // 根据选择的元数据类型生成不同版本的导出数据
    let exportData: any
    let fileName: string
    const currentDate = new Date().toISOString().split('T')[0]
    const selectedSemesters = semesters.value.filter(s => selectedSemesterIds.value.includes(s.semester_id))
    const semesterNames = selectedSemesters.map(s => s.semester_name).join('_')
    const semesterName = semesterNames || 'unknown'

    switch (selectedMetadata.value) {
      case '基础版':
        exportData = generateVersion1Data(studentRecords)
        fileName = `学生答题记录_基础版_${semesterName}_${currentDate}`
        break
      case '统计版':
        exportData = generateVersion2Data(studentRecords)
        fileName = `学生答题记录_统计版_${semesterName}_${currentDate}`
        break
      case '分析版':
        exportData = generateVersion3Data(studentRecords)
        fileName = `学生答题记录_分析版_${semesterName}_${currentDate}`
        break
      default:
        exportData = generateVersion1Data(studentRecords)
        fileName = `学生答题记录_${semesterName}_${currentDate}`
    }

    // 根据选择的格式导出数据
    if (selectedFormat.value === 'JSON') {
      downloadJSON(exportData, `${fileName}.json`)
    } else if (selectedFormat.value === 'XML') {
      downloadXML(exportData, `${fileName}.xml`)
    } else {
      downloadXLSX(exportData, `${fileName}.xlsx`)
    }

    ElMessage.success('数据导出成功')
  } catch (error: any) {
    console.error('导出数据失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('导出数据失败')
    }
  } finally {
    exportLoading.value = false
  }
}

const refreshDatasets = () => {
  fetchDatasets()
}

// 导航函数
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
// 生成版本1数据：基础版 - 原始答题记录
const generateVersion1Data = (records: StudentProblemRecord[]) => {
  return records.map(record => ({
    学生ID: record.student_id,
    题目内容: record.problem_content,
    答题结果: record.result_type === 1 ? '正确' : '错误',
    学生答案: record.answer_content,
    提交时间: record.timestep
  }))
}

// 生成版本2数据：统计版 - 按学生统计
const generateVersion2Data = (records: StudentProblemRecord[]) => {
  const studentStats = new Map()
  
  records.forEach(record => {
    const studentId = record.student_id
    if (!studentStats.has(studentId)) {
      studentStats.set(studentId, {
        学生ID: studentId,
        总提交次数: 0,
        正确次数: 0,
        错误次数: 0,
        正确率: '0%',
        最后提交时间: record.timestep,
        答题题目数: new Set()
      })
    }
    
    const stats = studentStats.get(studentId)
    stats.总提交次数++
    stats.答题题目数.add(record.problem_content)
    if (record.result_type === 1) {
      stats.正确次数++
    } else {
      stats.错误次数++
    }
    stats.正确率 = `${((stats.正确次数 / stats.总提交次数) * 100).toFixed(1)}%`
    
    // 更新最后提交时间
    if (new Date(record.timestep) > new Date(stats.最后提交时间)) {
      stats.最后提交时间 = record.timestep
    }
  })
  
  return Array.from(studentStats.values()).map(stats => ({
    学生ID: stats.学生ID,
    答题题目数: stats.答题题目数.size,
    总提交次数: stats.总提交次数,
    正确次数: stats.正确次数,
    错误次数: stats.错误次数,
    正确率: stats.正确率,
    最后提交时间: stats.最后提交时间
  }))
}

// 生成版本3数据：分析版 - 按题目统计
const generateVersion3Data = (records: StudentProblemRecord[]) => {
  const problemStats = new Map()
  
  records.forEach(record => {
    const problemContent = record.problem_content
    if (!problemStats.has(problemContent)) {
      problemStats.set(problemContent, {
        题目内容: problemContent,
        参与学生: new Set(),
        总提交次数: 0,
        正确提交次数: 0,
        错误提交次数: 0,
        正确率: '0%',
        首次提交时间: record.timestep,
        最后提交时间: record.timestep
      })
    }
    
    const stats = problemStats.get(problemContent)
    stats.参与学生.add(record.student_id)
    stats.总提交次数++
    if (record.result_type === 1) {
      stats.正确提交次数++
    } else {
      stats.错误提交次数++
    }
    stats.正确率 = `${((stats.正确提交次数 / stats.总提交次数) * 100).toFixed(1)}%`
    
    // 更新时间范围
    if (new Date(record.timestep) < new Date(stats.首次提交时间)) {
      stats.首次提交时间 = record.timestep
    }
    if (new Date(record.timestep) > new Date(stats.最后提交时间)) {
      stats.最后提交时间 = record.timestep
    }
  })
  
  return Array.from(problemStats.values()).map(stats => ({
    题目内容: stats.题目内容.length > 100 ? stats.题目内容.substring(0, 100) + '...' : stats.题目内容,
    参与学生数: stats.参与学生.size,
    总提交次数: stats.总提交次数,
    正确提交次数: stats.正确提交次数,
    错误提交次数: stats.错误提交次数,
    正确率: stats.正确率,
    首次提交时间: stats.首次提交时间,
    最后提交时间: stats.最后提交时间
  }))
}

// 下载JSON格式文件
const downloadJSON = (data: any, filename: string) => {
  const jsonStr = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// 下载XML格式文件
const downloadXML = (data: any, filename: string) => {
  let xmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n<records>\n'
  data.forEach((item: any, index: number) => {
    xmlStr += `  <record id="${index + 1}">\n`
    Object.keys(item).forEach(key => {
      const value = String(item[key]).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      xmlStr += `    <${key}>${value}</${key}>\n`
    })
    xmlStr += '  </record>\n'
  })
  xmlStr += '</records>'
  
  const blob = new Blob([xmlStr], { type: 'application/xml' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// 下载XLSX格式文件
const downloadXLSX = (data: any, filename: string) => {
  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')
  
  // 设置列宽
  const colWidths = Object.keys(data[0] || {}).map(() => ({ wch: 20 }))
  worksheet['!cols'] = colWidths
  
  XLSX.writeFile(workbook, filename)
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
      ElMessage.error('密码修改失败')
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

    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
  passwordFormRef.value?.resetFields()
}

// 组件挂载时获取数据
onMounted(async () => {
  await Promise.all([
    fetchRankingData(),
    fetchTeacherInfo(),
    fetchSemesters(),
    fetchDatasets()
  ])

  // 在获取基础数据后生成矩阵和分数数据
  generateMatrixData()
  generateScoresData()
})
</script>

<style scoped>
.teacher-dashboard {
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

/* 仪表板布局 */
.dashboard-layout {
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 108px);
}

.left-panel {
  flex: 1;
  min-width: 0;
}

.center-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

/* 卡片通用样式 */
.ranking-card,
.dataset-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 100%;
}

.matrix-section,
.score-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  flex: 1;
}

/* 区域标题 */
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

/* 排行榜样式 */
.ranking-card h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.ranking-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  background: #f8fafc;
  transition: all 0.3s;
}

.ranking-item:hover {
  background: #e2e8f0;
  transform: translateX(4px);
}

.ranking-item.top-three {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.rank-number {
  width: 40px;
  text-align: center;
  font-weight: 600;
  margin-right: 12px;
}

.student-info {
  flex: 1;
}

.student-name {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.student-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

/* 矩阵和分数表格样式 */
.matrix-container,
.scores-container {
  border-radius: 8px;
  overflow: hidden;
}

.matrix-table,
.scores-table {
  width: 100%;
}

.matrix-cell {
  cursor: pointer;
  transition: all 0.3s;
}

.matrix-cell:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.score-value {
  font-weight: 500;
  color: #059669;
}

/* 学期按钮样式 */
.semester-buttons-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.semester-btn {
  min-width: 120px;
  height: 50px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s;
}

.semester-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

/* 数据集样式 */
.dataset-card h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

/* 导出区域样式 */
.export-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.export-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.semester-checkbox-group,
.semester-radio-group,
.format-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metadata-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

.semester-checkbox,
.semester-radio,
.metadata-radio,
.format-radio {
  margin: 0;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  transition: all 0.3s;
}

.semester-checkbox:hover,
.semester-radio:hover,
.metadata-radio:hover,
.format-radio:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.semester-checkbox.is-checked,
.semester-radio.is-checked,
.metadata-radio.is-checked,
.format-radio.is-checked {
  border-color: #3b82f6;
  background: #dbeafe;
}

.metadata-radio {
  font-size: 12px;
  line-height: 1.4;
}

.metadata-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-title {
  font-weight: 600;
  font-size: 14px;
  color: #1f2937;
}

.option-desc {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.3;
}

.datasets-container {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.dataset-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 8px;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.dataset-item:hover {
  background: #e2e8f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dataset-item.active {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border-color: #3b82f6;
}

.dataset-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 12px;
  flex-shrink: 0;
}

.dataset-info {
  flex: 1;
}

.dataset-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.dataset-author {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.dataset-desc {
  font-size: 12px;
  color: #4b5563;
  line-height: 1.4;
  max-height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .dashboard-layout {
    flex-direction: column;
  }

  .left-panel,
  .right-panel {
    width: 100%;
  }

  .center-panel {
    order: -1;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .dashboard-layout {
    gap: 16px;
  }

  .nav-buttons {
    display: none;
  }
}
</style>
