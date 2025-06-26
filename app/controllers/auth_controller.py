from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.base import get_db
from schemas.auth import LoginRequest, LoginResponse, LoginData
from schemas.response import BaseResponse
from services.auth_service import auth_service

auth_router = APIRouter(prefix="/auth", tags=["认证"])

@auth_router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    - **account**: 账号（学号/教职工号/admin）
    - **password**: 密码
    - **role**: 角色类型（admin/teacher/student）
    """
    try:
        # 用户认证
        result = auth_service.authenticate_user(login_data, db)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        user_info, access_token = result
        
        # 构造响应数据
        response_data = LoginData(
            token=access_token,
            user=user_info
        )
        
        return LoginResponse(
            code=200,
            message="登录成功",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@auth_router.post("/logout", response_model=BaseResponse, summary="用户登出")
async def logout():
    """
    用户登出接口
    
    注意：JWT是无状态的，客户端只需删除本地存储的token即可
    """
    return BaseResponse(
        code=200,
        message="登出成功",
        data=None
    ) 