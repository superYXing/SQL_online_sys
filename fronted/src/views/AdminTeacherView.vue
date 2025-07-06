<template>
  <div class="admin-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <div class="logo" @click="goToSemester">SQL在线实践平台</div>
        <div class="header-buttons">
          <el-button type="text" @click="goToSemester" class="nav-btn">学期</el-button>
          <el-button type="text" class="nav-btn active">教师</el-button>
        </div>
      </div>
      <div class="header-right">
        <span class="username">admin001</span>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 主内容区 -->
      <el-main class="main-content">
        <!-- 页面标题和操作按钮 -->
        <div class="page-header">
          <h2>教师管理</h2>
          <el-button type="primary" @click="showAddTeacherDialog">
            <el-icon><Plus /></el-icon>
            添加教师
          </el-button>
        </div>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索教师ID或姓名"
            style="width: 300px; margin-right: 10px;"
            clearable
            @keyup.enter="searchTeachers"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="searchTeachers">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </div>

        <!-- 教师列表表格 -->
        <div class="table-container">
          <el-table
            :data="teachers"
            v-loading="loading"
            style="width: 100%"
            stripe
            border
          >
            <el-table-column prop="teacher_id" label="教师工号" width="150" />
            <el-table-column prop="teacher_name" label="教师姓名" width="200" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="editTeacher(row)"
                >
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteTeacher(row.teacher_id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页组件 -->
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
      </el-main>
    </el-container>

    <!-- 添加/编辑教师对话框 -->
    <el-dialog
      v-model="teacherDialogVisible"
      :title="isEdit ? '编辑教师' : '添加教师'"
      width="500px"
      :before-close="handleCloseDialog"
    >
      <el-form
        ref="teacherFormRef"
        :model="teacherForm"
        :rules="teacherRules"
        label-width="100px"
      >
        <el-form-item label="教师工号" prop="teacher_id">
          <el-input
            v-model="teacherForm.teacher_id"
            placeholder="请输入教师工号，如：T001"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="教师姓名" prop="teacher_name">
          <el-input
            v-model="teacherForm.teacher_name"
            placeholder="请输入教师姓名"
          />
        </el-form-item>
        <el-form-item label="登录密码" prop="teacher_password">
          <el-input
            v-model="teacherForm.teacher_password"
            type="password"
            placeholder="请输入登录密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="teacherDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTeacher" :loading="submitLoading">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ElMessage,
  ElMessageBox,
  ElHeader,
  ElContainer,
  ElMain,

  ElIcon,
  ElButton,
  ElInput,
  ElTable,
  ElTableColumn,
  ElPagination,
  ElDialog,
  ElForm,
  ElFormItem,
  type FormInstance,
  type FormRules
} from 'element-plus'
import {
  Plus,
  Search,
  Refresh
} from '@element-plus/icons-vue'
import axios from '@/utils/axios'

// 路由
const router = useRouter()

// 接口数据类型定义
interface Teacher {
  id: number
  teacher_id: string
  teacher_name: string
}

interface TeacherResponse {
  teachers: Teacher[]
  total: number
  page: number
  limit: number
}

// 响应式数据
const teachers = ref<Teacher[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框相关
const teacherDialogVisible = ref(false)
const teacherFormRef = ref<FormInstance>()
const submitLoading = ref(false)
const isEdit = ref(false)
const editingTeacherId = ref('')

const teacherForm = reactive({
  teacher_id: '',
  teacher_name: '',
  teacher_password: ''
})

// 密码验证函数
const validatePassword = (rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请输入登录密码'))
  } else if (value.length < 6 || value.length > 50) {
    callback(new Error('密码长度必须在 6 到 50 个字符之间'))
  } else {
    callback()
  }
}

// 表单验证规则
const teacherRules: FormRules = {
  teacher_id: [
    { required: true, message: '请输入教师工号', trigger: 'blur' },
    { min: 1, max: 50, message: '教师工号长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  teacher_name: [
    { required: true, message: '请输入教师姓名', trigger: 'blur' },
    { min: 1, max: 100, message: '教师姓名长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  teacher_password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ]
}

// 获取教师列表
const fetchTeachers = async () => {
  try {
    loading.value = true
    
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    
    const response = await axios.get<TeacherResponse>('/admin/teachers', {
      params
    })
    
    if (response.data) {
      teachers.value = response.data.teachers
      total.value = response.data.total
      console.log('教师数据加载成功:', response.data)
    }
  } catch (error: unknown) {
    console.error('获取教师数据失败:', error)
    ElMessage.error('获取教师数据失败，请检查网络连接')
    
    // 使用模拟数据
    const mockData: Teacher[] = [
      {
        id: 1,
        teacher_id: 'T001',
        teacher_name: '张老师'
      },
      {
        id: 2,
        teacher_id: 'T002',
        teacher_name: '李老师'
      }
    ]
    
    teachers.value = mockData
    total.value = mockData.length
  } finally {
    loading.value = false
  }
}

// 搜索教师
const searchTeachers = () => {
  currentPage.value = 1
  fetchTeachers()
}

// 重置搜索
const resetSearch = () => {
  searchKeyword.value = ''
  currentPage.value = 1
  fetchTeachers()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchTeachers()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchTeachers()
}



// 点击logo回到学期页面
const goToSemester = () => {
  router.push('/admin/semester')
}



// 显示添加教师对话框
const showAddTeacherDialog = () => {
  isEdit.value = false
  teacherDialogVisible.value = true
}

// 编辑教师
const editTeacher = async (teacher: Teacher) => {
  try {
    // 获取教师详细信息
    const response = await axios.get(`/admin/teachers/${teacher.teacher_id}`)
    
    if (response.data) {
      isEdit.value = true
      editingTeacherId.value = teacher.teacher_id
      teacherForm.teacher_id = response.data.teacher_id
      teacherForm.teacher_name = response.data.teacher_name
      teacherForm.teacher_password = '' // 密码不回显
      teacherDialogVisible.value = true
    }
  } catch (error: unknown) {
    console.error('获取教师信息失败:', error)
    ElMessage.error('获取教师信息失败')
  }
}

// 关闭对话框
const handleCloseDialog = () => {
  teacherDialogVisible.value = false
  // 重置表单
  if (teacherFormRef.value) {
    teacherFormRef.value.resetFields()
  }
  teacherForm.teacher_id = ''
  teacherForm.teacher_name = ''
  teacherForm.teacher_password = ''
  editingTeacherId.value = ''
}

// 提交教师信息
const submitTeacher = async () => {
  if (!teacherFormRef.value) return
  
  try {
    // 表单验证
    await teacherFormRef.value.validate()
    
    submitLoading.value = true
    
    let response
    
    if (isEdit.value) {
      // 更新教师
      response = await axios.put(`/admin/teachers/${editingTeacherId.value}`, {
        teacher_name: teacherForm.teacher_name,
        teacher_password: teacherForm.teacher_password
      })
    } else {
      // 创建教师
      response = await axios.post('/admin/teachers', {
        teacher_id: teacherForm.teacher_id,
        teacher_name: teacherForm.teacher_name,
        teacher_password: teacherForm.teacher_password
      })
    }
    
    if (response.data.success) {
      ElMessage.success(response.data.message || `教师${isEdit.value ? '更新' : '创建'}成功`)
      handleCloseDialog()
      // 重新获取教师数据
      await fetchTeachers()
    } else {
      ElMessage.error(response.data.message || `教师${isEdit.value ? '更新' : '创建'}失败`)
    }
  } catch (error: unknown) {
    console.error(`${isEdit.value ? '更新' : '创建'}教师失败:`, error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: unknown; message?: string } } }
      if (axiosError.response?.data?.detail) {
        // 返回后端的detail字段
        const detail = axiosError.response.data.detail
        if (Array.isArray(detail) && detail.length > 0) {
          ElMessage.error(detail[0].msg || `教师${isEdit.value ? '更新' : '创建'}失败`)
        } else if (typeof detail === 'string') {
          ElMessage.error(detail)
        } else {
          ElMessage.error(`教师${isEdit.value ? '更新' : '创建'}失败`)
        }
      } else if (axiosError.response?.data?.message) {
        ElMessage.error(axiosError.response.data.message)
      } else {
        ElMessage.error(`教师${isEdit.value ? '更新' : '创建'}失败，请检查网络连接`)
      }
    } else {
      ElMessage.error(`教师${isEdit.value ? '更新' : '创建'}失败，请检查网络连接`)
    }
  } finally {
    submitLoading.value = false
  }
}

// 删除教师
const deleteTeacher = async (teacherId: string) => {
  try {
    // 确认删除
    const confirmResult = await ElMessageBox.confirm(
      '确定要删除这个教师吗？如果有关联课程则无法删除。',
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
    
    // 调用删除教师接口
    const response = await axios.delete(`/admin/teachers/${teacherId}`)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '教师删除成功')
      // 重新获取教师数据
      await fetchTeachers()
    } else {
      ElMessage.error(response.data.message || '教师删除失败')
    }
  } catch (error: unknown) {
    console.error('删除教师失败:', error)
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: unknown; message?: string } } }
      if (axiosError.response?.data?.detail) {
        // 返回后端的detail字段
        const detail = axiosError.response.data.detail
        if (Array.isArray(detail) && detail.length > 0) {
          ElMessage.error(detail[0].msg || '删除教师失败')
        } else if (typeof detail === 'string') {
          ElMessage.error(detail)
        } else {
          ElMessage.error('删除教师失败')
        }
      } else if (axiosError.response?.data?.message) {
        ElMessage.error(axiosError.response.data.message)
      } else {
        ElMessage.error('删除教师失败，请检查网络连接')
      }
    } else {
      ElMessage.error('删除教师失败，请检查网络连接')
    }
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchTeachers()
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

.header-menu :deep(.el-menu-item) {
  color: white;
  border-bottom: none;
}

.header-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.header-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.2);
  border-bottom: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-size: 14px;
}

.teacher-label {
  font-size: 14px;
  color: white;
  margin-left: 10px;
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

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e6e6e6;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

/* 表格容器 */
.table-container {
  flex: 1;
  margin-bottom: 20px;
}

/* 分页容器 */
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>