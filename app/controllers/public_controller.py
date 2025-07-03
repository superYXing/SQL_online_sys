from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from models.base import get_db
from schemas.public import (
    CurrentSemesterResponse, SemesterListResponse, SystemInfoResponse,
    DatabaseSchemaPublicListResponse, ProblemPublicListResponse, DatabaseSchemaListResponse
)
from services.public_service import public_service
from services.auth_dependency import get_current_user

public_router = APIRouter(prefix="/public", tags=["公共接口"])

@public_router.get("/currentSemester", response_model=CurrentSemesterResponse, summary="获取当前学期")
async def get_current_semester(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据当前日期获取当前学期
    
    需要登录认证（所有角色可访问）
    
    返回：
    - semester_id: 学期ID
    - semester_name: 学期名称
    
    如果当前日期不在任何学期范围内，返回最新的学期
    """
    try:
        current_semester = public_service.get_current_semester(db=db)
        
        if not current_semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到当前学期信息"
            )
        
        return current_semester
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取当前学期失败: {str(e)}"
        )

@public_router.get("/semesters", response_model=SemesterListResponse, summary="获取所有学期列表")
async def get_all_semesters(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有学期列表
    
    需要登录认证（所有角色可访问）
    
    返回：
    - semesters: 学期列表（包含日期范围和是否为当前学期）
    - total: 总学期数
    - current_semester: 当前学期信息
    """
    try:
        semesters = public_service.get_all_semesters(db=db)
        return semesters
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学期列表失败: {str(e)}"
        )

@public_router.get("/system/info", response_model=SystemInfoResponse, summary="获取系统信息")
async def get_system_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取系统基本信息
    
    需要登录认证（所有角色可访问）
    
    返回：
    - system_name: 系统名称
    - version: 系统版本
    - current_time: 当前时间
    - current_semester: 当前学期信息
    """
    try:
        system_info = public_service.get_system_info(db=db)
        return system_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统信息失败: {str(e)}"
        )

@public_router.get("/schemas", response_model=DatabaseSchemaPublicListResponse, summary="获取数据库模式列表")
async def get_database_schemas(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有数据库模式列表（公共访问）

    需要登录认证（所有角色可访问）

    返回：
    - schemas: 数据库模式列表
    - total: 总模式数
    """
    try:
        schemas = public_service.get_public_database_schemas(db=db)
        return schemas

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库模式列表失败: {str(e)}"
        )

@public_router.get("/schema/list", response_model=DatabaseSchemaListResponse, summary="获取所有数据库模式")
async def get_all_database_schemas(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有数据库模式列表（新格式）

    需要登录认证（所有角色可访问）

    返回：
    - 数据库模式数组，每个元素包含：
      - schema_name: 模式名称
      - schema_description: 模式描述（HTML格式）
      - schema_author: 模式作者

    注意：此接口替代了 /admin/schemas 接口，现在所有登录用户都可以访问
    """
    try:
        schemas = public_service.get_database_schema_list(db=db)
        return schemas

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库模式列表失败: {str(e)}"
        )

@public_router.get("/problem/list", response_model=ProblemPublicListResponse, summary="获取题目列表")
async def get_problem_list(
    schema_id: Optional[int] = Query(None, description="数据库模式ID，不指定则返回所有题目"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取题目列表（公共访问）

    需要登录认证（所有角色可访问）

    查询参数：
    - schema_id: 数据库模式ID（可选），不指定则返回所有题目

    返回：
    - problems: 题目列表
    - total: 总题目数
    - schema_id: 查询的模式ID
    - schema_name: 模式名称（如果指定了schema_id）
    """
    try:
        # 获取题目列表
        problems = public_service.get_public_problem_list(
            schema_id=schema_id,
            db=db
        )

        return problems

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题目列表失败: {str(e)}"
        )

@public_router.get("/semester/{semester_id}/info", summary="获取指定学期信息")
async def get_semester_info(
    semester_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定学期的详细信息
    
    需要登录认证（所有角色可访问）
    
    路径参数：
    - semester_id: 学期ID
    
    返回学期的详细信息包括日期范围
    """
    try:
        semester_info = public_service.get_semester_date_range(
            semester_id=semester_id,
            db=db
        )
        
        if not semester_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学期不存在"
            )
        
        return semester_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学期信息失败: {str(e)}"
        )

@public_router.get("/health", summary="健康检查")
async def health_check():
    """
    系统健康检查接口
    
    无需认证
    
    返回系统运行状态
    """
    return {
        "status": "healthy",
        "message": "SQL在线平台运行正常",
        "timestamp": "2024-01-15T10:30:00Z"
    }
