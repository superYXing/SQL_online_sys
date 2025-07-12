<template>
  <div class="teacher-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToHome">SQL在线实践平台</span>
        <div class="nav-buttons">
          <el-button type="text" @click="goToDashboard" class="nav-btn">数据面板</el-button>
          <el-button type="text" @click="goToDatabaseSchema" class="nav-btn">数据库模式</el-button>
          <el-button type="text" @click="goToProblem" class="nav-btn">题目</el-button>
          <el-button type="text" @click="goToStudentInfo" class="nav-btn active"
            >学生信息</el-button
          >
        </div>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand" trigger="click">
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
      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="student-wrapper" :class="{ 'has-selection': selectedSemester }">
          <!-- 左侧：选择学期 -->
          <div class="left-panel">
            <div class="panel-header">
              <el-button @click="goBack" type="text" class="back-btn">
                <el-icon><ArrowLeft /></el-icon>
                返回
              </el-button>
              <h3>
                <el-icon><Calendar /></el-icon> 选择一个学期
              </h3>
            </div>
            <div class="semester-list">
              <div
                v-for="semester in semesterList"
                :key="semester.semester_id"
                class="semester-item"
                :class="{
                  active: selectedSemester === semester.semester_id,
                  current: semester.is_current,
                }"
                @click="selectSemester(semester)"
              >
                <div class="semester-name">{{ semester.semester_name }}</div>
                <div class="semester-date">
                  {{ semester.begin_date }} 至 {{ semester.end_date }}
                </div>
                <div v-if="semester.is_current" class="current-tag">当前学期</div>
              </div>
            </div>
          </div>

          <!-- 中间：添加选课记录（选择学期后显示） -->
          <div class="middle-panel" v-if="selectedSemester">
            <div class="panel-header">
              <h3>
                <el-icon><Plus /></el-icon> 添加选课记录
              </h3>
            </div>

            <!-- 手动导入 -->
            <div class="import-section">
              <h4>手动导入</h4>
              <el-form
                :model="studentForm"
                :rules="studentFormRules"
                ref="studentFormRef"
                label-width="80px"
                size="small"
              >
                <el-form-item label="学号" prop="student_id">
                  <el-input v-model="studentForm.student_id" placeholder="请输入学号" />
                </el-form-item>
                <el-form-item label="姓名" prop="student_name">
                  <el-input v-model="studentForm.student_name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="班级" prop="class_">
                  <el-input v-model="studentForm.class_" placeholder="请输入班级" />
                </el-form-item>
                <el-form-item label="状态" prop="status">
                  <el-select v-model="studentForm.status" placeholder="请选择状态">
                    <el-option label="正常" :value="0" />
                    <el-option label="重修" :value="1" />
                  </el-select>
                </el-form-item>
                <el-form-item label="课程ID" prop="course_id">
                  <el-input
                    v-model="studentForm.course_id"
                    placeholder="请输入课程ID"
                    type="number"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="addStudent" :loading="addingStudent"
                    >添加</el-button
                  >
                  <el-button @click="resetStudentForm">重置</el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 自动导入 -->
            <div class="import-section">
              <h4>自动导入</h4>
              <div class="upload-area">
                <el-upload
                  ref="uploadRef"
                  :auto-upload="false"
                  :show-file-list="true"
                  :limit="1"
                  accept=".xlsx,.xls"
                  @change="handleFileChange"
                  class="upload-demo"
                >
                  <el-button size="small" type="primary">选择Excel文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      只能上传xlsx/xls文件，且不超过500kb<br />
                      Excel模板字段：student_id(学号), student_name(姓名), class_(班级),
                      status(状态：0=正常，1=重修), course_id(课程ID)<br />
                      <strong>模板数据示例：</strong><br />
                      <code
                        style="
                          font-size: 12px;
                          background: #f5f5f5;
                          padding: 2px 4px;
                          border-radius: 3px;
                        "
                      >
                        student_id: 202322511772, student_name: 张三零, class_: 23级1班, status: 0,
                        course_id: 1<br />
                        student_id: 202346511822, student_name: 李四飒, class_: 23级1班, status: 1,
                        course_id: 1
                      </code>
                    </div>
                  </template>
                </el-upload>

                <el-button type="info" @click="downloadTemplate" class="template-btn">
                  <el-icon><Download /></el-icon>
                  下载模板
                </el-button>
              </div>
            </div>
          </div>

          <!-- 右侧：学生选课记录表（选择学期后显示） -->
          <div class="right-panel" v-if="selectedSemester">
            <div class="panel-header">
              <h3>
                <el-icon><User /></el-icon> 学生选课记录
              </h3>
              <div class="search-box">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索学号或姓名"
                  @input="handleSearch"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
            </div>

            <div class="table-container">
              <el-table
                :data="studentList"
                border
                stripe
                v-loading="studentsLoading"
                class="student-table"
                :header-cell-style="{ background: '#409eff', color: '#fff' }"
              >
                <el-table-column prop="student_id" label="学号" width="120" sortable />
                <el-table-column prop="student_name" label="姓名" width="100" />
                <el-table-column prop="class_" label="班级" width="150" />
                <el-table-column prop="teacher_name" label="教师" width="100" />
                <el-table-column prop="semester_name" label="学期" width="120" />
                <el-table-column prop="course_id" label="课程ID" width="80" />
                <el-table-column label="状态" width="80">
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 0 ? 'success' : 'warning'">
                      {{ scope.row.status === 0 ? '正常' : '重修' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180" fixed="right">
                  <template #default="scope">
                    <el-button type="primary" size="small" @click="viewStudentDetail(scope.row)">
                      详情
                    </el-button>
                    <el-button type="warning" size="small" @click="editStudent(scope.row)">
                      编辑
                    </el-button>
                    <el-button type="danger" size="small" @click="deleteStudent(scope.row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 分页 -->
              <div class="pagination-container">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="total"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- 学生详情对话框 -->
    <el-dialog v-model="studentDetailVisible" title="学生详细信息" width="500px">
      <div v-loading="studentDetailLoading" class="student-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学号">{{ studentDetail.student_id }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ studentDetail.student_name }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ studentDetail.class_ }}</el-descriptions-item>
          <el-descriptions-item label="课程ID">{{ studentDetail.course_id }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="studentDetailVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑学生对话框 -->
    <el-dialog v-model="editStudentVisible" title="编辑学生信息" width="500px">
      <el-form
        :model="editStudentForm"
        :rules="editStudentRules"
        ref="editStudentFormRef"
        label-width="100px"
      >
        <el-form-item label="学号">
          <el-input v-model="editStudentForm.student_id" disabled />
        </el-form-item>
        <el-form-item label="姓名" prop="student_name">
          <el-input v-model="editStudentForm.student_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="班级" prop="class_">
          <el-input v-model="editStudentForm.class_" placeholder="请输入班级" />
        </el-form-item>
        <el-form-item label="新密码" prop="student_password">
          <el-input
            v-model="editStudentForm.student_password"
            type="password"
            placeholder="留空则不修改密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editStudentVisible = false">取消</el-button>
          <el-button type="primary" @click="updateStudent" :loading="updatingStudent"
            >确认</el-button
          >
        </div>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form
        :model="passwordForm"
        :rules="passwordRules"
        ref="passwordFormRef"
        label-width="100px"
      >
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
          <el-button type="primary" @click="changePassword">确认</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 解析数据预览对话框 -->
    <el-dialog
      v-model="showParsedData"
      title="批量导入预览"
      width="90%"
      :close-on-click-modal="false"
    >
      <div class="parsed-data-container">
        <div class="parsed-header">
          <span>共解析到 {{ parsedStudents.length }} 条学生记录，请检查并修改数据后确认导入</span>
        </div>

        <el-table :data="parsedStudents" border stripe max-height="400" class="parsed-table">
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column label="学号" width="120">
            <template #default="scope">
              <el-input
                v-if="scope.row._editing"
                v-model="scope.row.student_id"
                size="small"
                :class="{
                  'error-input': !scope.row._valid && scope.row._errors.includes('学号不能为空'),
                }"
              />
              <span
                v-else
                :class="{
                  'error-text': !scope.row._valid && scope.row._errors.includes('学号不能为空'),
                }"
              >
                {{ scope.row.student_id }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="姓名" width="100">
            <template #default="scope">
              <el-input
                v-if="scope.row._editing"
                v-model="scope.row.student_name"
                size="small"
                :class="{
                  'error-input': !scope.row._valid && scope.row._errors.includes('姓名不能为空'),
                }"
              />
              <span
                v-else
                :class="{
                  'error-text': !scope.row._valid && scope.row._errors.includes('姓名不能为空'),
                }"
              >
                {{ scope.row.student_name }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="班级" width="150">
            <template #default="scope">
              <el-input
                v-if="scope.row._editing"
                v-model="scope.row.class_"
                size="small"
                :class="{
                  'error-input': !scope.row._valid && scope.row._errors.includes('班级不能为空'),
                }"
              />
              <span
                v-else
                :class="{
                  'error-text': !scope.row._valid && scope.row._errors.includes('班级不能为空'),
                }"
              >
                {{ scope.row.class_ }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-select
                v-if="scope.row._editing"
                v-model="scope.row.status"
                size="small"
                :class="{
                  'error-input': !scope.row._valid && scope.row._errors.includes('状态必须为0或1'),
                }"
              >
                <el-option label="正常" :value="0" />
                <el-option label="重修" :value="1" />
              </el-select>
              <el-tag v-else :type="scope.row.status === 0 ? 'success' : 'warning'">
                {{ scope.row.status === 0 ? '正常' : '重修' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="课程ID" width="100">
            <template #default="scope">
              <el-input
                v-if="scope.row._editing"
                v-model="scope.row.course_id"
                size="small"
                type="number"
                :class="{
                  'error-input': !scope.row._valid && scope.row._errors.includes('课程ID不能为空'),
                }"
              />
              <span
                v-else
                :class="{
                  'error-text': !scope.row._valid && scope.row._errors.includes('课程ID不能为空'),
                }"
              >
                {{ scope.row.course_id }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="scope">
              <el-tag v-if="scope.row._valid" type="success">有效</el-tag>
              <el-tooltip v-else :content="scope.row._errors.join(', ')" placement="top">
                <el-tag type="danger">错误</el-tag>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <div v-if="scope.row._editing">
                <el-button type="primary" size="small" @click="saveParsedStudent(scope.$index)">
                  <el-icon><Check /></el-icon>
                </el-button>
                <el-button size="small" @click="cancelEditParsedStudent(scope.$index)">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <div v-else>
                <el-button type="warning" size="small" @click="editParsedStudent(scope.$index)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button type="danger" size="small" @click="removeParsedStudent(scope.$index)">
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelBatchImport">取消</el-button>
          <el-button type="primary" @click="confirmBatchImport" :loading="batchImporting">
            确认导入 ({{ parsedStudents.filter((s) => s._valid).length }} 条有效记录)
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  ArrowLeft,
  Calendar,
  Plus,
  Upload,
  Download,
  User,
  Search,
  Edit,
  Check,
  Close,
} from '@element-plus/icons-vue'
import axios from '@/utils/axios'
import AdminService from '@/utils/adminService'
import * as XLSX from 'xlsx'

const router = useRouter()

// 响应式数据
const teacherInfo = ref<any>({})
const semesterList = ref<any[]>([])
const selectedSemester = ref<number | null>(null)
const selectedSemesterInfo = ref<any>(null)
const studentList = ref<any[]>([])
const searchKeyword = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 加载状态
const studentsLoading = ref(false)
const addingStudent = ref(false)
const importing = ref(false)

// 表单数据
const studentForm = ref({
  student_id: '',
  student_name: '',
  class_: '',
  status: 0,
  course_id: '',
})

// 表单引用
const studentFormRef = ref()
const editStudentFormRef = ref()

// 文件上传
const uploadRef = ref()
const uploadFile = ref<File | null>(null)

// Excel解析相关
const parsedStudents = ref<any[]>([])
const showParsedData = ref(false)
const batchImporting = ref(false)

// 对话框相关
const passwordDialogVisible = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const passwordFormRef = ref()

// 学生详情相关
const studentDetailVisible = ref(false)
const studentDetailLoading = ref(false)
const studentDetail = ref({
  id: '',
  student_id: '',
  student_name: '',
  class_: '',
  course_id: '',
})

// 编辑学生相关
const editStudentVisible = ref(false)
const updatingStudent = ref(false)
const editStudentForm = ref({
  student_id: '',
  student_name: '',
  class_: '',
  student_password: '',
})

// 表单验证规则
const passwordRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const studentFormRules = {
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  student_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  class_: [{ required: true, message: '请输入班级', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  course_id: [{ required: true, message: '请输入课程ID', trigger: 'blur' }],
}

const editStudentRules = {
  student_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  class_: [{ required: true, message: '请输入班级', trigger: 'blur' }],
}

// 生命周期
onMounted(() => {
  fetchTeacherInfo()
  fetchSemesters()
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
  }
}

// 获取学期列表
const fetchSemesters = async () => {
  try {
    const response = await axios.get('/public/semesters')
    if (response.data && response.data.semesters) {
      semesterList.value = response.data.semesters
    }
  } catch (error) {
    console.error('获取学期列表失败:', error)
    ElMessage.error('获取学期列表失败')
  }
}

// 选择学期
const selectSemester = (semester: any) => {
  selectedSemester.value = semester.semester_id
  selectedSemesterInfo.value = semester
  currentPage.value = 1
  fetchStudents()
}

// 获取学生列表
const fetchStudents = async () => {
  if (!selectedSemester.value) return

  studentsLoading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      semester_id: selectedSemester.value,
      search: searchKeyword.value,
    }

    const response = await axios.get('/teacher/students', { params })
    if (response.data) {
      studentList.value = response.data.students || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    console.error('获取学生列表失败:', error)
    ElMessage.error('获取学生列表失败')
  } finally {
    studentsLoading.value = false
  }
}

// 添加学生
const addStudent = async () => {
  if (!studentFormRef.value) return

  try {
    await studentFormRef.value.validate()

    addingStudent.value = true
    // 直接发送学生数组
    const response = await axios.post('/teacher/students/addcourse', [studentForm.value])
    if (response.data && response.data.code === 200) {
      ElMessage.success(response.data.msg || '添加学生成功')
      resetStudentForm()
      fetchStudents()
    } else {
      ElMessage.error(response.data?.msg || '添加学生失败')
    }
  } catch (error) {
    console.error('添加学生失败:', error)
    if (error !== 'validation failed') {
      ElMessage.error('添加学生失败')
    }
  } finally {
    addingStudent.value = false
  }
}

// 重置学生表单
const resetStudentForm = () => {
  studentForm.value = {
    student_id: '',
    student_name: '',
    class_: '',
    status: 0,
    course_id: '',
  }
  if (studentFormRef.value) {
    studentFormRef.value.clearValidate()
  }
}

// 文件上传处理
const handleFileChange = (file: any) => {
  uploadFile.value = file.raw
  parseExcelFile(file.raw)
}

// 解析Excel文件
const parseExcelFile = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[sheetName]
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })

      // 解析数据，跳过表头
      const students: any[] = []
      for (let i = 1; i < jsonData.length; i++) {
        const row = jsonData[i] as any[]
        if (row.length >= 5 && row[0]) {
          // 确保有足够的列且学号不为空
          students.push({
            student_id: String(row[0] || ''),
            student_name: String(row[1] || ''),
            class_: String(row[2] || ''),
            status: Number(row[3]) || 0,
            course_id: Number(row[4]) || selectedSemester.value || 0,
            _editing: false,
            _valid: true,
            _errors: [],
          })
        }
      }

      if (students.length === 0) {
        ElMessage.warning('Excel文件中没有找到有效的学生数据')
        return
      }

      parsedStudents.value = students
      showParsedData.value = true
      ElMessage.success(`成功解析 ${students.length} 条学生记录`)
    } catch (error) {
      console.error('解析Excel文件失败:', error)
      ElMessage.error('解析Excel文件失败，请检查文件格式')
    }
  }
  reader.readAsArrayBuffer(file)
}

// 批量导入学生
const importStudents = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要上传的Excel文件')
    return
  }

  // 如果还没有解析数据，先解析
  if (parsedStudents.value.length === 0) {
    parseExcelFile(uploadFile.value)
    return
  }

  // 显示解析后的数据供用户确认
  showParsedData.value = true
}

// 确认批量导入
const confirmBatchImport = async () => {
  if (parsedStudents.value.length === 0) {
    ElMessage.warning('没有可导入的数据')
    return
  }

  // 验证数据
  const validStudents = parsedStudents.value.filter((student) => {
    student._errors = []
    student._valid = true

    if (!student.student_id) {
      student._errors.push('学号不能为空')
      student._valid = false
    }
    if (!student.student_name) {
      student._errors.push('姓名不能为空')
      student._valid = false
    }
    if (!student.class_) {
      student._errors.push('班级不能为空')
      student._valid = false
    }
    if (![0, 1].includes(student.status)) {
      student._errors.push('状态必须为0或1')
      student._valid = false
    }
    if (!student.course_id) {
      student._errors.push('课程ID不能为空')
      student._valid = false
    }

    return student._valid
  })

  if (validStudents.length === 0) {
    ElMessage.error('没有有效的学生数据可导入')
    return
  }

  if (validStudents.length < parsedStudents.value.length) {
    const invalidCount = parsedStudents.value.length - validStudents.length
    const result = await ElMessageBox.confirm(
      `有 ${invalidCount} 条记录存在错误，是否只导入有效的 ${validStudents.length} 条记录？`,
      '数据验证',
      {
        confirmButtonText: '确定导入',
        cancelButtonText: '取消',
        type: 'warning',
      },
    ).catch(() => false)

    if (!result) return
  }

  batchImporting.value = true
  try {
    // 直接发送学生数组
    const studentsData = validStudents.map((student) => ({
      student_id: student.student_id,
      student_name: student.student_name,
      class_: student.class_,
      status: student.status,
      course_id: student.course_id,
    }))

    const response = await axios.post('/teacher/students/addcourse', studentsData)

    // 根据后端返回的状态码处理不同情况
    if (response.data) {
      const { code, msg } = response.data

      if (code === 200) {
        // 全部成功 (code: 200)
        ElMessage.success(msg || '批量导入成功')

        // 清空数据并刷新列表
        uploadRef.value?.clearFiles()
        uploadFile.value = null
        parsedStudents.value = []
        showParsedData.value = false
        fetchStudents()
      } else if (code === 206) {
        // 部分成功 (code: 206)
        const detailMessage = msg || '部分导入成功'

        await ElMessageBox.alert(detailMessage, '导入结果详情', {
          confirmButtonText: '确定',
          type: 'warning',
          dangerouslyUseHTMLString: false,
        })

        // 清空数据并刷新列表
        uploadRef.value?.clearFiles()
        uploadFile.value = null
        parsedStudents.value = []
        showParsedData.value = false
        fetchStudents()
      } else {
        // 其他错误情况
        ElMessage.error(msg || '批量导入失败')
      }
    } else {
      ElMessage.error('批量导入失败：服务器响应异常')
    }
  } catch (error: any) {
    console.error('批量导入失败:', error)

    // 处理HTTP错误响应
    if (error.response?.data) {
      const { code, msg } = error.response.data

      if (code === 400) {
        // 全部失败 (code: 400)
        const detailMessage = msg || '批量导入失败'

        await ElMessageBox.alert(detailMessage, '导入失败详情', {
          confirmButtonText: '确定',
          type: 'error',
          dangerouslyUseHTMLString: false,
        })
      } else if (error.response.data.detail) {
        // 其他详细错误信息
        ElMessage.error(error.response.data.detail)
      } else {
        // 使用返回的消息或默认消息
        ElMessage.error(msg || '批量导入失败')
      }
    } else {
      ElMessage.error('批量导入失败：网络错误或服务器无响应')
    }
  } finally {
    batchImporting.value = false
  }
}

// 取消批量导入
const cancelBatchImport = () => {
  showParsedData.value = false
  parsedStudents.value = []
  uploadRef.value?.clearFiles()
  uploadFile.value = null
}

// 编辑解析后的学生数据
const editParsedStudent = (index: number) => {
  parsedStudents.value[index]._editing = true
}

// 保存编辑的学生数据
const saveParsedStudent = (index: number) => {
  const student = parsedStudents.value[index]
  // 重新验证
  student._errors = []
  student._valid = true

  if (!student.student_id) {
    student._errors.push('学号不能为空')
    student._valid = false
  }
  if (!student.student_name) {
    student._errors.push('姓名不能为空')
    student._valid = false
  }
  if (!student.class_) {
    student._errors.push('班级不能为空')
    student._valid = false
  }
  if (![0, 1].includes(student.status)) {
    student._errors.push('状态必须为0或1')
    student._valid = false
  }
  if (!student.course_id) {
    student._errors.push('课程ID不能为空')
    student._valid = false
  }

  student._editing = false
}

// 取消编辑学生数据
const cancelEditParsedStudent = (index: number) => {
  parsedStudents.value[index]._editing = false
}

// 删除解析后的学生数据
const removeParsedStudent = (index: number) => {
  parsedStudents.value.splice(index, 1)
  if (parsedStudents.value.length === 0) {
    showParsedData.value = false
  }
}

// 下载模板
const downloadTemplate = () => {
  // 创建Excel模板
  const wb = XLSX.utils.book_new()
  const wsData = [
    ['student_id', 'student_name', 'class_', 'status', 'course_id'],
    ['202322511772', '张三零', '23级1班', 0, 1],
    ['202346511822', '李四飒', '23级1班', 1, 1],
  ]
  const ws = XLSX.utils.aoa_to_sheet(wsData)

  // 设置列宽
  ws['!cols'] = [
    { wch: 15 }, // student_id
    { wch: 12 }, // student_name
    { wch: 20 }, // class_
    { wch: 8 }, // status
    { wch: 10 }, // course_id
  ]

  XLSX.utils.book_append_sheet(wb, ws, '学生信息')
  XLSX.writeFile(wb, '学生导入模板.xlsx')
}

// 查看学生详情
const viewStudentDetail = async (student: any) => {
  studentDetailVisible.value = true
  studentDetailLoading.value = true

  try {
    const response = await axios.get(`/teacher/students/${student.student_id}`)
    if (response.data) {
      studentDetail.value = response.data
    }
  } catch (error) {
    console.error('获取学生详情失败:', error)
    ElMessage.error('获取学生详情失败')
  } finally {
    studentDetailLoading.value = false
  }
}

// 编辑学生
const editStudent = (student: any) => {
  editStudentForm.value = {
    student_id: student.student_id,
    student_name: student.student_name,
    class_: student.class_,
    student_password: '',
  }
  editStudentVisible.value = true
}

// 更新学生信息
const updateStudent = async () => {
  if (!editStudentFormRef.value) return

  try {
    await editStudentFormRef.value.validate()

    updatingStudent.value = true
    const updateData: any = {
      student_name: editStudentForm.value.student_name,
      class_: editStudentForm.value.class_,
    }

    // 只有在输入了新密码时才包含密码字段
    if (editStudentForm.value.student_password) {
      updateData.student_password = editStudentForm.value.student_password
    }

    const response = await axios.put(
      `/teacher/students/${editStudentForm.value.student_id}`,
      updateData,
    )
    if (response.data) {
      ElMessage.success('更新学生信息成功')
      editStudentVisible.value = false
      fetchStudents()
    }
  } catch (error) {
    console.error('更新学生信息失败:', error)
    if (error !== 'validation failed') {
      ElMessage.error('更新学生信息失败')
    }
  } finally {
    updatingStudent.value = false
  }
}

// 删除学生
const deleteStudent = async (student: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学生 ${student.student_name}(${student.student_id}) 吗？\n\n注意：删除学生将同时删除其相关的选课记录等信息，此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false,
      },
    )

    // 调用adminService删除学生
    const success = await AdminService.deleteStudent(student.student_id)

    if (success) {
      // 重新获取学生列表
      fetchStudents()
    }
  } catch (error: any) {
    // 如果是用户取消操作，不显示错误信息
    if (error === 'cancel') {
      return
    }

    console.error('删除学生操作被取消或失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchStudents()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchStudents()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchStudents()
}

// 导航函数
const goBack = () => {
  router.go(-1)
}

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
  router.push('/teacher/problem')
}

const goToStudentInfo = () => {
  // 当前页面，不需要跳转
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

    const response = await axios.put('/teacher/change-password', {
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword,
    })

    if (response.data && response.data.code === 200) {
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: '',
      }
    } else {
      ElMessage.error(response.data?.msg || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  }
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.teacher-layout {
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

.nav-btn.active {
  color: #409eff;
  font-weight: 600;
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
  cursor: pointer;
  color: #ffffff;
  font-size: 16px;
  display: flex;
}

/* 解析数据预览样式 */
.parsed-data-container {
  max-height: 500px;
  overflow-y: auto;
}

.parsed-header {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-weight: 500;
  color: #606266;
}

.parsed-table {
  width: 100%;
}

.error-input {
  border-color: #f56c6c !important;
}

.error-text {
  color: #f56c6c;
  font-weight: 500;
}

.parsed-table .el-table__row.error-row {
  background-color: #fef0f0;
}

.parsed-table .el-input {
  width: 100%;
}

.parsed-table .el-select {
  width: 100%;
}

.username-dropdown:hover {
  color: #cce5ff;
}

/* 主容器 */
.main-container {
  flex: 1;
  overflow: hidden;
}

.main-content {
  padding: 0;
  height: 100%;
  overflow: hidden;
}

/* 学生信息包装器 */
.student-wrapper {
  display: grid;
  grid-template-columns: 300px;
  height: 100%;
  gap: 0;
}

.student-wrapper.has-selection {
  grid-template-columns: 300px 280px 1fr;
}

/* 面板样式 */
.left-panel,
.middle-panel,
.right-panel {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
  height: 100%;
}

.right-panel {
  border-right: none;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  color: #606266;
  font-size: 14px;
  margin-right: 16px;
}

.back-btn:hover {
  color: #409eff;
}

/* 学期列表 */
.semester-list {
  padding: 16px;
}

.semester-item {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #ffffff;
  position: relative;
}

.semester-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.semester-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.semester-item.current {
  border-color: #67c23a;
}

.semester-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  font-size: 16px;
}

.semester-date {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.current-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #67c23a;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

/* 中间面板 - 添加选课记录 */
.middle-panel {
  padding: 20px;
}

.import-section {
  margin-bottom: 32px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.import-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.import-btn,
.template-btn {
  align-self: flex-start;
}

.template-btn {
  margin-left: 8px;
}

/* 右侧面板 - 学生列表 */
.right-panel {
  display: flex;
  flex-direction: column;
}

.search-box {
  width: 200px;
}

.table-container {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.student-table {
  flex: 1;
  margin-bottom: 16px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 16px 0;
  border-top: 1px solid #e4e7ed;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .student-wrapper.has-selection {
    grid-template-columns: 250px 220px 1fr;
  }
}

@media (max-width: 768px) {
  .student-wrapper {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .student-wrapper.has-selection {
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

  .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }
}
</style>
