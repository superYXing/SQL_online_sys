from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from controllers.auth_controller import auth_router
from controllers.student_controller import student_router
from controllers.admin_controller import admin_router
from controllers.teacher_controller import teacher_router
from controllers.public_controller import public_router

# 创建FastAPI应用实例
app = FastAPI(
    title="SQL在线平台API",
    description="基于FastAPI的SQL在线学习平台后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
    uvicorn.run(app, host="localhost", port=8000)
