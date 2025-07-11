from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import logging

# 初始化日志配置（必须在其他导入之前）
from config.logging_config import setup_logging, get_logger
setup_logging()

from controllers.auth_controller import auth_router
from controllers.student_controller import student_router
from controllers.admin_controller import admin_router
from controllers.teacher_controller import teacher_router
from controllers.public_controller import public_router
from services.monitor_service import AccessMonitorMiddleware, monitor_service
from middleware.exception_handler import GlobalExceptionHandler

# 获取应用日志器
app_logger = get_logger('app')

# 创建FastAPI应用实例
app = FastAPI(
    title="SQL在线平台API",
    description="基于FastAPI的SQL在线学习平台后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app_logger.info("SQL在线平台API启动中...")

# 添加全局异常处理中间件（最先添加）
app.add_middleware(GlobalExceptionHandler)

# 添加访问监控中间件（需要在CORS中间件之前添加）
app.add_middleware(AccessMonitorMiddleware, monitor_service=monitor_service)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(admin_router)
app.include_router(teacher_router)
app.include_router(public_router)

@app.get("/", include_in_schema=False)  # 设置include_in_schema=False，使此路由不在文档中显示
async def redirect_to_docs():
    """根路径重定向到API文档"""
    return RedirectResponse(url="/docs")



if __name__ == "__main__":
    import uvicorn

    # 启动信息
    app_logger.info("正在启动SQL在线平台服务器...")
    app_logger.info("服务器地址: http://127.0.0.1:8000")
    app_logger.info("API文档地址: http://127.0.0.1:8000/docs")

    print("\n🚀 SQL在线平台启动中...")
    print("📊 控制台将显示实时在线状态")
    print("📝 详细日志已保存到 logs/ 目录")
    print("=" * 50)

    # 配置uvicorn日志
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        log_config=None,  # 禁用uvicorn默认日志配置
        access_log=False  # 禁用uvicorn访问日志（我们有自己的）
    )
