from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from models.base import get_db
from schemas.admin import (
    SemesterUpdateRequest, SemesterUpdateResponse, SemesterInfo, SemesterCreateRequest,
    SemesterListResponse, TeacherCreateRequest, TeacherInfo, TeacherUpdateRequest,
    TeacherListResponse, OperationResponse, DatabaseSchemaCreateRequest,
    DatabaseSchemaUpdateRequest, DatabaseSchemaInfo, DatabaseSchemaListResponse
)
# 已删除学生相关Schema导入: StudentCreateRequest, StudentInfo, StudentUpdateRequest, StudentListResponse
from schemas.response import BaseResponse
from services.admin_service import admin_service
from services.user_management_service import user_management_service
from services.auth_dependency import get_current_admin, get_current_user

admin_router = APIRouter(prefix="/admin", tags=["管理员"])

# 当前学期接口已移至 /public 路径
# 请使用 GET /public/currentSemester 替代此接口

@admin_router.put("/semester/time", response_model=SemesterUpdateResponse, summary="修改学期时间")
async def update_semester_time(
    request_data: SemesterUpdateRequest,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    修改学期时间
    
    需要管理员身份的JWT认证令牌
    
    请求参数：
    - semester_id: 学期ID
    - begin_date: 开始日期 (YYYY-MM-DD格式)
    - end_date: 结束日期 (YYYY-MM-DD格式)
    
    返回：
    - success: 是否成功
    - message: 操作结果信息
    - semester: 更新后的学期信息
    
    注意事项：
    - 开始日期必须早于结束日期
    - 不能与其他学期时间冲突
    - 学期必须存在
    """
    try:
        # 更新学期时间
        success, message, semester_info = admin_service.update_semester_time(
            semester_id=request_data.semester_id,
            begin_date=request_data.begin_date,
            end_date=request_data.end_date,
            current_user=current_user,
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return SemesterUpdateResponse(
            success=success,
            message=message,
            semester=semester_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改学期时间失败: {str(e)}"
        )

@admin_router.get("/semester/{semester_id}", response_model=SemesterInfo, summary="获取学期信息")
async def get_semester_info(
    semester_id: int,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取学期信息
    
    需要管理员身份的JWT认证令牌
    
    路径参数：
    - semester_id: 学期ID
    
    返回学期的详细信息：
    - semester_id: 学期ID
    - semester_name: 学期名称
    - begin_date: 开始日期
    - end_date: 结束日期
    - date_id: 日期范围ID
    """
    try:
        # 获取学期信息
        semester_info = admin_service.get_semester_info(
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

# 教师管理接口
@admin_router.post("/teachers", response_model=TeacherInfo, summary="创建教师")
async def create_teacher(
    teacher_data: TeacherCreateRequest,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建教师

    需要管理员身份的JWT认证令牌

    请求参数：
    - teacher_id: 教师ID（唯一）
    - teacher_name: 教师姓名
    - teacher_password: 教师密码

    返回创建的教师信息
    """
    try:
        success, message, teacher_info = user_management_service.create_teacher(
            teacher_id=teacher_data.teacher_id,
            teacher_name=teacher_data.teacher_name,
            teacher_password=teacher_data.teacher_password,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return teacher_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建教师失败: {str(e)}"
        )

@admin_router.get("/teachers", response_model=TeacherListResponse, summary="获取教师列表")
async def get_teachers(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（教师ID或姓名）"),
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取教师列表

    需要管理员身份的JWT认证令牌

    查询参数：
    - page: 页码（默认1）
    - limit: 每页数量（默认20，最大100）
    - search: 搜索关键词（可选）

    返回教师列表和分页信息
    """
    try:
        teachers = user_management_service.get_teachers(
            page=page,
            limit=limit,
            search=search,
            current_user=current_user,
            db=db
        )

        return teachers

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教师列表失败: {str(e)}"
        )

@admin_router.get("/teachers/{teacher_id}", response_model=TeacherInfo, summary="获取教师信息")
async def get_teacher(
    teacher_id: str,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取教师信息

    需要管理员身份的JWT认证令牌

    路径参数：
    - teacher_id: 教师ID

    返回教师的详细信息
    """
    try:
        teacher_info = user_management_service.get_teacher_by_id(
            teacher_id=teacher_id,
            current_user=current_user,
            db=db
        )

        if not teacher_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教师不存在"
            )

        return teacher_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教师信息失败: {str(e)}"
        )

@admin_router.put("/teachers/{teacher_id}", response_model=TeacherInfo, summary="更新教师信息")
async def update_teacher(
    teacher_id: str,
    teacher_data: TeacherUpdateRequest,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新教师信息

    需要管理员身份的JWT认证令牌

    路径参数：
    - teacher_id: 教师ID

    请求参数：
    - teacher_name: 教师姓名（可选）
    - teacher_password: 教师密码（可选）

    返回更新后的教师信息
    """
    try:
        success, message, teacher_info = user_management_service.update_teacher(
            teacher_id=teacher_id,
            teacher_name=teacher_data.teacher_name,
            teacher_password=teacher_data.teacher_password,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return teacher_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新教师信息失败: {str(e)}"
        )

@admin_router.delete("/teachers/{teacher_id}", response_model=OperationResponse, summary="删除教师")
async def delete_teacher(
    teacher_id: str,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除教师

    需要管理员身份的JWT认证令牌

    路径参数：
    - teacher_id: 教师ID

    注意：如果教师有关联的课程，将无法删除
    """
    try:
        success, message = user_management_service.delete_teacher(
            teacher_id=teacher_id,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return OperationResponse(success=success, message=message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除教师失败: {str(e)}"
        )

# 已删除: 学生管理接口 - 不再需要在admin控制器中实现

# 学期管理接口
@admin_router.post("/semesters", response_model=SemesterInfo, summary="创建学期")
async def create_semester(
    semester_data: SemesterCreateRequest,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建学期

    需要管理员身份的JWT认证令牌

    请求参数：
    - semester_name: 学期名称
    - begin_date: 开始日期 (YYYY-MM-DD格式)
    - end_date: 结束日期 (YYYY-MM-DD格式)

    返回创建的学期信息

    注意事项：
    - 开始日期必须早于结束日期
    - 不能与其他学期时间冲突
    """
    try:
        success, message, semester_info = admin_service.create_semester(
            semester_name=semester_data.semester_name,
            begin_date=semester_data.begin_date,
            end_date=semester_data.end_date,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return semester_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建学期失败: {str(e)}"
        )

@admin_router.get("/semesters", response_model=SemesterListResponse, summary="获取学期列表")
async def get_semesters(
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取学期列表

    需要管理员身份的JWT认证令牌

    返回所有学期的列表，包括学期信息和时间范围
    """
    try:
        semesters = admin_service.get_semesters(current_user=current_user, db=db)
        return semesters

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学期列表失败: {str(e)}"
        )

@admin_router.delete("/semesters/{semester_id}", response_model=OperationResponse, summary="删除学期")
async def delete_semester(
    semester_id: int,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除学期

    需要管理员身份的JWT认证令牌

    路径参数：
    - semester_id: 学期ID

    注意：如果学期有关联的课程，将无法删除
    """
    try:
        success, message = admin_service.delete_semester(
            semester_id=semester_id,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return OperationResponse(success=success, message=message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除学期失败: {str(e)}"
        )

# 数据库模式管理接口
@admin_router.post("/schemas", response_model=DatabaseSchemaInfo, summary="创建数据库模式")
async def create_database_schema(
    schema_data: DatabaseSchemaCreateRequest,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建数据库模式

    需要管理员身份的JWT认证令牌

    请求参数：
    - schema_name: 数据库模式名称（唯一）
    - schema_description: 数据库模式描述（可选）

    返回创建的数据库模式信息
    """
    try:
        success, message, schema_info = admin_service.create_database_schema(
            schema_name=schema_data.schema_name,
            schema_description=schema_data.schema_description,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return schema_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建数据库模式失败: {str(e)}"
        )

@admin_router.get("/schemas", response_model=DatabaseSchemaListResponse, summary="获取数据库模式列表", deprecated=True)
async def get_database_schemas(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（模式名称）"),
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取数据库模式列表

    ⚠️ **已废弃**: 此接口已被 GET /public/schema/list 替代

    新接口特点：
    - 所有登录用户都可以访问（不再限制管理员）
    - 返回格式为数组，包含 schema_name, schema_description, schema_author
    - 接口路径: GET /public/schema/list

    需要管理员身份的JWT认证令牌

    查询参数：
    - page: 页码（默认1）
    - limit: 每页数量（默认20，最大100）
    - search: 搜索关键词（可选）

    返回数据库模式列表和分页信息
    """
    try:
        schemas = admin_service.get_database_schemas(
            page=page,
            limit=limit,
            search=search,
            current_user=current_user,
            db=db
        )

        return schemas

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库模式列表失败: {str(e)}"
        )

@admin_router.get("/schemas/{schema_id}", response_model=DatabaseSchemaInfo, summary="获取数据库模式信息")
async def get_database_schema(
    schema_id: int,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取指定数据库模式的详细信息

    需要管理员身份的JWT认证令牌

    路径参数：
    - schema_id: 数据库模式ID

    返回数据库模式的详细信息
    """
    try:
        schema_info = admin_service.get_database_schema_by_id(
            schema_id=schema_id,
            current_user=current_user,
            db=db
        )

        if not schema_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据库模式不存在"
            )

        return schema_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库模式信息失败: {str(e)}"
        )

@admin_router.put("/schemas/{schema_id}", response_model=DatabaseSchemaInfo, summary="更新数据库模式信息")
async def update_database_schema(
    schema_id: int,
    schema_data: DatabaseSchemaUpdateRequest,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新数据库模式信息

    需要管理员身份的JWT认证令牌

    路径参数：
    - schema_id: 数据库模式ID

    请求参数：
    - schema_name: 数据库模式名称（可选）
    - schema_description: 数据库模式描述（可选）

    返回更新后的数据库模式信息
    """
    try:
        success, message, schema_info = admin_service.update_database_schema(
            schema_id=schema_id,
            schema_name=schema_data.schema_name,
            schema_description=schema_data.schema_description,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return schema_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新数据库模式失败: {str(e)}"
        )

@admin_router.delete("/schemas/{schema_id}", response_model=OperationResponse, summary="删除数据库模式")
async def delete_database_schema(
    schema_id: int,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除数据库模式

    需要管理员身份的JWT认证令牌

    路径参数：
    - schema_id: 数据库模式ID

    注意：如果数据库模式有关联的题目，将无法删除
    """
    try:
        success, message = admin_service.delete_database_schema(
            schema_id=schema_id,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return OperationResponse(success=success, message=message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除数据库模式失败: {str(e)}"
        )
