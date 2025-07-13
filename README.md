# SQL在线实践平台

一个基于FastAPI和Vue.js的现代化SQL在线学习与实践平台，为数据库课程教学提供完整的解决方案。系统网址：http://wyaaa.gnway.cc

## 🚀 项目简介

SQL在线实践平台是一个专为数据库课程设计的在线教学平台，支持学生在线练习SQL语句，教师管理题目和学生，以及智能化的学习分析功能。平台提供了完整的用户管理、题目管理、在线SQL执行、AI智能分析等功能模块。

## ✨ 主要功能

### 👨‍🎓 学生功能
- **在线SQL练习**: 支持多种数据库引擎（MySQL、PostgreSQL、openGauss）
- **实时代码执行**: 即时查看SQL执行结果
- **AI智能分析**: 获得SQL语句的智能分析和优化建议
- **学习进度跟踪**: 查看个人学习进度和答题记录
- **多课程支持**: 支持多学期、多课程的学习管理

### 👨‍🏫 教师功能
- **题目管理**: 创建、编辑、删除SQL练习题目
- **学生管理**: 管理学生信息和学习进度
- **数据库模式管理**: 创建和管理教学用数据库模式
- **AI教学分析**: 智能分析学生知识点掌握情况
- **学习数据统计**: 查看学生答题统计和学习分析

### 👨‍💼 管理员功能
- **用户管理**: 管理教师和学生账户
- **课程管理**: 创建和管理课程、学期信息
- **系统监控**: 实时监控系统运行状态
- **数据库管理**: 管理多种数据库连接和配置

## 🏗️ 系统架构

### 技术架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue.js)  │    │  后端 (FastAPI)  │    │   数据库集群     │
│                 │    │                 │    │                 │
│ • Vue 3         │◄──►│ • FastAPI       │◄──►│ • MySQL         │
│ • TypeScript    │    │ • SQLAlchemy    │    │ • PostgreSQL    │
│ • Element Plus  │    │ • Pydantic      │    │ • openGauss     │
│ • Vite          │    │ • JWT Auth      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI服务集成     │
                    │                 │
                    │ • 智能SQL分析    │
                    │ • 学习建议生成   │
                    │ • 知识点评估     │
                    └─────────────────┘
```

### 模块架构
- **认证模块**: JWT令牌认证，支持学生、教师、管理员三种角色
- **用户管理**: 完整的用户生命周期管理
- **题目系统**: 灵活的题目创建和管理系统
- **SQL执行引擎**: 支持多种数据库的安全SQL执行
- **AI分析服务**: 集成AI能力，提供智能学习分析
- **监控系统**: 实时系统监控和日志管理

## 🛠️ 技术栈

### 后端技术
- **框架**: FastAPI 0.104+
- **数据库ORM**: SQLAlchemy 2.0+
- **数据验证**: Pydantic 2.0+
- **认证**: JWT (PyJWT)
- **数据库**: MySQL, PostgreSQL, openGauss
- **异步支持**: asyncio, uvicorn
- **日志系统**: Python logging

### 前端技术
- **框架**: Vue.js 3.x
- **语言**: TypeScript
- **UI组件**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4

### 开发工具
- **API文档**: Swagger/OpenAPI 3.0
- **代码质量**: ESLint, Prettier
- **测试**: Vitest, Playwright
- **容器化**: Docker支持

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- MySQL 8.0+ / PostgreSQL 13+ / openGauss 3.0+


## 📖 使用教程

### 管理员使用
1. 使用管理员账户登录系统
2. 创建学期和课程信息
3. 添加教师和学生账户
4. 配置数据库连接信息

### 教师使用
1. 登录教师账户
2. 创建数据库模式和题目
3. 管理学生信息和学习进度
4. 使用AI分析功能了解学生学习情况
5. 查看学生答题统计和分析报告

### 学生使用
1. 登录学生账户
2. 选择课程和题目进行练习
3. 在线编写和执行SQL语句
4. 查看执行结果和AI分析建议
5. 跟踪个人学习进度

## 🌟 项目特点

### 🔒 安全性
- JWT令牌认证机制
- 角色权限控制
- SQL注入防护
- 数据库连接池管理

### 🚀 高性能
- 异步FastAPI框架
- 数据库连接优化
- 前端组件懒加载
- API响应缓存

### 🎯 易用性
- 直观的用户界面
- 完整的API文档
- 详细的错误提示
- 响应式设计支持

### 🤖 智能化
- AI驱动的SQL分析
- 智能学习建议
- 知识点掌握度评估
- 个性化学习路径

### 🔧 可扩展性
- 模块化架构设计
- 多数据库支持
- 插件化AI服务
- 微服务友好

## 📁 项目结构

```
fastApiProject/
├── app/                    # 后端应用
│   ├── controllers/        # 控制器层
│   ├── services/          # 业务逻辑层
│   ├── models/            # 数据模型
│   ├── schemas/           # 数据验证模式
│   ├── utils/             # 工具函数
│   ├── config/            # 配置文件
│   ├── middleware/        # 中间件
│   ├── tests/             # 测试文件
│   └── main.py            # 应用入口
├── fronted/               # 前端应用
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   └── utils/         # 工具函数
│   ├── public/            # 静态资源
│   └── package.json       # 前端依赖
├── logs/                  # 日志文件
├── 接口文档/               # API文档
└── README.md              # 项目说明
```

## 🔧 配置说明

### 数据库配置
在 `app/.env` 文件中配置数据库连接：

```env
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=sqlsys

# PostgreSQL配置
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=postgres

# openGauss配置
OPENGAUSS_HOST=localhost
OPENGAUSS_PORT=15432
OPENGAUSS_USER=gaussdb
OPENGAUSS_PASSWORD=your_password
OPENGAUSS_DATABASE=postgres
```

### AI服务配置
```env
# AI服务配置
AI_API_URL=your_ai_service_url
AI_API_KEY=your_ai_api_key
```


**SQL在线实践平台** - 让数据库学习更简单、更智能！