# SQL在线平台 API

基于 FastAPI 框架开发的 SQL 在线学习平台后端 API，支持多角色用户管理、SQL 题库管理、在线答题和学习成果分析。

## 🚀 项目特性

- **多角色用户系统**：支持管理员、教师、学生三种角色
- **JWT 身份认证**：安全的用户认证和授权机制
- **SQL 题库管理**：支持题目创建、编辑和管理
- **在线答题系统**：实时 SQL 语句执行和结果验证
- **学习成果分析**：答题记录统计和排名系统
- **多数据库支持**：支持 MySQL、PostgreSQL、openGauss 等数据库引擎
- **RESTful API**：标准化的 API 接口设计
- **自动化文档**：集成 Swagger UI 和 ReDoc

## 📋 功能模块

### 管理员功能
- 用户登录和身份认证
- 学期管理（创建、更新、删除、查询）
- 教师账号管理（创建、更新、删除、查询）
- 学生账号管理（创建、更新、删除、查询）
- 数据库模式管理
- 系统数据面板和态势矩阵
- 密码修改

### 教师功能
- 用户登录和身份认证
- 学生选课记录导入
- 成绩核算和导出
- 数据面板查看
- 态势矩阵分析
- 密码修改

### 学生功能
- 用户登录和身份认证
- 个人信息查看
- 数据库模式选择
- 题目浏览和答题
- 答题记录查询
- 排名查看和分析
- 密码修改

## 🛠️ 技术栈

- **后端框架**：FastAPI 0.104.1
- **数据库**：MySQL（主要）+ SQLAlchemy ORM
- **身份认证**：JWT (JSON Web Tokens)
- **密码加密**：Passlib + Bcrypt
- **API 文档**：Swagger UI / ReDoc
- **异步支持**：Uvicorn ASGI 服务器
- **数据验证**：Pydantic
- **跨域支持**：CORS 中间件

## 📦 项目结构

```
fastApiProject/
├── app/
│   ├── controllers/          # 控制器层
│   │   ├── auth_controller.py      # 认证控制器
│   │   ├── admin_controller.py     # 管理员控制器
│   │   └── student_controller.py   # 学生控制器
│   ├── models/              # 数据模型层
│   │   ├── student.py             # 学生模型
│   │   ├── teacher.py             # 教师模型
│   │   ├── semester.py            # 学期模型
│   │   ├── course.py              # 课程模型
│   │   ├── problem.py             # 题目模型
│   │   └── answer_record.py       # 答题记录模型
│   ├── services/            # 业务逻辑层
│   │   ├── auth_service.py        # 认证服务
│   │   ├── admin_service.py       # 管理员服务
│   │   ├── student_service.py     # 学生服务
│   │   └── user_management_service.py  # 用户管理服务
│   ├── schemas/             # 数据模式定义
│   │   ├── auth.py               # 认证相关模式
│   │   ├── admin.py              # 管理员相关模式
│   │   └── student.py            # 学生相关模式
│   ├── scripts/             # 脚本文件
│   ├── tests/               # 测试文件
│   ├── docs/                # 文档文件
│   ├── main.py              # 应用入口文件
│   ├── requirements.txt     # 依赖包列表
│   └── config.md            # 配置说明
└── README.md                # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ 或 8.0+
- pip 或 conda

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd fastApiProject
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   cd app
   pip install -r requirements.txt
   ```

4. **配置环境变量**

   在 `app` 目录下创建 `.env` 文件：
   ```env
   # 数据库配置
   SQLALCHEMY_DATABASE_URL=mysql+pymysql://username:password@localhost:3306/database_name

   # JWT配置
   JWT_SECRET_KEY=your-super-secret-jwt-key-here-please-change-in-production
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # 应用配置
   APP_HOST=0.0.0.0
   APP_PORT=8000
   DEBUG=True
   ```

5. **初始化数据库**
   ```bash
   python -c "from models.database import create_tables; create_tables()"
   ```

6. **启动应用**
   ```bash
   python main.py
   ```

   或使用 uvicorn：
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 访问应用

- **API 文档 (Swagger UI)**：http://localhost:8000/docs
- **API 文档 (ReDoc)**：http://localhost:8000/redoc
- **根路径**：http://localhost:8000/ （自动重定向到 API 文档）

## 🔐 默认账号

### 管理员账号
- **用户名**：`admin`
- **密码**：`admin123`
- **角色**：`admin`

### 教师账号
- **用户名**：教师ID（在数据库中创建）
- **密码**：数据库中的 `teacher_password` 字段
- **角色**：`teacher`

### 学生账号
- **用户名**：学生ID（学号）
- **密码**：数据库中的 `student_password` 字段
- **角色**：`student`

## 📚 API 接口说明

### 认证接口
- `POST /login` - 用户登录
- `POST /update-password` - 修改密码

### 管理员接口
- `POST /admin/semesters` - 创建学期
- `GET /admin/semesters` - 获取学期列表
- `PUT /admin/semesters/{semester_id}` - 更新学期
- `DELETE /admin/semesters/{semester_id}` - 删除学期
- `POST /admin/teachers` - 创建教师
- `GET /admin/teachers` - 获取教师列表
- `PUT /admin/teachers/{teacher_id}` - 更新教师信息
- `DELETE /admin/teachers/{teacher_id}` - 删除教师
- `POST /admin/students` - 创建学生
- `GET /admin/students` - 获取学生列表
- `PUT /admin/students/{student_id}` - 更新学生信息
- `DELETE /admin/students/{student_id}` - 删除学生

### 学生接口
- `GET /student/profile` - 获取学生个人信息
- `GET /student/rank` - 获取学生排名
- `POST /student/answer/submit` - 提交答题
- `GET /student/answer/records` - 获取答题记录

## 🗄️ 数据库设计

### 核心数据表

#### 学生表 (student)
- `id` - 主键，自增ID
- `student_id` - 学生ID（学号）
- `student_name` - 学生姓名
- `class` - 班级
- `student_password` - 学生密码

#### 教师表 (teacher)
- `id` - 主键，自增ID
- `teacher_id` - 教师ID
- `teacher_name` - 教师姓名
- `teacher_password` - 教师密码

#### 学期表 (semester)
- `semester_id` - 主键，学期ID
- `semester_name` - 学期名称
- `date_id` - 外键，关联日期范围表

#### 题目表 (problem)
- `problem_id` - 主键，题目ID
- `database_schema_id` - 外键，数据库模式ID
- `problem_content` - 题目内容
- `is_required` - 是否必做题

#### 答题记录表 (answer_record)
- `student_id` - 外键，学生ID
- `problem_id` - 外键，题目ID
- `answer_content` - 答题内容
- `result_type` - 结果类型（0:正确 1:语法错误 2:结果错误）
- `method_count` - 方法数，新方法时递增
- `timestep` - 操作时间戳

## 🧪 测试

### 运行测试
```bash
cd app
python -m pytest tests/ -v
```

### 测试覆盖率
```bash
pip install pytest-cov
python -m pytest tests/ --cov=. --cov-report=html
```

## 🚀 部署

### Docker 部署（推荐）

1. **创建 Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY app/requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY app/ .

   EXPOSE 8000

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **创建 docker-compose.yml**
   ```yaml
   version: '3.8'

   services:
     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - SQLALCHEMY_DATABASE_URL=mysql+pymysql://root:password@db:3306/sql_platform
       depends_on:
         - db

     db:
       image: mysql:8.0
       environment:
         MYSQL_ROOT_PASSWORD: password
         MYSQL_DATABASE: sql_platform
       ports:
         - "3306:3306"
       volumes:
         - mysql_data:/var/lib/mysql

   volumes:
     mysql_data:
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

### 传统部署

1. **安装依赖**
   ```bash
   pip install -r app/requirements.txt
   ```

2. **配置环境变量**
   ```bash
   export SQLALCHEMY_DATABASE_URL="mysql+pymysql://user:pass@localhost/dbname"
   export JWT_SECRET_KEY="your-secret-key"
   ```

3. **启动服务**
   ```bash
   cd app
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

## 🔧 开发指南

### 代码结构说明

- **controllers/**: 控制器层，处理 HTTP 请求和响应
- **services/**: 业务逻辑层，包含核心业务逻辑
- **models/**: 数据模型层，定义数据库表结构
- **schemas/**: 数据模式层，定义请求和响应的数据结构
- **scripts/**: 工具脚本，如数据库初始化脚本

### 开发规范

1. **代码风格**: 遵循 PEP 8 规范
2. **类型注解**: 使用 Python 类型注解
3. **文档字符串**: 为函数和类添加详细的文档字符串
4. **错误处理**: 统一的异常处理机制
5. **日志记录**: 合理使用日志记录

### 添加新功能

1. 在 `models/` 中定义数据模型
2. 在 `schemas/` 中定义请求/响应模式
3. 在 `services/` 中实现业务逻辑
4. 在 `controllers/` 中添加 API 端点
5. 在 `main.py` 中注册路由
6. 编写相应的测试用例

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

---

**注意**: 本项目仅用于学习和教育目的，请勿用于生产环境而不进行适当的安全配置和测试。

- **起止日期id** `undefined`（主键，外键 → 起止日期表）
- **学期id** `integer`（主键，外键 → 学期表）
- **课序号** `integer`（主键）
- **课名** `char(256)`

---
### 学生表

- **学号** `integer`（主键）
- **学生姓名** `char(256)`
- **班级** `char(256)`
- **学生密码** `char(256)`

---

  ### 教师表

- **教职工号** `integer`（主键）
- **教师姓名** `char(256)`
- **教师密码** `char(256)`

---

 ### 学期表

- **起止日期id** `undefined`（主键，外键 → 起止日期表）
- **学期id** `integer`（主键）
- **学期名称** `char(256)`

---

### 起止日期表

- **起止日期id** `undefined`（主键）
- **起始日期** `date`
- **终止日期** `date`

---

 ### 选课表

- **学号** `integer`（主键，外键 → 学生表）
- **起止日期id** `undefined`（主键）
- **学期id** `integer`（主键）
- **课序号** `integer`（主键）

---

 ### 上课表

- **教职工号** `integer`（主键，外键 → 教师表）
- **起止日期id** `undefined`（主键）
- **学期id** `integer`（主键）
- **课序号** `integer`（主键）

---

### 答题表

- **学号** `integer`（主键）
- **题目id** `integer`（主键）

---

 ### 数据库模式表

- **模式id** `integer`（主键）
- **描述** `char(256)`

# PowerDesigner设计
### 概念逻辑图
![alt text](image.png)

### 物理逻辑图
![alt text](image-1.png)

## 基于Mysql的数据库
![alt text](image-2.png)

## 技术架构
Python FastAPI + VUE + PostgreSQL（Mysql，OpenGauss）

MVC三层架构，遵循RESTful API风格，就是一套协议来规范多种形式的前端和同一个后台的交互方式。

前端Tailwind CSS组件

ECharts数据可视化

SQL执行：后端接受前端的SQL代码，并根据前端选择的不同环境（Mysql，PostgreSQL和OpenGauss）执行，并把结果返回给前端



## api接口设计
### 登录
* POST http://api/login/
* 返回JWT令牌的TOKEN
### 


# SQL在线测试平台 API接口设计

## 基础信息
- 基础URL: `http://api/v1`
- 认证方式: JWT Token
- 请求格式: JSON
- 响应格式: JSON

## 通用响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 1. 认证相关接口

### 1.1 用户登录
- **接口**: `POST /auth/login`
- **说明**: 用户登录获取JWT令牌
- **请求参数**:
```json
{
  "username": "string",  // 用户名（学号/教职工号/admin）
  "password": "string",  // 密码
  "role": "string"       // 角色类型：admin/teacher/student
}
```
- **响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "string",
      "username": "string",
      // "name": "string",
      "role": "string"
    }
  }
}
```

### 1.2 修改密码
- **接口**: `PUT /auth/password`
- **说明**: 修改用户密码
- **请求参数**:
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

### 1.3 登出
- **接口**: `POST /auth/logout`
- **说明**: 用户登出

## 2. 用户管理接口

### 2.1 学生管理

#### 2.1.1 获取学生列表
- **接口**: `GET /users/students`
- **说明**: 获取学生列表（支持分页和筛选）
- **查询参数**:
  - `page`: 页码（默认1）
  - `limit`: 每页数量（默认20）
  - `class_name`: 班级筛选
  - `semester_id`: 学期筛选

#### 2.1.2 创建学生账号
- **接口**: `POST /users/students`
- **说明**: 创建新学生账号
- **请求参数**:
```json
{
  "student_id": "string",    // 学号
  "name": "string",          // 姓名
  "class_name": "string",    // 班级
  "password": "string",      // 密码
  "semester_id": "string",   // 当前学期
  "course_id": "string",     // 课序号
  "teacher_id": "string"     // 任课老师ID
}
```

#### 2.1.3 更新学生信息
- **接口**: `PUT /users/students/{student_id}`
- **说明**: 更新学生信息

#### 2.1.4 删除学生
- **接口**: `DELETE /users/students/{student_id}`
- **说明**: 删除学生账号

#### 2.1.5 导入学生选课记录
- **接口**: `POST /users/students/import`
- **说明**: 批量导入学生选课记录
- **请求参数**: 文件上传（Excel/CSV）

### 2.2 教师管理

#### 2.2.1 获取教师列表
- **接口**: `GET /users/teachers`
- **说明**: 获取教师列表

#### 2.2.2 创建教师账号
- **接口**: `POST /users/teachers`
- **说明**: 创建新教师账号
- **请求参数**:
```json
{
  "teacher_id": "string",    // 教职工号
  "name": "string",          // 姓名
  "password": "string",      // 密码
  "semester_id": "string"    // 当前学期
}
```

#### 2.2.3 更新教师信息
- **接口**: `PUT /users/teachers/{teacher_id}`
- **说明**: 更新教师信息

#### 2.2.4 删除教师
- **接口**: `DELETE /users/teachers/{teacher_id}`
- **说明**: 删除教师账号

## 3. 学期管理接口

### 3.1 获取学期列表
- **接口**: `GET /semesters`
- **说明**: 获取所有学期列表

### 3.2 创建学期
- **接口**: `POST /semesters`
- **说明**: 创建新学期
- **请求参数**:
```json
{
  "name": "string",          // 学期名称
  "start_date": "string",    // 开始日期
  "end_date": "string"       // 结束日期
}
```

### 3.3 更新学期
- **接口**: `PUT /semesters/{semester_id}`
- **说明**: 更新学期信息

### 3.4 删除学期
- **接口**: `DELETE /semesters/{semester_id}`
- **说明**: 删除学期

## 4. 数据库模式管理接口

### 4.1 获取数据库模式列表
- **接口**: `GET /database-schemas`
- **说明**: 获取所有数据库模式

### 4.2 创建数据库模式
- **接口**: `POST /database-schemas`
- **说明**: 创建新的数据库模式
- **请求参数**:
```json
{
  "name": "string",          // 模式名称
  "description": "string"    // 模式描述（HTML格式）
}
```

### 4.3 上传数据库模式描述
- **接口**: `POST /database-schemas/{schema_id}/upload`
- **说明**: 上传数据库模式描述文件（HTML）
- **请求参数**: 文件上传

### 4.4 更新数据库模式
- **接口**: `PUT /database-schemas/{schema_id}`
- **说明**: 更新数据库模式信息

### 4.5 删除数据库模式
- **接口**: `DELETE /database-schemas/{schema_id}`
- **说明**: 删除数据库模式

### 4.6 获取数据库模式详情
- **接口**: `GET /database-schemas/{schema_id}`
- **说明**: 获取数据库模式详细信息

## 5. 题目管理接口

### 5.1 获取题目列表
- **接口**: `GET /questions`
- **说明**: 获取题目列表
- **查询参数**:
  - `schema_id`: 数据库模式ID
  - `is_required`: 是否必做题
  - `page`: 页码
  - `limit`: 每页数量

### 5.2 创建题目
- **接口**: `POST /questions`
- **说明**: 创建新题目
- **请求参数**:
```json
{
  "schema_id": "string",     // 数据库模式ID
  "content": "string",       // 题目内容
  "is_required": "boolean",  // 是否必做题
  "standard_sql": "string",  // 标准SQL答案
  "expected_result": "array" // 期望结果
}
```

### 5.3 更新题目
- **接口**: `PUT /questions/{question_id}`
- **说明**: 更新题目信息

### 5.4 删除题目
- **接口**: `DELETE /questions/{question_id}`
- **说明**: 删除题目

### 5.5 获取题目详情
- **接口**: `GET /questions/{question_id}`
- **说明**: 获取题目详细信息

## 6. SQL执行和答题接口

### 6.1 执行SQL语句
- **接口**: `POST /sql/execute`
- **说明**: 执行SQL语句并返回结果
- **请求参数**:
```json
{
  "sql": "string",           // SQL语句
  "database_type": "string", // 数据库类型：mysql/postgresql/opengauss
  "schema_id": "string"      // 数据库模式ID
}
```
- **响应**:
```json
{
  "code": 200,
  "message": "执行成功",
  "data": {
    "columns": ["column1", "column2"],
    "rows": [
      ["value1", "value2"],
      ["value3", "value4"]
    ],
    "execution_time": 0.05,
    "row_count": 2
  }
}
```

### 6.2 提交答案
- **接口**: `POST /answers`
- **说明**: 学生提交题目答案
- **请求参数**:
```json
{
  "question_id": "string",   // 题目ID
  "sql": "string",           // 学生提交的SQL
  "database_type": "string"  // 使用的数据库类型
}
```

### 6.3 获取答题记录
- **接口**: `GET /answers`
- **说明**: 获取答题记录
- **查询参数**:
  - `student_id`: 学生ID（可选）
  - `question_id`: 题目ID（可选）
  - `page`: 页码
  - `limit`: 每页数量

### 6.4 获取答题详情
- **接口**: `GET /answers/{answer_id}`
- **说明**: 获取答题详细信息

## 7. 数据统计和分析接口

### 7.1 获取数据面板
- **接口**: `GET /dashboard`
- **说明**: 获取数据面板统计信息
- **响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_students": 100,
    "total_questions": 50,
    "total_answers": 1000,
    "correct_rate": 0.75,
    "recent_activities": []
  }
}
```

### 7.2 获取态势矩阵
- **接口**: `GET /analytics/matrix`
- **说明**: 获取态势矩阵数据
- **查询参数**:
  - `semester_id`: 学期ID
  - `class_name`: 班级名称

### 7.3 获取排名
- **接口**: `GET /rankings`
- **说明**: 获取学生排名
- **查询参数**:
  - `semester_id`: 学期ID
  - `class_name`: 班级名称
  - `limit`: 排名数量

### 7.4 获取答题情况分析
- **接口**: `GET /analytics/answers`
- **说明**: 获取答题情况分析
- **查询参数**:
  - `student_id`: 学生ID
  - `question_id`: 题目ID
  - `time_range`: 时间范围

### 7.5 核算分数并导出
- **接口**: `POST /analytics/scores/export`
- **说明**: 教师核算学生分数并导出
- **请求参数**:
```json
{
  "semester_id": "string",
  "class_name": "string",
  "format": "string"  // 导出格式：excel/csv
}
```

## 8. 选课记录管理接口

### 8.1 获取选课记录
- **接口**: `GET /course-records`
- **说明**: 获取选课记录列表

### 8.2 创建选课记录
- **接口**: `POST /course-records`
- **说明**: 创建选课记录
- **请求参数**:
```json
{
  "student_id": "string",    // 学号
  "student_name": "string",  // 学生姓名
  "class_name": "string",    // 班级
  "teacher_name": "string"   // 教师姓名
}
```

### 8.3 更新选课记录
- **接口**: `PUT /course-records/{record_id}`
- **说明**: 更新选课记录

### 8.4 删除选课记录
- **接口**: `DELETE /course-records/{record_id}`
- **说明**: 删除选课记录

## 9. 数据库引擎管理接口

### 9.1 获取支持的数据库引擎
- **接口**: `GET /database-engines`
- **说明**: 获取系统支持的数据库引擎列表

### 9.2 测试数据库连接
- **接口**: `POST /database-engines/test`
- **说明**: 测试数据库连接
- **请求参数**:
```json
{
  "engine_type": "string",   // 引擎类型
  "host": "string",          // 主机地址
  "port": "integer",         // 端口
  "database": "string",      // 数据库名
  "username": "string",      // 用户名
  "password": "string"       // 密码
}
```

## 10. 错误码定义

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 1001 | 用户名或密码错误 |
| 1002 | 用户不存在 |
| 1003 | 用户已存在 |
| 2001 | SQL执行错误 |
| 2002 | 数据库连接失败 |
| 3001 | 文件上传失败 |
| 3002 | 文件格式不支持 |

## 11. 权限控制

### 管理员权限
- 所有用户管理接口
- 学期管理接口
- 数据库模式管理接口
- 题目管理接口
- 数据统计接口

### 教师权限
- 学生管理接口（查看、导入）
- 答题记录查看接口
- 数据统计接口
- 分数核算和导出接口

### 学生权限
- 题目查看接口
- SQL执行接口
- 答题接口
- 个人数据查看接口
- 排名查看接口

## 12. 接口调用示例

### 登录示例
```bash
curl -X POST http://api/v1/auth/login \
-H "Content-Type: application/json" \
-d '{
  "username": "20230001",
  "password": "123456",
  "role": "student"
}'
```

### 执行SQL示例
```bash
curl -X POST http://api/v1/sql/execute \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_TOKEN" \
-d '{
  "sql": "SELECT * FROM users LIMIT 10",
  "database_type": "postgresql",
  "schema_id": "schema_001"
}'
```

### 提交答案示例
```bash
curl -X POST http://api/v1/answers \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_TOKEN" \
-d '{
  "question_id": "q001",
  "sql": "SELECT name, age FROM students WHERE age > 18",
  "database_type": "mysql"
}'
``` 
