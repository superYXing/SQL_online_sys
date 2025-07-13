<template>
  <div class="teacher-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="goToHome">SQL在线实践平台</span>
        <div class="nav-buttons">
          <el-button type="text" @click="goToDashboard" class="nav-btn">数据面板</el-button>
          <el-button type="text" @click="goToDatabaseSchema" class="nav-btn active"
            >数据库模式</el-button
          >
          <el-button type="text" @click="goToProblem" class="nav-btn">题目</el-button>
          <el-button type="text" @click="goToStudentInfo" class="nav-btn">学生信息</el-button>
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
        <div class="schema-wrapper" :class="{ 'has-selection': selectedSchema }">
          <!-- 左侧：数据库模式列表 -->
          <div class="left-panel">
            <div class="panel-header">
              <div class="header-content">
                <div class="header-title">
                  <el-button type="text" @click="goBack" class="back-btn">
                    <el-icon><ArrowLeft /></el-icon>
                  </el-button>
                  <h3 class="title-with-spacing">
                    <el-icon><DataAnalysis /></el-icon> 数据库模式
                  </h3>
                </div>
                <el-button type="primary" @click="showCreateDialog" class="create-btn">
                  <el-icon><Plus /></el-icon>
                  创建模式
                </el-button>
              </div>
            </div>
            <div class="schema-list">
              <div
                v-for="schema in schemaList"
                :key="schema.schema_name"
                class="schema-item"
                :class="{ active: selectedSchema === schema.schema_name }"
                @click="selectSchema(schema)"
              >
                <div class="schema-content">
                  <div class="schema-name">{{ schema.schema_name }}</div>
                  <div class="schema-author">{{ schema.schema_author }}</div>
                  <!-- 数据库模式状态信息 -->
                  <div class="schema-visibility">
                    <el-tag :type="getVisibilityTagType(schema.schema_status || 0)" size="small">
                      {{ getVisibilityText(schema.schema_status || 0) }}
                    </el-tag>
                  </div>
                </div>
                <div class="schema-actions">
                  <el-button
                    type="danger"
                    size="small"
                    @click.stop="deleteSchema(schema)"
                    :loading="deleteLoading === schema.schema_id"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 状态信息说明 -->
            <div class="visibility-info">
              <h4>📋 数据库模式状态说明</h4>
              <div class="visibility-options">
                <div class="visibility-option">
                  <el-radio v-model="schemaStatus" :label="1"> 完全可见 </el-radio>
                  <p class="option-desc">
                    学生可以使用数据库模式的题目，也可以使用数据库模式的查询功能。
                  </p>
                </div>
                <div class="visibility-option">
                  <el-radio v-model="schemaStatus" :label="0"> 不可见 </el-radio>
                  <p class="option-desc">数据库模式对学生透明。</p>
                </div>
              </div>
              <div class="status-actions">
                <el-button
                  type="primary"
                  @click="updateSchemaStatus"
                  :loading="statusLoading"
                  class="confirm-btn"
                >
                  确认设置
                </el-button>
              </div>
            </div>
          </div>

          <!-- 中间：选项表单（选择模式后显示） -->
          <div class="middle-panel" v-if="selectedSchema">
            <div class="panel-header">
              <h3>
                <el-icon><Setting /></el-icon> 数据库模式操作
              </h3>
            </div>
            <div class="option-buttons">
              <el-button
                :type="activeTab === 'basic' ? 'primary' : 'default'"
                @click="activeTab = 'basic'"
                class="option-btn"
              >
                基本信息
              </el-button>
              <el-button
                :type="activeTab === 'query' ? 'primary' : 'default'"
                @click="activeTab = 'query'"
                class="option-btn"
              >
                查询面板
              </el-button>
              <el-button
                :type="activeTab === 'tables' ? 'primary' : 'default'"
                @click="activeTab = 'tables'"
                class="option-btn"
              >
                数据表
              </el-button>
              <el-button
                :type="activeTab === 'views' ? 'primary' : 'default'"
                @click="activeTab = 'views'"
                class="option-btn"
              >
                视图
              </el-button>
            </div>
          </div>

          <!-- 右侧：内容面板（选择模式后显示） -->
          <div class="right-panel" v-if="selectedSchema">
            <!-- 基本信息 -->
            <div v-if="activeTab === 'basic'" class="content-panel">
              <div class="panel-header">
                <h3>
                  <el-icon><Document /></el-icon> 基本信息
                </h3>
                <div class="header-actions">
                  <el-button v-if="!isEditMode" type="primary" @click="enterEditMode">
                    <el-icon><Edit /></el-icon>
                    编辑模式
                  </el-button>
                  <div v-else class="edit-actions">
                    <el-button @click="cancelEdit">取消</el-button>
                    <el-button type="primary" @click="saveChanges" :loading="editLoading">
                      <el-icon><Check /></el-icon>
                      保存修改
                    </el-button>
                  </div>
                </div>
              </div>
              <div class="basic-info-content">
                <div class="schema-header">
                  <h2 v-if="!isEditMode">{{ selectedSchemaInfo.schema_name }}</h2>
                  <el-input
                    v-else
                    v-model="editForm.schema_name"
                    placeholder="数据库模式名称"
                    class="schema-name-input"
                  />
                  <p class="author">作者：{{ selectedSchemaInfo.schema_author }}</p>
                </div>

                <!-- 数据库模式描述 -->
                <div class="schema-description">
                  <h4>📝 数据库模式描述</h4>
                  <div v-if="!isEditMode" class="description-viewer expanded">
                    <div
                      v-html="selectedSchemaInfo.schema_description || getDefaultDescription()"
                    ></div>
                    <el-pagination
                      v-if="false"
                      v-model:current-page="currentPage"
                      :page-size="pageSize"
                      :total="1000"
                      layout="prev, pager, next"
                      class="description-pagination"
                    />
                  </div>
                  <div v-else class="description-editor">
                    <div class="html-editor-header">
                      <div class="editor-tabs">
                        <el-button
                          :type="editHtmlViewMode === 'edit' ? 'primary' : 'default'"
                          @click="editHtmlViewMode = 'edit'"
                          size="small"
                        >
                          <el-icon><Edit /></el-icon>
                          编辑
                        </el-button>
                        <el-button
                          :type="editHtmlViewMode === 'preview' ? 'primary' : 'default'"
                          @click="editHtmlViewMode = 'preview'"
                          size="small"
                        >
                          <el-icon><View /></el-icon>
                          预览
                        </el-button>
                        <el-button
                          :type="editHtmlViewMode === 'split' ? 'primary' : 'default'"
                          @click="editHtmlViewMode = 'split'"
                          size="small"
                        >
                          <el-icon><Grid /></el-icon>
                          分栏
                        </el-button>
                      </div>
                    </div>
                    <div class="html-editor-content" :class="`mode-${editHtmlViewMode}`">
                      <!-- 编辑模式 -->
                      <div v-if="editHtmlViewMode === 'edit'" class="editor-panel full">
                        <el-input
                          v-model="editForm.html_content"
                          type="textarea"
                          :rows="20"
                          placeholder="请输入HTML代码..."
                          class="html-code-editor"
                        />
                      </div>
                      <!-- 预览模式 -->
                      <div v-else-if="editHtmlViewMode === 'preview'" class="preview-panel full">
                        <div
                          class="html-preview"
                          v-html="editForm.html_content || '<p>暂无内容</p>'"
                        ></div>
                      </div>
                      <!-- 分栏模式 -->
                      <div v-else class="split-view">
                        <div class="editor-panel half">
                          <div class="panel-title">HTML代码</div>
                          <el-input
                            v-model="editForm.html_content"
                            type="textarea"
                            :rows="18"
                            placeholder="请输入HTML代码..."
                            class="html-code-editor"
                          />
                        </div>
                        <div class="preview-panel half">
                          <div class="panel-title">预览效果</div>
                          <div
                            class="html-preview"
                            v-html="editForm.html_content || '<p>暂无内容</p>'"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 编辑模式下的额外配置 -->
                <div v-if="isEditMode" class="edit-config">
                  <div class="config-item">
                    <h4>📋 SQL模式名称</h4>
                    <el-input v-model="editForm.sql_schema" placeholder="请输入SQL模式名称" />
                  </div>
                  <div class="config-item">
                    <h4>📁 更新MySQL建表文件（可选）</h4>
                    <el-upload
                      :before-upload="(file) => handleEditFileChange(file, 'mysql')"
                      :show-file-list="true"
                      :limit="1"
                      accept=".sql"
                      drag
                      class="sql-file-upload"
                    >
                      <el-icon class="el-icon--upload"><Upload /></el-icon>
                      <div class="el-upload__text">
                        将MySQL SQL文件拖到此处，或<em>点击上传</em>
                      </div>
                      <template #tip>
                        <div class="el-upload__tip">
                          只能上传.sql文件，且不超过10MB。如不上传则保持原有文件不变。
                        </div>
                      </template>
                    </el-upload>

                    <!-- MySQL文件内容显示 -->
                    <div
                      v-if="editMysqlFileContent"
                      class="sql-content-display"
                      style="margin-top: 10px"
                    >
                      <el-input
                        v-model="editMysqlFileContent"
                        type="textarea"
                        :rows="4"
                        readonly
                        placeholder="MySQL SQL文件内容"
                        class="sql-content-textarea"
                      />
                    </div>
                  </div>

                  <div class="config-item">
                    <h4>📁 更新PostgreSQL/OpenGauss建表文件（可选）</h4>
                    <el-upload
                      :before-upload="(file) => handleEditFileChange(file, 'postgresql')"
                      :show-file-list="true"
                      :limit="1"
                      accept=".sql"
                      drag
                      class="sql-file-upload"
                    >
                      <el-icon class="el-icon--upload"><Upload /></el-icon>
                      <div class="el-upload__text">
                        将PostgreSQL/OpenGauss SQL文件拖到此处，或<em>点击上传</em>
                      </div>
                      <template #tip>
                        <div class="el-upload__tip">
                          只能上传.sql文件，且不超过10MB。如不上传则保持原有文件不变。
                        </div>
                      </template>
                    </el-upload>

                    <!-- PostgreSQL文件内容显示 -->
                    <div
                      v-if="editPostgresqlFileContent"
                      class="sql-content-display"
                      style="margin-top: 10px"
                    >
                      <el-input
                        v-model="editPostgresqlFileContent"
                        type="textarea"
                        :rows="4"
                        readonly
                        placeholder="PostgreSQL/OpenGauss SQL文件内容"
                        class="sql-content-textarea"
                      />
                    </div>
                  </div>
                </div>

                <!-- 数据库模式状态说明 -->
                <div class="visibility-info">
                  <h4>📋 数据库模式状态说明</h4>
                  <div class="visibility-options">
                    <div class="visibility-option">
                      <el-tag type="success" size="small">完全可见</el-tag>
                      <p class="option-desc">
                        学生可以使用数据库模式的题目，也可以使用数据库模式的查询功能。
                      </p>
                    </div>
                    <div class="visibility-option">
                      <el-tag type="danger" size="small">不可见</el-tag>
                      <p class="option-desc">数据库模式对学生透明。</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 查询面板 -->
            <div v-if="activeTab === 'query'" class="content-panel">
              <div class="panel-header">
                <h3>
                  <el-icon><Search /></el-icon> SQL操作（全部权限）（pgsql引擎）
                </h3>
                <div class="query-actions">
                  <el-button type="primary" @click="executeQuery" :loading="queryLoading">
                    <el-icon><Search /></el-icon>
                    查询
                  </el-button>
                  <el-button @click="clearQuery">
                    <el-icon><Delete /></el-icon>
                    清空
                  </el-button>
                </div>
              </div>

              <div class="query-content">
                <!-- SQL编辑器 -->
                <div class="sql-editor">
                  <el-input
                    v-model="sqlQuery"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入SQL语句，例如：SELECT * FROM EMPLOYEES"
                    class="sql-textarea"
                  />
                </div>

                <!-- 查询结果表格 -->
                <div class="results-section">
                  <div class="results-header">
                    <h4>
                      <el-icon><Grid /></el-icon> 查询结果
                    </h4>
                    <div class="results-info" v-if="queryResults.length > 0">
                      共 {{ queryResults.length }} 条记录
                    </div>
                  </div>

                  <div v-if="queryResults.length === 0 && !queryLoading" class="no-results">
                    <el-empty description="暂无查询结果，请执行SQL查询" />
                  </div>

                  <div v-else class="results-table" v-loading="queryLoading">
                    <el-table
                      :data="queryResults"
                      border
                      stripe
                      height="400"
                      class="query-table"
                      :header-cell-style="{ background: '#409eff', color: '#fff' }"
                    >
                      <el-table-column
                        v-for="column in queryColumns"
                        :key="column"
                        :prop="column"
                        :label="column"
                        min-width="120"
                        show-overflow-tooltip
                      />
                    </el-table>
                  </div>
                </div>
              </div>
            </div>

            <!-- 数据表 -->
            <div v-if="activeTab === 'tables'" class="content-panel">
              <div class="panel-header">
                <h3>
                  <el-icon><Grid /></el-icon> 数据表
                </h3>
              </div>
              <div class="placeholder-content">
                <el-empty description="数据表功能开发中..." />
              </div>
            </div>

            <!-- 视图 -->
            <div v-if="activeTab === 'views'" class="content-panel">
              <div class="panel-header">
                <h3>
                  <el-icon><View /></el-icon> 视图
                </h3>
              </div>
              <div class="placeholder-content">
                <el-empty description="视图功能开发中..." />
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>

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

    <!-- 创建数据库模式对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建数据库模式"
      width="900px"
      class="create-schema-dialog"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
        <el-form-item label="模式名称" prop="schema_name">
          <el-input v-model="createForm.schema_name" placeholder="请输入数据库模式名称" />
        </el-form-item>

        <el-form-item label="SQL模式名称" prop="sql_schema">
          <el-input v-model="createForm.sql_schema" placeholder="请输入SQL模式名称" />
        </el-form-item>

        <el-form-item label="MySQL建表文件" required>
          <el-upload
            :before-upload="(file) => handleFileChange(file, 'mysql')"
            :show-file-list="true"
            :limit="1"
            accept=".sql"
            drag
            class="sql-file-upload"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">将MySQL SQL文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">只能上传.sql文件，且不超过10MB</div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- MySQL SQL文件内容显示区域 -->
        <el-form-item label="MySQL文件内容" v-if="mysqlFileContent">
          <div class="sql-content-display">
            <el-input
              v-model="mysqlFileContent"
              type="textarea"
              :rows="6"
              readonly
              placeholder="MySQL SQL文件内容将在此显示"
              class="sql-content-textarea"
            />
          </div>
        </el-form-item>

        <el-form-item label="PostgreSQL/OpenGauss建表文件" required>
          <el-upload
            :before-upload="(file) => handleFileChange(file, 'postgresql')"
            :show-file-list="true"
            :limit="1"
            accept=".sql"
            drag
            class="sql-file-upload"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将PostgreSQL/OpenGauss SQL文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">只能上传.sql文件，且不超过10MB</div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- PostgreSQL SQL文件内容显示区域 -->
        <el-form-item label="PostgreSQL文件内容" v-if="postgresqlFileContent">
          <div class="sql-content-display">
            <el-input
              v-model="postgresqlFileContent"
              type="textarea"
              :rows="6"
              readonly
              placeholder="PostgreSQL/OpenGauss SQL文件内容将在此显示"
              class="sql-content-textarea"
            />
          </div>
        </el-form-item>

        <el-form-item label="模式描述" prop="html_content">
          <div class="html-editor-container">
            <div class="html-editor-header">
              <div class="editor-tabs">
                <el-button
                  :type="createHtmlViewMode === 'edit' ? 'primary' : 'default'"
                  @click="createHtmlViewMode = 'edit'"
                  size="small"
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button
                  :type="createHtmlViewMode === 'preview' ? 'primary' : 'default'"
                  @click="createHtmlViewMode = 'preview'"
                  size="small"
                >
                  <el-icon><View /></el-icon>
                  预览
                </el-button>
                <el-button
                  :type="createHtmlViewMode === 'split' ? 'primary' : 'default'"
                  @click="createHtmlViewMode = 'split'"
                  size="small"
                >
                  <el-icon><Grid /></el-icon>
                  分栏
                </el-button>
              </div>
            </div>
            <div class="html-editor-content" :class="`mode-${createHtmlViewMode}`">
              <!-- 编辑模式 -->
              <div v-if="createHtmlViewMode === 'edit'" class="editor-panel full">
                <el-input
                  v-model="createForm.html_content"
                  type="textarea"
                  :rows="15"
                  placeholder="请输入HTML代码..."
                  class="html-code-editor"
                />
              </div>
              <!-- 预览模式 -->
              <div v-else-if="createHtmlViewMode === 'preview'" class="preview-panel full">
                <div
                  class="html-preview"
                  v-html="createForm.html_content || '<p>暂无内容</p>'"
                ></div>
              </div>
              <!-- 分栏模式 -->
              <div v-else class="split-view">
                <div class="editor-panel half">
                  <div class="panel-title">HTML代码</div>
                  <el-input
                    v-model="createForm.html_content"
                    type="textarea"
                    :rows="13"
                    placeholder="请输入HTML代码..."
                    class="html-code-editor"
                  />
                </div>
                <div class="preview-panel half">
                  <div class="panel-title">预览效果</div>
                  <div
                    class="html-preview"
                    v-html="createForm.html_content || '<p>暂无内容</p>'"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createSchema" :loading="createLoading">
            创建模式
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
  Plus,
  DataAnalysis,
  Search,
  Delete,
  Grid,
  Document,
  Setting,
  View,
  Upload,
  Edit,
  Check,
} from '@element-plus/icons-vue'
import axios from '@/utils/axios'

const router = useRouter()

// 响应式数据
const teacherInfo = ref<any>({})
const schemaList = ref<any[]>([])
const selectedSchema = ref<string>('')
const selectedSchemaInfo = ref<any>(null)
const activeTab = ref('basic')
const sqlQuery = ref('SELECT * FROM EMPLOYEES')
const queryResults = ref<any[]>([])
const queryColumns = ref<string[]>([])
const queryHistory = ref<any[]>([])

const schemaStatus = ref<number>(1) // 1: 完全可见, 0: 不可见
const statusLoading = ref(false)

// 编辑模式相关
const isEditMode = ref(false)
const editHtmlViewMode = ref('edit') // 'edit', 'preview', 'split'
const editForm = ref({
  schema_id: 0,
  html_content: '',
  schema_name: '',
  mysql_file: null as File | null,
  postgresql_file: null as File | null,
  sql_schema: '',
})
const editFormRef = ref()
const editLoading = ref(false)
const editMysqlFileContent = ref('')
const editPostgresqlFileContent = ref('')
const currentPage = ref(1)
const pageSize = ref(1000) // 设置较大值以显示完整内容

// 创建数据库模式对话框
const createDialogVisible = ref(false)
const createHtmlViewMode = ref('edit') // 'edit', 'preview', 'split'
const createForm = ref({
  html_content: '',
  schema_name: '',
  mysql_file: null as File | null,
  postgresql_file: null as File | null,
  sql_schema: '',
})
const createFormRef = ref()
const createLoading = ref(false)
const mysqlFileContent = ref('')
const postgresqlFileContent = ref('')

// 加载状态
const queryLoading = ref(false)
const deleteLoading = ref<number | null>(null)

// 对话框相关
const passwordDialogVisible = ref(false)

// 表单数据
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// 表单引用
const passwordFormRef = ref()

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

// 创建数据库模式表单验证规则
const createRules = {
  schema_name: [
    { required: true, message: '请输入数据库模式名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  sql_schema: [{ required: true, message: '请输入SQL模式名称', trigger: 'blur' }],
  html_content: [{ required: true, message: '请输入HTML内容', trigger: 'blur' }],
}

// 生命周期
onMounted(() => {
  fetchTeacherInfo()
  fetchSchemaList()
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

// 获取数据库模式列表
const fetchSchemaList = async () => {
  try {
    const response = await axios.get('/public/schema/list')
    if (response.data && Array.isArray(response.data)) {
      schemaList.value = response.data.map((schema) => ({
        ...schema,
        schema_id: schema.schema_id || 1, // 确保有schema_id
      }))
    }
  } catch (error) {
    console.error('获取数据库模式列表失败:', error)
    ElMessage.error('获取数据库模式列表失败')
  }
}

// 选择数据库模式
const selectSchema = (schema: any) => {
  selectedSchema.value = schema.schema_name
  selectedSchemaInfo.value = schema
  activeTab.value = 'basic' // 默认选择基本信息
  // 清空查询结果
  queryResults.value = []
  queryColumns.value = []
  // 根据当前模式的状态初始化schemaStatus
  // 使用后端返回的schema_status字段（0为不可见，1为可见）
  schemaStatus.value = schema.schema_status || 0
}

// 获取选中模式的schema_id
const getSchemaId = (schemaName: string) => {
  // 这里需要根据实际情况获取schema_id
  // 可能需要从API获取或者维护一个映射关系
  const schema = schemaList.value.find((s) => s.schema_name === schemaName)
  return schema ? schema.schema_id || 1 : 1 // 默认返回1
}

// 获取默认描述内容
const getDefaultDescription = () => {
  return `
    <div style="padding: 20px; line-height: 1.6;">
      <h3 style="color: #409eff; margin-bottom: 16px;">Oracle HR 数据库模式</h3>
      <p style="margin-bottom: 12px;">这是Oracle数据库的经典HR（人力资源）示例模式，包含了完整的员工管理系统数据结构。</p>

      <h4 style="color: #606266; margin: 16px 0 8px 0;">主要数据表：</h4>
      <ul style="margin: 0; padding-left: 20px;">
        <li style="margin-bottom: 8px;"><strong>EMPLOYEES</strong> - 员工信息表，包含员工基本信息、薪资、部门等</li>
        <li style="margin-bottom: 8px;"><strong>DEPARTMENTS</strong> - 部门信息表，存储公司各部门详细信息</li>
        <li style="margin-bottom: 8px;"><strong>JOBS</strong> - 职位信息表，定义各种工作岗位</li>
        <li style="margin-bottom: 8px;"><strong>LOCATIONS</strong> - 地理位置表，存储办公地点信息</li>
        <li style="margin-bottom: 8px;"><strong>COUNTRIES</strong> - 国家信息表</li>
        <li style="margin-bottom: 8px;"><strong>REGIONS</strong> - 地区信息表</li>
      </ul>

      <h4 style="color: #606266; margin: 16px 0 8px 0;">数据特点：</h4>
      <ul style="margin: 0; padding-left: 20px;">
        <li style="margin-bottom: 8px;">包含完整的员工层级关系（经理-下属）</li>
        <li style="margin-bottom: 8px;">支持多部门、多地区的组织架构</li>
        <li style="margin-bottom: 8px;">包含薪资历史和职位变更记录</li>
        <li style="margin-bottom: 8px;">适合学习SQL查询、连接、聚合等操作</li>
      </ul>

      <div style="background: #f0f9ff; padding: 12px; border-radius: 6px; margin-top: 16px;">
        <strong style="color: #409eff;">💡 提示：</strong>
        <span style="color: #606266;">这个数据库模式非常适合练习复杂的SQL查询，包括多表连接、子查询、聚合函数等高级特性。</span>
      </div>
    </div>
  `
}

// 执行SQL查询
const executeQuery = async () => {
  if (!sqlQuery.value.trim()) {
    ElMessage.warning('请输入SQL语句')
    return
  }

  if (!selectedSchema.value) {
    ElMessage.warning('请先选择数据库模式')
    return
  }

  queryLoading.value = true
  try {
    const schemaId = getSchemaId(selectedSchema.value)
    const response = await axios.post('/teacher/schema/query', {
      schema_id: schemaId,
      sql: sqlQuery.value,
    })

    if (response.data.code === 200) {
      queryColumns.value = response.data.columns || []

      // 转换行数据为对象数组
      const rows = response.data.rows || []
      queryResults.value = rows.map((row: any[]) => {
        const obj: any = {}
        queryColumns.value.forEach((col, index) => {
          obj[col] = row[index]
        })
        return obj
      })

      // 添加到查询历史
      queryHistory.value.unshift({
        sql: sqlQuery.value,
        time: new Date().toLocaleString(),
      })

      // 限制历史记录数量
      if (queryHistory.value.length > 10) {
        queryHistory.value = queryHistory.value.slice(0, 10)
      }

      ElMessage.success('查询成功')
    } else {
      ElMessage.error(response.data.msg || '查询失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  } finally {
    queryLoading.value = false
  }
}

// 清空查询
const clearQuery = () => {
  sqlQuery.value = ''
}

// 加载历史查询
const loadHistoryQuery = (history: any) => {
  sqlQuery.value = history.sql
}

// 导航函数
const goToHome = () => {
  router.push('/teacher/home')
}

const goToDashboard = () => {
  router.push('/teacher/dashboard')
}

const goToDatabaseSchema = () => {
  // 当前页面，不需要跳转
}

const goToProblem = () => {
  router.push('/teacher/problem')
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

// 回退到上一页
const goBack = () => {
  router.go(-1)
}

// 更新数据库模式状态
const updateSchemaStatus = async () => {
  if (!selectedSchemaInfo.value) {
    ElMessage.warning('请先选择数据库模式')
    return
  }

  try {
    statusLoading.value = true

    const response = await axios.put('/teacher/schema-status', {
      schema_id: selectedSchemaInfo.value.schema_id,
      status: schemaStatus.value,
    })

    if (response.data && response.data.code === 200) {
      ElMessage.success(response.data.message || '权限设置成功')
      // 重新获取模式列表以更新状态显示
      await fetchSchemaList()
    } else {
      ElMessage.error(response.data?.message || '权限设置失败')
    }
  } catch (error) {
    console.error('设置数据库模式权限失败:', error)
    ElMessage.error('设置数据库模式权限失败')
  } finally {
    statusLoading.value = false
  }
}

// 显示创建数据库模式对话框
const showCreateDialog = () => {
  createDialogVisible.value = true
  // 重置表单
  createForm.value = {
    html_content: '',
    schema_name: '',
    mysql_file: null,
    postgresql_file: null,
    sql_schema: '',
  }
  mysqlFileContent.value = ''
  postgresqlFileContent.value = ''
}

// 处理文件上传
const handleFileChange = (file: File, type: 'mysql' | 'postgresql') => {
  if (type === 'mysql') {
    createForm.value.mysql_file = file

    // 读取MySQL文件内容并显示
    const reader = new FileReader()
    reader.onload = (e) => {
      mysqlFileContent.value = e.target?.result as string
    }
    reader.onerror = () => {
      ElMessage.error('MySQL文件读取失败')
    }
    reader.readAsText(file)
  } else if (type === 'postgresql') {
    createForm.value.postgresql_file = file

    // 读取PostgreSQL文件内容并显示
    const reader = new FileReader()
    reader.onload = (e) => {
      postgresqlFileContent.value = e.target?.result as string
    }
    reader.onerror = () => {
      ElMessage.error('PostgreSQL文件读取失败')
    }
    reader.readAsText(file)
  }

  return false // 阻止自动上传
}

// 处理编辑模式文件上传
const handleEditFileChange = (file: File, type: 'mysql' | 'postgresql') => {
  if (type === 'mysql') {
    editForm.value.mysql_file = file

    // 读取MySQL文件内容并显示
    const reader = new FileReader()
    reader.onload = (e) => {
      editMysqlFileContent.value = e.target?.result as string
    }
    reader.onerror = () => {
      ElMessage.error('MySQL文件读取失败')
    }
    reader.readAsText(file)
  } else if (type === 'postgresql') {
    editForm.value.postgresql_file = file

    // 读取PostgreSQL文件内容并显示
    const reader = new FileReader()
    reader.onload = (e) => {
      editPostgresqlFileContent.value = e.target?.result as string
    }
    reader.onerror = () => {
      ElMessage.error('PostgreSQL文件读取失败')
    }
    reader.readAsText(file)
  }

  return false // 阻止自动上传
}

// 创建数据库模式
const createSchema = async () => {
  if (!createFormRef.value) return

  try {
    await createFormRef.value.validate()

    // 检查是否上传了两个文件
    if (!createForm.value.mysql_file) {
      ElMessage.error('请上传MySQL建表文件')
      return
    }
    if (!createForm.value.postgresql_file) {
      ElMessage.error('请上传PostgreSQL/OpenGauss建表文件')
      return
    }

    createLoading.value = true

    // 读取MySQL文件内容为字符串
    const mysqlFileContent = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        resolve(e.target?.result as string)
      }
      reader.onerror = reject
      reader.readAsText(createForm.value.mysql_file!)
    })

    // 读取PostgreSQL文件内容为字符串
    const postgresqlFileContent = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        resolve(e.target?.result as string)
      }
      reader.onerror = reject
      reader.readAsText(createForm.value.postgresql_file!)
    })

    const requestData = {
      schema_description: createForm.value.html_content,
      schema_name: createForm.value.schema_name,
      sql_file_content: {
        mysql_engine: mysqlFileContent,
        postgresql_opengauss_engine: postgresqlFileContent,
      },
      sql_schema: createForm.value.sql_schema,
      schema_author: teacherInfo.value.teacher_name || '',
    }

    const response = await axios.post('/teacher/schema/create', requestData, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.data && response.data.code === 200) {
      ElMessage.success('数据库模式创建成功')
      createDialogVisible.value = false
      // 重新获取模式列表
      await fetchSchemaList()
    } else {
      ElMessage.error(response.data?.msg || '创建失败')
    }
  } catch (error) {
    console.error('创建数据库模式失败:', error)
    ElMessage.error('创建数据库模式失败')
  } finally {
    createLoading.value = false
  }
}

// 获取可见性标签类型
const getVisibilityTagType = (status: number) => {
  return status === 1 ? 'success' : 'danger'
}

// 获取可见性文本
const getVisibilityText = (status: number) => {
  return status === 1 ? '完全可见' : '不可见'
}

// 获取数据库类型标签颜色

// 进入编辑模式
const enterEditMode = () => {
  if (!selectedSchemaInfo.value) return

  isEditMode.value = true
  editForm.value = {
    schema_id: selectedSchemaInfo.value.schema_id,
    html_content: selectedSchemaInfo.value.schema_description || '', // 加载完整的HTML内容，不去除任何标签
    schema_name: selectedSchemaInfo.value.schema_name,
    mysql_file: null,
    postgresql_file: null,
    sql_schema: selectedSchemaInfo.value.schema_name, // 默认使用schema_name
  }
  // 重置文件内容显示
  editMysqlFileContent.value = ''
  editPostgresqlFileContent.value = ''
}

// 取消编辑
const cancelEdit = () => {
  isEditMode.value = false
  editForm.value = {
    schema_id: 0,
    html_content: '',
    schema_name: '',
    mysql_file: null,
    postgresql_file: null,
    sql_schema: '',
  }
  // 重置文件内容显示
  editMysqlFileContent.value = ''
  editPostgresqlFileContent.value = ''
}

// 保存修改（先删除再创建）
const saveChanges = async () => {
  if (!selectedSchemaInfo.value) return

  try {
    // 检查是否上传了两个文件（如果要更新SQL文件的话）
    const hasNewFiles = editForm.value.mysql_file || editForm.value.postgresql_file
    if (hasNewFiles && (!editForm.value.mysql_file || !editForm.value.postgresql_file)) {
      ElMessage.error('如果要更新SQL文件，请同时上传MySQL和PostgreSQL/OpenGauss两种文件')
      return
    }

    editLoading.value = true

    // 第一步：删除原有模式
    const deleteResponse = await axios.delete(`/teacher/schemas/${editForm.value.schema_id}`)

    if (!deleteResponse.data || !deleteResponse.data.success) {
      ElMessage.error('删除原模式失败')
      return
    }

    // 第二步：准备创建新模式的数据
    let sqlFileContent: any

    if (hasNewFiles) {
      // 如果有新文件，读取新文件内容
      const mysqlContent = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target?.result as string)
        reader.onerror = reject
        reader.readAsText(editForm.value.mysql_file!)
      })

      const postgresqlContent = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target?.result as string)
        reader.onerror = reject
        reader.readAsText(editForm.value.postgresql_file!)
      })

      sqlFileContent = {
        mysql_engine: mysqlContent,
        postgresql_opengauss_engine: postgresqlContent,
      }
    } else {
      // 如果没有新文件，使用原有的文件内容（这里需要从原模式中获取）
      // 注意：这里假设原模式的SQL文件内容可以从某个地方获取
      // 实际实现中可能需要先获取原模式的完整信息
      ElMessage.warning('未上传新的SQL文件，将保持原有文件不变')
      // 这里可能需要调用API获取原有的SQL文件内容
      // 为了简化，我们要求用户必须上传新文件
      ElMessage.error('编辑模式下必须重新上传SQL文件')
      return
    }

    // 第三步：创建新模式
    const createData = {
      schema_description: editForm.value.html_content,
      schema_name: editForm.value.schema_name,
      sql_file_content: sqlFileContent,
      sql_schema: editForm.value.sql_schema,
      schema_author: teacherInfo.value.teacher_name || '',
    }

    const createResponse = await axios.post('/teacher/schema/create', createData, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (createResponse.data && createResponse.data.code === 200) {
      ElMessage.success('数据库模式修改成功')

      // 退出编辑模式
      isEditMode.value = false

      // 清空选中状态，因为原模式已被删除
      selectedSchema.value = ''
      selectedSchemaInfo.value = null

      // 重新获取模式列表
      await fetchSchemaList()
    } else {
      ElMessage.error(createResponse.data?.msg || '创建新模式失败')
    }
  } catch (error) {
    console.error('修改数据库模式失败:', error)
    ElMessage.error('修改数据库模式失败')
  } finally {
    editLoading.value = false
  }
}

// 删除数据库模式
const deleteSchema = async (schema: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据库模式 "${schema.schema_name}" 吗？\n\n注意：如果该模式下存在题目，需要先删除所有相关题目。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
      },
    )

    deleteLoading.value = schema.schema_id

    const response = await axios.delete(`/teacher/schemas/${schema.schema_id}`)

    if (response.data && response.data.success) {
      ElMessage.success(response.data.message || '数据库模式删除成功')

      // 如果删除的是当前选中的模式，清空选中状态
      if (selectedSchema.value === schema.schema_name) {
        selectedSchema.value = ''
        selectedSchemaInfo.value = null
      }

      // 重新获取模式列表
      await fetchSchemaList()
    } else {
      ElMessage.error(response.data?.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除数据库模式失败:', error)
      ElMessage.error('删除数据库模式失败')
    }
  } finally {
    deleteLoading.value = null
  }
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
.schema-wrapper {
  display: grid;
  grid-template-columns: 250px;
  height: 100%;
  gap: 0;
}

.schema-wrapper.has-selection {
  grid-template-columns: 250px 200px 1fr;
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

.header-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

.title-with-spacing {
  letter-spacing: 2px;
  white-space: nowrap;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  color: #606266;
  font-size: 18px;
  padding: 4px;
}

.back-btn:hover {
  color: #409eff;
}

.create-btn {
  font-size: 14px;
  padding: 8px 16px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.schema-content {
  flex: 1;
}

.schema-actions {
  margin-left: 12px;
}

.schema-visibility {
  margin-top: 8px;
}

/* 状态信息说明 */
.visibility-info {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;
}

.visibility-info h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.visibility-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.visibility-option {
  padding: 8px;
  background-color: #ffffff;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.option-desc {
  margin: 4px 0 0 24px;
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}

/* 中间面板 - 选项按钮 */
.middle-panel {
  padding: 20px;
}

.option-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  width: 100%;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
}

/* 右侧面板 - 内容区域 */
.right-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.content-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.content-panel .panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-actions {
  display: flex;
  gap: 8px;
}

/* 基本信息内容 */
.basic-info-content {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.schema-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.schema-header .author {
  margin: 0 0 20px 0;
  color: #606266;
  font-size: 14px;
}

.schema-description h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.description-viewer {
  width: 100%;
  height: 300px;
  padding: 0;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow-y: auto;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.description-viewer.expanded {
  height: 390px; /* 扩展30%：300px * 1.3 = 390px */
}

/* 数据库模式状态 */
.schema-status {
  margin-top: 24px;
}

.schema-status h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.status-item {
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.status-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.status-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.status-value.active {
  color: #67c23a;
}

/* 数据库连接信息 */
.connection-info {
  margin-top: 24px;
}

.connection-info h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.connection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.connection-item {
  padding: 12px 16px;
  background-color: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #d9ecff;
}

.connection-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.connection-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.connection-value.connected {
  color: #67c23a;
}

/* 查询面板内容 */
.query-content {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.sql-editor {
  margin-bottom: 20px;
}

.sql-textarea {
  font-family: 'Courier New', monospace;
}

.results-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.results-info {
  font-size: 14px;
  color: #606266;
}

.no-results {
  padding: 40px 20px;
  text-align: center;
}

.results-table {
  flex: 1;
  overflow: hidden;
}

.query-table {
  height: 100%;
}

/* 占位内容 */
.placeholder-content {
  padding: 40px 20px;
  text-align: center;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 编辑模式样式 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.edit-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.schema-name-input {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.description-editor {
  margin-top: 16px;
}

.description-pagination {
  margin-top: 16px;
  text-align: center;
}

.edit-config {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.config-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.config-item {
  margin-bottom: 16px;
}

.config-item h4 {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 600;
}

.sql-file-upload {
  margin-top: 8px;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .schema-wrapper.has-selection {
    grid-template-columns: 200px 160px 1fr;
  }
}

@media (max-width: 768px) {
  .schema-wrapper {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .schema-wrapper.has-selection {
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

  .option-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .option-btn {
    width: calc(50% - 6px);
  }

  .content-panel .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .results-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}

/* 创建数据库模式对话框样式 */
.create-schema-dialog .el-dialog__body {
  padding: 20px 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 16px;
}

.form-col {
  display: flex;
  flex-direction: column;
}

.sql-content-display {
  margin-top: 8px;
}

.sql-content-textarea {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.sql-content-textarea .el-textarea__inner {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #495057;
}

.html-editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  resize: horizontal;
  min-width: 750px;
  max-width: 100%;
}

.html-editor-header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  padding: 8px 12px;
}

.editor-tabs {
  display: flex;
  gap: 8px;
}

.html-editor-content {
  min-height: 400px;
}

.split-view {
  display: flex;
  height: 100%;
}

.editor-panel.half {
  flex: 2;
  border-right: 1px solid #dcdfe6;
}

.preview-panel.half {
  flex: 1;
  border-right: 1px solid #dcdfe6;
}

.preview-panel.half {
  border-right: none;
  border-left: 1px solid #dcdfe6;
}

.editor-panel.full,
.preview-panel.full {
  width: 100%;
  height: 100%;
}

.panel-title {
  background-color: #f8f9fa;
  padding: 8px 12px;
  border-bottom: 1px solid #e9ecef;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.html-code-editor {
  font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.html-code-editor .el-textarea__inner {
  font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
  border: none;
  border-radius: 0;
  resize: none;
}

.html-preview {
  padding: 12px;
  min-height: 300px;
  background-color: #fff;
  overflow-y: auto;
  border: none;
}

.html-preview h1,
.html-preview h2,
.html-preview h3,
.html-preview h4,
.html-preview h5,
.html-preview h6 {
  margin-top: 0;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.html-preview p {
  margin-bottom: 16px;
  line-height: 1.6;
}

.html-preview ul,
.html-preview ol {
  margin-bottom: 16px;
  padding-left: 24px;
}

.html-preview li {
  margin-bottom: 4px;
}

.html-preview code {
  background-color: #f6f8fa;
  border-radius: 3px;
  font-size: 85%;
  margin: 0;
  padding: 0.2em 0.4em;
}

.html-preview pre {
  background-color: #f6f8fa;
  border-radius: 6px;
  font-size: 85%;
  line-height: 1.45;
  overflow: auto;
  padding: 16px;
  margin-bottom: 16px;
}

.html-editor-container .ql-toolbar {
  border-bottom: 1px solid #dcdfe6;
  background-color: #fafafa;
}

.html-editor-container .ql-container {
  border: none;
  font-size: 14px;
}

.sql-file-upload .el-upload-dragger {
  width: 100%;
  height: 120px;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.sql-file-upload .el-upload-dragger:hover {
  border-color: #409eff;
}

.sql-file-upload .el-upload-dragger .el-icon--upload {
  font-size: 28px;
  color: #8c939d;
  margin-bottom: 16px;
}

.sql-file-upload .el-upload__text {
  color: #606266;
  font-size: 14px;
  text-align: center;
}

.sql-file-upload .el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 7px;
}

@media (max-width: 768px) {
  .create-schema-dialog {
    width: 95% !important;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
