from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from services.jwt_service import jwt_service

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前用户信息"""
    token = credentials.credentials
    
    payload = jwt_service.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role")
    }

async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前管理员用户"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

async def get_current_teacher(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前教师用户"""
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要教师权限"
        )
    return current_user

async def get_current_student(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前学生用户"""
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要学生权限"
        )
    return current_user

async def get_current_teacher_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前教师或管理员用户"""
    if current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要教师或管理员权限"
        )
    return current_user 