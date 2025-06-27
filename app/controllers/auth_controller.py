from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.base import get_db
from schemas.auth import LoginRequest, LoginResponse, LoginData, UpdatePasswordRequest
from schemas.response import BaseResponse
from services.auth_service import auth_service
from services.auth_dependency import get_current_user

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

@auth_router.put("/password", response_model=BaseResponse, summary="修改密码")
async def update_password(
    password_data: UpdatePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码接口
    
    需要提供JWT认证令牌
    
    - **old_password**: 原密码
    - **new_password**: 新密码
    """
    try:
        # 验证新密码不能为空
        if not password_data.new_password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能为空"
            )
        
        # 验证新密码长度
        if len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码长度不能少于6位"
            )
        
        # 验证新旧密码不能相同
        if password_data.old_password == password_data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能与原密码相同"
            )
        
        # 调用服务层修改密码
        success = auth_service.update_password(
            user_id=current_user["id"],
            role=current_user["role"],
            old_password=password_data.old_password,
            new_password=password_data.new_password,
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误或修改失败"
            )
        
        return BaseResponse(
            code=200,
            message="密码修改成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )