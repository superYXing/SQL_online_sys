<template>
  <div class="teacher-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToHome">SQL在线实践平台</span>
        <div class="nav-buttons">
          <el-button type="text" @click="goToDashboard" class="nav-btn">数据面板</el-button>
          <el-button type="text" @click="goToDatabaseSchema" class="nav-btn">数据库模式</el-button>
          <el-button type="text" @click="goToProblem" class="nav-btn active">题目</el-button>
          <el-button type="text" @click="goToStudentInfo" class="nav-btn">学生信息</el-button>
        </div>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand" trigger="click">
          <span class="username-dropdown">
            {{ teacherInfo.teacher_name || '加载中...' }} <el-icon class="el-icon--right"><arrow-down /></el-icon>
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
              <h3><el-icon><DataAnalysis /></el-icon> 数据库模式</h3>
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
          <div class="middle-panel" v-if="selectedSchema">
            <div class="problems-section">
              <div class="problems-header">
                <h3><el-icon><Files /></el-icon> 题目管理</h3>
                <el-button type="primary" @click="showCreateDialog" class="create-btn">
                  <el-icon><Plus /></el-icon>
                  新建
                </el-button>
              </div>
              <div class="problem-list">
                <div
                  v-for="(problem, index) in currentProblems"
                  :key="problem.problem_id"
                  class="problem-item"
                  :class="{ 'selected': selectedProblem && selectedProblem.problem_id === problem.problem_id }"
                  @click="selectProblem(problem)"
                >
                  <div class="problem-header">
                    <span class="problem-number">NO.{{ index + 1 }}</span>
                    <span class="problem-status" :class="problem.is_required ? 'required' : 'optional'">
                      {{ problem.is_required ? '必做题' : '选做题' }}
                    </span>
                    <span class="problem-status approved">已通过审核</span>
                  </div>
                  <div class="problem-title">{{ getProblemTitle(problem, index) }}</div>
                  <div class="problem-meta">
                    <span class="problem-date">{{ formatDate(new Date()) }}</span>
                    <div class="problem-actions">
                      <el-button type="primary" size="small" @click.stop="editProblem(problem)">编辑</el-button>
                      <el-button type="danger" size="small" @click.stop="deleteProblem(problem)">删除</el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：题目详情 -->
          <div class="right-panel" v-if="selectedSchema">
            <div class="panel-header">
              <h3><el-icon><Document /></el-icon> 题目详情</h3>
            </div>
            
            <!-- 未选择题目时的空状态 -->
            <div class="no-selection" v-if="!selectedProblem">
              <el-empty description="请选择一个题目查看详情" />
            </div>
            
            <!-- 题目详情内容 -->
            <div class="problem-detail-content" v-if="selectedProblem">
              <!-- 题目标题和操作 -->
              <div class="detail-header">
                <div class="detail-title">
                  <h3>{{ getProblemNumber(selectedProblem) }}</h3>
                  <div class="detail-actions">
                    <el-button type="primary" size="small" @click="editProblem(selectedProblem)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button type="danger" size="small" @click="deleteProblem(selectedProblem)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>

              <!-- 紧凑信息卡片 -->
              <div class="compact-info-grid">
                <!-- 题目属性 -->
                <div class="info-card">
                  <div class="card-title">题目属性</div>
                  <div class="attribute-tags">
                    <el-tag v-if="selectedProblem.is_required" type="danger" size="small">必做题</el-tag>
                    <el-tag v-else type="info" size="small">选做题</el-tag>
                    <el-tag v-if="selectedProblem.is_ordered" type="warning" size="small">有序</el-tag>
                    <el-tag v-else type="success" size="small">无序</el-tag>
                    <el-tag type="" size="small">已通过审核</el-tag>
                  </div>
                </div>

                <!-- 统计信息 -->
                <div class="info-card" v-if="problemStats">
                  <div class="card-title">统计数据</div>
                  <div class="stats-compact">
                    <span class="stat-item">完成: {{ problemStats.completed_student_count || 0 }}人</span>
                    <span class="stat-item">提交: {{ problemStats.total_submission_count || 0 }}次</span>
                  </div>
                </div>

                <!-- 知识点 -->
                <div class="info-card">
                  <div class="card-title">知识点</div>
                  <div class="knowledge-points">
                    <div class="placeholder-box"></div>
                    <div class="placeholder-box"></div>
                    <div class="placeholder-box"></div>
                  </div>
                </div>
              </div>

              <!-- 题目内容 -->
              <div class="content-section">
                <div class="section-title">📝 题干</div>
                <div class="content-box">
                  <div v-html="selectedProblem.problem_content || '暂无题干'"></div>
                </div>
              </div>

              <!-- 示例SQL -->
              <div class="content-section" v-if="selectedProblem.example_sql">
                <div class="section-title">💻 示例SQL</div>
                <div class="sql-box">
                  <pre><code>{{ selectedProblem.example_sql }}</code></pre>
                </div>
              </div>

              <!-- 评判标准 -->
              <div class="content-section">
                <div class="section-title">⚖️ 评判标准</div>
                <div class="criteria-box">
                  <div class="criteria-item">
                    <span class="criteria-label">结果排序:</span>
                    <span class="criteria-value">{{ selectedProblem.is_ordered ? '有序（严格按顺序匹配）' : '无序（不要求顺序）' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- 编辑/新建题目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEditing ? '编辑题目' : '新建题目'"
      width="60%"
      :before-close="handleDialogClose"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="120px">
        <el-form-item label="是否必做题" prop="is_required">
          <el-switch
            v-model="editForm.is_required"
            :active-value="1"
            :inactive-value="0"
            active-text="必做题"
            inactive-text="选做题"
          />
        </el-form-item>
        <el-form-item label="是否有序" prop="is_ordered">
          <el-switch
            v-model="editForm.is_ordered"
            :active-value="1"
            :inactive-value="0"
            active-text="有序"
            inactive-text="无序"
          />
        </el-form-item>
        <el-form-item label="题目内容" prop="problem_content">
          <el-input
            v-model="editForm.problem_content"
            type="textarea"
            :rows="8"
            placeholder="请输入题目内容"
          />
        </el-form-item>
        <el-form-item label="示例SQL" prop="example_sql">
          <el-input
            v-model="editForm.example_sql"
            type="textarea"
            :rows="6"
            placeholder="请输入示例SQL（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit" :loading="submitting">
            {{ isEditing ? '保存' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  DataAnalysis,
  Files,
  Document,
  Plus,
  Edit,
  Delete,
  ArrowLeft
} from '@element-plus/icons-vue'
import axios from '@/utils/axios'

const router = useRouter()

// 响应式数据
const teacherInfo = ref<any>({})
const schemaList = ref<any[]>([])
const allProblemsData = ref<any[]>([])
const currentProblems = ref<any[]>([])
const selectedSchema = ref<string>('')
const selectedSchemaInfo = ref<any>(null)
const selectedProblem = ref<any>(null)
const problemStats = ref<any>(null)

// 对话框相关
const editDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const isEditing = ref(false)
const submitting = ref(false)

// 表单数据
const editForm = ref({
  problem_id: 0,
  is_required: 1,
  is_ordered: 0,
  problem_content: '',
  example_sql: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单引用
const editFormRef = ref()
const passwordFormRef = ref()

// 表单验证规则
const editRules = {
  problem_content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
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
      trigger: 'blur'
    }
  ]
}

// 生命周期
onMounted(() => {
  fetchTeacherInfo()
  fetchAllProblems()
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

// 获取所有题目数据
const fetchAllProblems = async () => {
  try {
    const response = await axios.get('/public/problem/list')
    if (response.data && Array.isArray(response.data)) {
      allProblemsData.value = response.data
      // 提取所有数据库模式
      schemaList.value = response.data.map((item: any) => ({
        schema_id: item.schema_id, // 添加schema_id字段
        schema_name: item.schema_name,
        schema_author: '系统' // 根据API响应，没有author字段，使用默认值
      }))
    }
  } catch (error) {
    console.error('获取题目数据失败:', error)
    ElMessage.error('获取题目数据失败')
  }
}

// 选择数据库模式
const selectSchema = async (schema: any) => {
  selectedSchema.value = schema.schema_name
  selectedSchemaInfo.value = schema
  selectedProblem.value = null

  // 调用public/problem/list接口获取该模式下的题目列表
  await fetchProblemsBySchemaFromPublic(schema.schema_name)
}

// 从public接口根据数据库模式获取题目列表
const fetchProblemsBySchemaFromPublic = async (schemaName: string) => {
  try {
    const response = await axios.get('/public/problem/list')
    
    if (response.data && Array.isArray(response.data)) {
      // 收集所有题目并过滤出属于当前schema的题目
      let allProblems: any[] = []
      
      // 遍历所有数据库模式，收集题目
      response.data.forEach((schemaItem: any) => {
        if (schemaItem.problems && Array.isArray(schemaItem.problems)) {
          // 为每个题目添加schema_name标识
          const problemsWithSchema = schemaItem.problems.map((problem: any) => ({
            ...problem,
            schema_name: schemaItem.schema_name
          }))
          allProblems = allProblems.concat(problemsWithSchema)
        }
      })
      
      // 过滤出属于当前schema的题目
      const filteredProblems = allProblems.filter((problem: any) => problem.schema_name === schemaName)
      
      if (filteredProblems.length > 0) {
        currentProblems.value = filteredProblems
      } else {
        currentProblems.value = []
        ElMessage.warning('该数据库模式下暂无题目')
      }
    } else {
      currentProblems.value = []
      ElMessage.warning('获取题目数据格式错误')
    }
  } catch (error) {
    console.error('获取题目列表失败:', error)
    ElMessage.error('获取题目列表失败')
    currentProblems.value = []
  }
}

// 根据数据库模式获取题目列表（保留原函数以备其他地方使用）
const fetchProblemsBySchema = async (schemaId: number) => {
  try {
    const response = await axios.get('/teacher/problem/list', {
      params: {
        schema_id: schemaId
      }
    })
    
    if (response.data && response.data.code === 200 && response.data.data) {
      currentProblems.value = response.data.data
    } else {
      currentProblems.value = []
      ElMessage.warning('该数据库模式下暂无题目')
    }
  } catch (error) {
    console.error('获取题目列表失败:', error)
    ElMessage.error('获取题目列表失败')
    currentProblems.value = []
  }
}

// 选择题目
const selectProblem = async (problem: any) => {
  // 通过teacher/problem/list接口获取题目详情
  const teacherProblemDetail = await fetchProblemDetailFromTeacher(problem.problem_id)
  
  // 合并public接口和teacher接口的数据
  selectedProblem.value = {
    ...problem, // public接口的基础数据
    ...teacherProblemDetail // teacher接口的详细数据（is_required, is_ordered等）
  }
  
  await fetchProblemStats(problem.problem_id)
}

// 从teacher接口获取题目详细内容
const fetchProblemDetailFromTeacher = async (problemId: number) => {
  try {
    // 如果teacher接口支持schema_name参数，使用schema_name
    // 否则仍使用schema_id（需要根据实际API接口确定）
    const params: any = {}
    if (selectedSchemaInfo.value?.schema_name) {
      params.schema_name = selectedSchemaInfo.value.schema_name
    } else if (selectedSchemaInfo.value?.schema_id) {
      params.schema_id = selectedSchemaInfo.value.schema_id
    }
    
    const response = await axios.get('/teacher/problem/list', {
      params: params
    })
    
    if (response.data && response.data.code === 200 && response.data.data) {
      const problemDetail = response.data.data.find((p: any) => p.problem_id === problemId)
      if (problemDetail) {
        return problemDetail
      }
    }
    
    console.warn(`未找到problem_id为${problemId}的题目详情`)
    return {}
  } catch (error) {
    console.error('获取题目详情失败:', error)
    return {}
  }
}

// 从public接口获取题目详细内容（保留原函数以备其他地方使用）
const fetchProblemDetailFromPublic = async (problemId: number) => {
  try {
    // 从已缓存的allProblemsData中查找对应的题目详情
    for (const schemaData of allProblemsData.value) {
      if (schemaData.problems) {
        const problemDetail = schemaData.problems.find((p: any) => p.problem_id === problemId)
        if (problemDetail) {
          return problemDetail
        }
      }
    }
    
    // 如果缓存中没有找到，返回空对象
    console.warn(`未找到problem_id为${problemId}的题目详情`)
    return {}
  } catch (error) {
    console.error('获取题目详情失败:', error)
    return {}
  }
}

// 获取题目统计信息
const fetchProblemStats = async (problemId: number) => {
  try {
    const response = await axios.get('/teacher/problem/summary', {
      params: { problem_id: problemId }
    })
    if (response.data && response.data.data) {
      problemStats.value = response.data.data
    }
  } catch (error) {
    console.error('获取题目统计失败:', error)
    problemStats.value = null
  }
}

// 显示新建对话框
const showCreateDialog = () => {
  if (!selectedSchemaInfo.value) {
    ElMessage.warning('请先选择一个数据库模式')
    return
  }
  
  isEditing.value = false
  editForm.value = {
    problem_id: 0,
    is_required: 1,
    is_ordered: 0,
    problem_content: '',
    example_sql: ''
  }
  editDialogVisible.value = true
}

// 编辑题目
const editProblem = (problem: any) => {
  isEditing.value = true
  editForm.value = {
    problem_id: problem.problem_id,
    is_required: problem.is_required !== undefined ? problem.is_required : 1,
    is_ordered: problem.is_ordered !== undefined ? problem.is_ordered : 0,
    problem_content: problem.problem_content || '',
    example_sql: problem.example_sql || ''
  }
  editDialogVisible.value = true
}

// 删除题目
const deleteProblem = async (problem: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除题目"${getProblemTitle(problem)}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await axios.delete('/teacher/problem/delete', {
      params: { problem_id: problem.problem_id }
    })

    if (response.data && response.data.code === 200) {
      ElMessage.success('题目删除成功')
      // 刷新题目列表
      await fetchAllProblems()
      // 如果删除的是当前选中的题目，返回列表
      if (selectedProblem.value && selectedProblem.value.problem_id === problem.problem_id) {
        selectedProblem.value = null
      }
      // 重新选择当前模式以刷新题目列表
      if (selectedSchemaInfo.value) {
        selectSchema(selectedSchemaInfo.value)
      }
    } else {
      ElMessage.error(response.data?.msg || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除题目失败:', error)
      ElMessage.error('删除题目失败')
    }
  }
}

// 提交编辑
const submitEdit = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()
    submitting.value = true

    if (isEditing.value) {
      // 编辑题目
      const response = await axios.put('/teacher/problem/edit', editForm.value)
      if (response.data && response.data.code === 200) {
        ElMessage.success('题目更新成功')
        editDialogVisible.value = false
        // 刷新题目列表
        await fetchAllProblems()
        // 重新选择当前模式以刷新题目列表
        if (selectedSchemaInfo.value) {
          selectSchema(selectedSchemaInfo.value)
        }
      } else {
        ElMessage.error(response.data?.msg || '更新失败')
      }
    } else {
      // 新建题目
      const createData: any = {
        is_required: editForm.value.is_required,
        is_ordered: editForm.value.is_ordered,
        problem_content: editForm.value.problem_content,
        example_sql: editForm.value.example_sql
      }
      
      // 如果有选中的模式，添加schema_id
      if (selectedSchemaInfo.value && selectedSchemaInfo.value.schema_id) {
        createData.schema_id = selectedSchemaInfo.value.schema_id
      }
      
      const response = await axios.post('/teacher/problem/create', createData)
      
      if (response.data && response.data.code === 200) {
        ElMessage.success('题目创建成功')
        editDialogVisible.value = false
        // 刷新题目列表
        await fetchAllProblems()
        // 重新选择当前模式以刷新题目列表
        if (selectedSchemaInfo.value) {
          selectSchema(selectedSchemaInfo.value)
        }
      } else {
        ElMessage.error(response.data?.msg || '创建失败')
      }
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleDialogClose = () => {
  editDialogVisible.value = false
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
}

// 格式化日期
const formatDate = (date: Date) => {
  return date.toLocaleDateString('zh-CN')
}

// 获取题目编号（NO.1, NO.2格式）
const getProblemNumber = (problem: any) => {
  if (!problem) return 'NO.0'
  
  // 在当前题目列表中找到该题目的索引位置
  const index = currentProblems.value.findIndex(p => p.problem_id === problem.problem_id)
  return `NO.${index >= 0 ? index + 1 : 1}`
}

// 获取题目标题
const getProblemTitle = (problem: any, index?: number) => {
  if (!problem) return '题目详情'

  // 如果有problem_content，取前30个字符作为标题
  if (problem.problem_content) {
    const content = problem.problem_content.replace(/<[^>]*>/g, '').trim() // 移除HTML标签
    if (content.length > 30) {
      return content.substring(0, 30) + '...'
    }
    return content || `题目 ${problem.problem_id}`
  }

  // 否则使用题目ID或索引
  if (problem.problem_id) {
    return `题目 ${problem.problem_id}`
  }

  return `题目 ${(index || 0) + 1}`
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
  // 当前页面，不需要跳转
}

const goToStudentInfo = () => {
  router.push('/teacher/student-info')
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
      new_password: passwordForm.value.newPassword
    })

    if (response.data && response.data.code === 200) {
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
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
  align-items: center;
  gap: 4px;
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

/* 任务包装器 */
.task-wrapper {
  display: grid;
  grid-template-columns: 250px 300px 1fr;
  height: 100%;
  gap: 0;
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

/* 数据库模式列表 */
.schema-list {
  padding: 16px;
}

.schema-item {
  padding: 12px 16px;
  margin-bottom: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #ffffff;
}

.schema-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.schema-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.schema-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.schema-author {
  font-size: 12px;
  color: #909399;
}

/* 题目列表 */
.problems-section {
  padding: 16px;
}

.problems-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.problems-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.problem-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.problem-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #ffffff;
}

.problem-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.problem-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.problem-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.problem-number {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.problem-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.problem-status.required {
  background-color: #fef0f0;
  color: #f56c6c;
}

.problem-status.optional {
  background-color: #f0f9ff;
  color: #409eff;
}

.problem-status.approved {
  background-color: #f0f9ff;
  color: #67c23a;
}

.problem-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  font-size: 14px;
}

.problem-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.problem-date {
  font-size: 12px;
  color: #909399;
}

.problem-actions {
  display: flex;
  gap: 8px;
}

/* 题目详情内容 */
.problem-detail-content {
  padding: 16px;
  overflow-y: auto;
  height: calc(100% - 60px);
}

.problem-info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.problem-title-section {
  flex: 1;
}

.problem-title-section h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.problem-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.problem-actions-detail {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.problem-stats-section {
  margin-bottom: 16px;
}

.problem-stats-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.stat-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.problem-content-section {
  margin-bottom: 16px;
}

.problem-content-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.problem-content {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  line-height: 1.5;
  color: #303133;
  font-size: 13px;
  max-height: 200px;
  overflow-y: auto;
}

.example-sql-section {
  margin-top: 16px;
}

.example-sql-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.sql-code {
  background-color: #f5f5f5;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
  max-height: 150px;
  overflow-y: auto;
}

.sql-code pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #303133;
  white-space: pre-wrap;
}

/* 空状态 */
.no-selection {
  padding: 40px 20px;
  text-align: center;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 紧凑信息卡片样式 */
.compact-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.info-card {
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
}

.card-title {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.attribute-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.stats-compact {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-compact .stat-item {
  font-size: 12px;
  color: #303133;
}

.knowledge-points {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.placeholder-box {
  width: 40px;
  height: 20px;
  background-color: #e4e7ed;
  border-radius: 4px;
}

.detail-header {
  margin-bottom: 16px;
}

.detail-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.content-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.content-box {
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  line-height: 1.6;
  color: #303133;
  font-size: 13px;
}

.sql-box {
  background-color: #f5f5f5;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
}

.sql-box pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #303133;
  white-space: pre-wrap;
}

.criteria-box {
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
}

.criteria-item {
  display: flex;
  margin-bottom: 8px;
}

.criteria-item:last-child {
  margin-bottom: 0;
}

.criteria-label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
  margin-right: 8px;
}

.criteria-value {
  color: #303133;
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

  .problems-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .problem-actions-detail {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .compact-info-grid {
    grid-template-columns: 1fr;
  }

  .detail-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .detail-actions {
    align-self: stretch;
  }
}
</style>
