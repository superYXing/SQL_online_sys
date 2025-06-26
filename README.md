## 题目：
题目描述：基于python及FastAPI框架，实现SQL在线测试平台，主要功能用户管理（包含管理员、教师、学生三种角色）、SQL题库管理、SQL在线答题管理、学习成果分析，支持创建sql查询题目、测试sql语句的准确性、对答题情况进行可视化分析等。
具体包括：
（1）功能要求，参考原型图
（2）系统数据库使用Mysql
（3）支持添加并切换使用不同的数据库引擎进行sql测试（包括PostgreSQL、MySQL、openGauss等）
技术要求：Python、FastAPI、PostgreSQL

## 功能分析
* 管理员：登录，管理账号，学期管理，添加教师，添加学期，查询面板，上传数据库模式描述信息（html格式），添加数据库模式，查看数据面板，查看态势矩阵，修改密码
  
* 教师：登录，导入学生选课记录，核算分数并导出，查看数据面板，查看态势矩阵，修改密码
  
* 学生：登录，查看数据面板（答题情况），选择数据库模式，查看题目，答题，查看排名，答题情况分析，修改密码
## 数据库


###   题目表

- **题目id** `integer`（主键）
- **数据库模式id** `integer`（外键 → 数据库模式表.模式id）
- **题目内容** `char(256)`
- **是否必做题** `smallint`

---

  ### 学生答题表

- **学号** `integer`（主键，外键 → 学生表.学号）
- **题目id** `integer`（主键，外键 → 题目表.题目id）
- **答题id** `undefined`
- **是否正确** `undefined`

---

  ### 课程表

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
