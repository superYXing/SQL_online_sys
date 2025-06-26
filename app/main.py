from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from controllers.auth_controller import auth_router
from services.auth_dependency import get_current_user

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

@app.get("/", summary="根路径")
async def root():
    """根路径接口"""
    return {"message": "欢迎使用SQL在线平台API", "version": "1.0.0"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
