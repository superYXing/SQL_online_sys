<template>
  <div class="admin-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToSemester">SQL在线实践平台</span>
        <div class="header-buttons">
          <el-button type="text" class="nav-btn active">学期</el-button>
          <el-button type="text" @click="goToTeacher" class="nav-btn">教师</el-button>
        </div>
      </div>
      <div class="header-right">
        <div class="admin-status">
          <div class="status-item">
            <span class="status-label">管理员:</span>
            <el-dropdown @command="handleCommand">
              <span class="username-dropdown">
                admin001
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
          <div class="status-item">
            <span class="status-label">当前学期:</span>
            <span class="status-value">{{ currentSemesterComputed?.semester_name || '暂无' }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">系统状态:</span>
            <span class="status-value online">在线</span>
          </div>
        </div>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside class="sidebar" width="200px">
        <el-menu
          :default-active="activeSection"
          class="sidebar-menu"
        >
          <el-menu-item index="create" @click="switchSection('create')">
            <el-icon><Plus /></el-icon>
            <span>创建学期</span>
          </el-menu-item>
          <el-menu-item index="upcoming" @click="switchSection('upcoming')">
            <el-icon><Calendar /></el-icon>
            <span>未开始的学期</span>
          </el-menu-item>
          <el-menu-item index="current" @click="switchSection('current')">
            <el-icon><Clock /></el-icon>
            <span>当前学期</span>
          </el-menu-item>
          <el-menu-item index="ended" @click="switchSection('ended')">
            <el-icon><Lock /></el-icon>
            <span>已结束的学期</span>
          </el-menu-item>
        </el-menu>

        <!-- 动态显示不同类型的学期 -->
        <div class="semester-section" v-if="activeSection === 'upcoming'">
          <h3>未开始的学期</h3>
          <div v-if="upcomingSemesters.length > 0">
            <div v-for="semester in upcomingSemesters" :key="semester.semester_id" class="semester-item">
              <div class="semester-info">
                <span class="semester-name">{{ semester.semester_name }}</span>
                <div class="semester-actions">
                  <el-icon class="action-icon delete-icon" @click="deleteSemester(semester.semester_id)"><Delete /></el-icon>
                </div>
              </div>
              <div class="semester-dates">
                <div class="date-item">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(semester.begin_date) }}</span>
                </div>
                <div class="date-item">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(semester.end_date) }}</span>
                </div>
              </div>
            </div>
          </div>
          <EmptyState v-else title="暂无未开始的学期" description="当前没有计划中的学期，您可以创建新的学期。">
            <template #actions>
              <el-button type="primary" @click="switchSection('create')">
                <el-icon><Plus /></el-icon>
                创建学期
              </el-button>
            </template>
          </EmptyState>
        </div>

        <div class="semester-section" v-if="activeSection === 'current'">
           <h3>当前学期</h3>
           <div v-if="currentSemesterComputed" class="semester-item">
             <div class="semester-info">
               <span class="semester-name">{{ currentSemesterComputed.semester_name }}</span>
               <div class="semester-actions">
                 <el-icon class="action-icon delete-icon" @click="deleteSemester(currentSemesterComputed.semester_id)"><Delete /></el-icon>
               </div>
             </div>
             <div class="semester-dates">
               <div class="date-item">
                 <el-icon><Calendar /></el-icon>
                 <span>{{ formatDate(currentSemesterComputed.begin_date) }}</span>
               </div>
               <div class="date-item">
                 <el-icon><Calendar /></el-icon>
                 <span>{{ formatDate(currentSemesterComputed.end_date) }}</span>
               </div>
             </div>
           </div>
           <div v-else class="no-semester">
             <span>暂无当前学期</span>
           </div>
         </div>

        <div class="semester-section" v-if="activeSection === 'ended'">
          <h3>已结束的学期</h3>
          <div v-if="endedSemesters.length > 0">
            <div v-for="semester in endedSemesters" :key="semester.semester_id" class="semester-item">
              <div class="semester-info">
                <span class="semester-name">{{ semester.semester_name }}</span>
                <div class="semester-actions">
                  <el-icon class="action-icon delete-icon" @click="deleteSemester(semester.semester_id)"><Delete /></el-icon>
                </div>
              </div>
              <div class="semester-dates">
                <div class="date-item">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(semester.begin_date) }}</span>
                </div>
                <div class="date-item">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(semester.end_date) }}</span>
                </div>
              </div>
            </div>
          </div>
          <EmptyState v-else title="暂无已结束的学期" description="当前没有已结束的学期记录。" />
        </div>

        <div class="semester-section" v-if="activeSection === 'create'">
          <h3>创建学期</h3>
          <div class="create-semester-form">
            <el-button type="primary" @click="showAddSemesterDialog" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Plus /></el-icon>
              <span>添加新学期</span>
            </el-button>
            <p class="create-tip">点击上方按钮创建新的学期</p>
          </div>
        </div>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <!-- 当前学期信息 -->
        <div v-if="currentSemesterComputed" class="current-semester-header">
          <h2>{{ currentSemesterComputed.semester_name }}</h2>
          <div class="semester-actions">
            <el-icon class="action-icon delete-icon" @click="deleteSemester(currentSemesterComputed.semester_id)"><Delete /></el-icon>
          </div>
        </div>

        <!-- 日历组件 -->
        <div class="calendar-container">
          <el-calendar v-model="calendarValue" class="semester-calendar">
            <template #header="{ date }">
              <div class="calendar-header">
                <el-button-group>
                  <el-button @click="previousMonth">
                    <el-icon><ArrowLeft /></el-icon>
                  </el-button>
                  <el-button @click="nextMonth">
                    <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </el-button-group>
                <span class="calendar-title">{{ formatCalendarTitle(new Date(date)) }}</span>
              </div>
            </template>
          </el-calendar>
        </div>

        <!-- 学期时间设置 -->
        <div class="semester-time-settings">
          <div class="time-setting-item">
            <label>起始时间</label>
            <el-date-picker
              v-model="semesterStartDate"
              type="date"
              placeholder="选择起始日期"
              format="YYYY年MM月DD日"
              value-format="YYYY-MM-DD"
            />
          </div>
          <div class="time-setting-item">
            <label>结束时间</label>
            <el-date-picker
              v-model="semesterEndDate"
              type="date"
              placeholder="选择结束日期"
              format="YYYY年MM月DD日"
              value-format="YYYY-MM-DD"
            />
          </div>
          <div class="time-setting-item">
            <el-button type="primary" @click="updateSemesterTime">保存修改</el-button>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- 添加学期对话框 -->
    <el-dialog
      v-model="addSemesterDialogVisible"
      title="添加学期"
      width="500px"
      :before-close="handleCloseAddDialog"
    >
      <el-form
        ref="addSemesterFormRef"
        :model="addSemesterForm"
        :rules="addSemesterRules"
        label-width="100px"
      >
        <el-form-item label="学期名称" prop="semester_name">
          <el-input
            v-model="addSemesterForm.semester_name"
            placeholder="请输入学期名称，如：2025-2026学年第一学期"
          />
        </el-form-item>
        <el-form-item label="开始日期" prop="begin_date">
          <el-date-picker
            v-model="addSemesterForm.begin_date"
            type="date"
            placeholder="选择开始日期"
            format="YYYY年MM月DD日"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="addSemesterForm.end_date"
            type="date"
            placeholder="选择结束日期"
            format="YYYY年MM月DD日"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addSemesterDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createSemester" :loading="createLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>

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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ElMessage, 
  ElMessageBox,
  ElHeader, 
  ElContainer, 
  ElAside, 
  ElMain,
  ElMenu,
  ElMenuItem,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElIcon,
  ElButton,
  ElButtonGroup,
  ElCalendar,
  ElDatePicker,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  type FormInstance,
  type FormRules
} from 'element-plus'
import {
  ArrowDown,
  Plus,
  Calendar,
  Clock,
  Lock,
  Delete,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'
import axios from 'axios'
import EmptyState from '@/components/EmptyState.vue'

// 路由
const router = useRouter()

// 接口数据类型定义
interface Semester {
  semester_id: number
  semester_name: string
  begin_date: string
  end_date: string
  is_current: boolean
}

interface SemesterResponse {
  semesters: Semester[]
  total: number
  current_semester: {
    semester_id: number
    semester_name: string
  }
}

// 响应式数据
const semesters = ref<Semester[]>([])

const calendarValue = ref(new Date())
const semesterStartDate = ref('')
const semesterEndDate = ref('')
const activeSection = ref('ended') // 当前显示的学期类型：'create', 'upcoming', 'current', 'ended'

// 添加学期对话框相关
const addSemesterDialogVisible = ref(false)
const addSemesterFormRef = ref<FormInstance>()
const createLoading = ref(false)
const addSemesterForm = reactive({
  semester_name: '',
  begin_date: '',
  end_date: ''
})

// 修改密码相关
const passwordDialogVisible = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordLoading = ref(false)

// 表单验证规则
const addSemesterRules: FormRules = {
  semester_name: [
    { required: true, message: '请输入学期名称', trigger: 'blur' },
    { min: 1, max: 100, message: '学期名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  begin_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ]
}

// 计算属性：未开始的学期（根据系统时间判断）
const upcomingSemesters = computed(() => {
  const now = new Date()
  const today = now.toISOString().split('T')[0] // 格式化为 YYYY-MM-DD
  
  return semesters.value.filter(semester => {
    // 如果学期开始日期晚于今天，则为未开始的学期
    return semester.begin_date > today
  })
})

// 计算属性：当前学期（根据系统时间和is_current字段判断）
const currentSemesterComputed = computed(() => {
  const now = new Date()
  const today = now.toISOString().split('T')[0] // 格式化为 YYYY-MM-DD
  
  return semesters.value.find(semester => {
    // 优先使用is_current字段，如果没有则根据日期判断
    if (semester.is_current) {
      return true
    }
    // 如果当前日期在学期开始和结束日期之间，则为当前学期
    return semester.begin_date <= today && semester.end_date >= today
  }) || null
})

// 计算属性：已结束的学期
const endedSemesters = computed(() => {
  const now = new Date()
  const today = now.toISOString().split('T')[0] // 格式化为 YYYY-MM-DD
  
  return semesters.value.filter(semester => {
    // 如果学期结束日期早于今天，则为已结束的学期
    return semester.end_date < today
  })
})

// 获取所有学期数据
const fetchSemesters = async () => {
  try {
    // 从localStorage获取JWT Token
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    // 如果有token，添加到请求头
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await axios.get<SemesterResponse>('http://localhost:8000/public/semesters', {
      headers
    })
    
    if (response.data) {
      semesters.value = response.data.semesters
      
      // 设置当前学期的时间设置
      const current = response.data.semesters.find(s => s.is_current)
      if (current) {
        semesterStartDate.value = current.begin_date
        semesterEndDate.value = current.end_date
      }
      
      console.log('学期数据加载成功:', response.data)
    }
  } catch (error: unknown) {
    console.error('获取学期数据失败:', error)
    ElMessage.error('获取学期数据失败，请检查网络连接')
    
    // 清空数据，显示无数据状态
    semesters.value = []
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

// 格式化日历标题
const formatCalendarTitle = (date: Date) => {
  return `${date.getFullYear()}年${date.getMonth() + 1}月`
}

// 日历导航
const previousMonth = () => {
  const current = new Date(calendarValue.value)
  current.setMonth(current.getMonth() - 1)
  calendarValue.value = current
}

const nextMonth = () => {
  const current = new Date(calendarValue.value)
  current.setMonth(current.getMonth() + 1)
  calendarValue.value = current
}

// 切换学期类型显示
const switchSection = (section: string) => {
  activeSection.value = section
}

// 点击logo回到学期页面
const goToSemester = () => {
  router.push('/admin/semester')
}

// 跳转到教师页面
const goToTeacher = () => {
  router.push('/admin/teacher')
}



// 显示添加学期对话框
const showAddSemesterDialog = () => {
  addSemesterDialogVisible.value = true
}

// 关闭添加学期对话框
const handleCloseAddDialog = () => {
  addSemesterDialogVisible.value = false
  // 重置表单
  if (addSemesterFormRef.value) {
    addSemesterFormRef.value.resetFields()
  }
  addSemesterForm.semester_name = ''
  addSemesterForm.begin_date = ''
  addSemesterForm.end_date = ''
}

// 创建学期
const createSemester = async () => {
  if (!addSemesterFormRef.value) return
  
  try {
    // 表单验证
    await addSemesterFormRef.value.validate()
    
    // 验证结束日期是否晚于开始日期
    if (addSemesterForm.end_date <= addSemesterForm.begin_date) {
      ElMessage.error('结束日期必须晚于开始日期')
      return
    }
    
    createLoading.value = true
    
    // 从localStorage获取JWT Token
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    // 调用创建学期接口
    const response = await axios.post('http://localhost:8000/admin/semesters', {
      semester_name: addSemesterForm.semester_name,
      begin_date: addSemesterForm.begin_date,
      end_date: addSemesterForm.end_date
    }, { headers })
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '学期创建成功')
      handleCloseAddDialog()
      // 重新获取学期数据
      await fetchSemesters()
    } else {
      ElMessage.error(response.data.message || '学期创建失败')
    }
  } catch (error: unknown) {
    console.error('创建学期失败:', error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: unknown; message?: string } } }
      if (axiosError.response?.data?.detail) {
        // 返回后端的detail字段
        const detail = axiosError.response.data.detail
        if (Array.isArray(detail) && detail.length > 0) {
          ElMessage.error(detail[0].msg || '创建学期失败')
        } else if (typeof detail === 'string') {
          ElMessage.error(detail)
        } else {
          ElMessage.error('创建学期失败')
        }
      } else if (axiosError.response?.data?.message) {
        ElMessage.error(axiosError.response.data.message)
      } else {
        ElMessage.error('创建学期失败，请检查网络连接')
      }
    } else {
      ElMessage.error('创建学期失败，请检查网络连接')
    }
  } finally {
    createLoading.value = false
  }
}

// 删除学期
const deleteSemester = async (semesterId: number) => {
  try {
    // 确认删除
    const confirmResult = await ElMessageBox.confirm(
      '确定要删除这个学期吗？如果有关联课程则无法删除。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (confirmResult !== 'confirm') {
      return
    }
    
    // 从localStorage获取JWT Token
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    // 调用删除学期接口
    const response = await axios.delete(`http://localhost:8000/admin/semesters/${semesterId}`, {
      headers
    })
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '学期删除成功')
      // 重新获取学期数据
      await fetchSemesters()
    } else {
      ElMessage.error(response.data.message || '学期删除失败')
    }
  } catch (error: unknown) {
    console.error('删除学期失败:', error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: unknown; message?: string } } }
      if (axiosError.response?.data?.detail) {
        // 返回后端的detail字段
        const detail = axiosError.response.data.detail
        if (Array.isArray(detail) && detail.length > 0) {
          ElMessage.error(detail[0].msg || '删除学期失败')
        } else if (typeof detail === 'string') {
          ElMessage.error(detail)
        } else {
          ElMessage.error('删除学期失败')
        }
      } else if (axiosError.response?.data?.message) {
        ElMessage.error(axiosError.response.data.message)
      } else {
        ElMessage.error('删除学期失败，请检查网络连接')
      }
    } else {
      ElMessage.error('删除学期失败，请检查网络连接')
    }
  }
}

// 修改学期时间
const updateSemesterTime = async () => {
  if (!currentSemesterComputed.value) {
    ElMessage.error('请先选择要修改的学期')
    return
  }
  
  if (!semesterStartDate.value || !semesterEndDate.value) {
    ElMessage.error('请选择开始日期和结束日期')
    return
  }
  
  if (semesterEndDate.value <= semesterStartDate.value) {
    ElMessage.error('结束日期必须晚于开始日期')
    return
  }
  
  try {
    // 从localStorage获取JWT Token
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    // 调用修改学期时间接口
    const response = await axios.put('http://localhost:8000/admin/semester/time', {
      semester_id: currentSemesterComputed.value.semester_id,
      begin_date: semesterStartDate.value,
      end_date: semesterEndDate.value
    }, { headers })
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '学期时间修改成功')
      // 重新获取学期数据
      await fetchSemesters()
    } else {
      ElMessage.error(response.data.message || '学期时间修改失败')
    }
  } catch (error: unknown) {
     console.error('修改学期时间失败:', error)
     if (error && typeof error === 'object' && 'response' in error) {
       const axiosError = error as { response?: { data?: { message?: string } } }
       if (axiosError.response?.data?.message) {
         ElMessage.error(axiosError.response.data.message)
       } else {
         ElMessage.error('修改学期时间失败，请检查网络连接')
       }
     } else {
       ElMessage.error('修改学期时间失败，请检查网络连接')
     }
  }
}

// 密码验证规则
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
    {
      validator: (rule: any, value: any, callback: any) => {
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

// 下拉菜单处理
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
    const valid = await passwordFormRef.value.validate()
    if (!valid) return
    
    passwordLoading.value = true
    
    // 从localStorage获取JWT Token
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await axios.put('http://localhost:8000/admin/change-password', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    }, { headers })
    
    if (response.data.success) {
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
      resetPasswordForm()
    } else {
      ElMessage.error(response.data.message || '密码修改失败')
    }
  } catch (error: unknown) {
    console.error('修改密码失败:', error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { message?: string } } }
      if (axiosError.response?.data?.message) {
        ElMessage.error(axiosError.response.data.message)
      } else {
        ElMessage.error('密码修改失败，请检查网络连接')
      }
    } else {
      ElMessage.error('密码修改失败，请检查网络连接')
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
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '确认退出', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 清除本地存储的token
    localStorage.removeItem('token')
    localStorage.removeItem('user_type')
    localStorage.removeItem('username')
    
    // 跳转到登录页面
    window.location.href = '/login'
  } catch {
    // 用户取消退出
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchSemesters()
})
</script>

<style scoped>
.admin-layout {
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

.logo {
  font-size: 18px;
  font-weight: bold;
  margin-right: 30px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.8;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 20px;
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
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-status {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.status-label {
  color: rgba(255, 255, 255, 0.8);
  font-weight: normal;
}

.status-value {
  color: white;
  font-weight: 500;
}

.status-value.online {
  color: #52c41a;
  font-weight: 600;
}

.username {
  font-size: 14px;
}

.teacher-label {
  font-size: 14px;
  color: white;
  margin-left: 10px;
}

.el-dropdown-link {
  color: white;
  cursor: pointer;
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

/* 侧边栏 */
.sidebar {
  background-color: #f5f5f5;
  border-right: 1px solid #e6e6e6;
  overflow-y: auto;
}

.sidebar-menu {
  border: none;
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #e6f7ff;
  color: #1890ff;
}

.semester-section {
  padding: 20px 16px;
}

.semester-section h3 {
  font-size: 14px;
  color: #666;
  margin: 0 0 15px 0;
  font-weight: normal;
}

.semester-item {
  margin-bottom: 20px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e6e6e6;
}

.semester-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.semester-name {
  font-size: 14px;
  font-weight: 500;
}

.semester-actions {
  display: flex;
  gap: 8px;
}

.action-icon {
  font-size: 16px;
  color: #666;
  cursor: pointer;
}

.action-icon:hover {
  color: #1890ff;
}

.delete-icon:hover {
  color: #ff4d4f;
}

.semester-dates {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.date-item .el-icon {
  font-size: 12px;
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

.current-semester-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e6e6e6;
}

.current-semester-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

/* 日历组件 */
.calendar-container {
  margin-bottom: 30px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.calendar-title {
  font-size: 16px;
  font-weight: 500;
}

.semester-calendar {
  border: 1px solid #e6e6e6;
  border-radius: 6px;
}

.semester-calendar :deep(.el-calendar__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #e6e6e6;
}

.semester-calendar :deep(.el-calendar__body) {
  padding: 15px;
}

.semester-calendar :deep(.el-calendar-table .el-calendar-day) {
  height: 60px;
  padding: 8px;
}

.semester-calendar :deep(.el-calendar-table thead th) {
  padding: 10px 0;
  background-color: #fafafa;
  border-bottom: 1px solid #e6e6e6;
}

/* 学期时间设置 */
.semester-time-settings {
  display: flex;
  gap: 30px;
  align-items: center;
}

.time-setting-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-setting-item label {
  font-size: 14px;
  color: #333;
}

/* 创建学期表单样式 */
.create-semester-form {
  padding: 20px 0;
  text-align: center;
}

.create-tip {
  font-size: 12px;
  color: #666;
  margin: 0;
  line-height: 1.4;
}

/* 无学期提示样式 */
.no-semester {
  padding: 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>