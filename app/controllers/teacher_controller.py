from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from models.base import get_db
from schemas.teacher import (
    TeacherProfileResponse, TeacherCourseListResponse, CourseGradeResponse,
    StudentCreateRequest, StudentCreateResponse, StudentImportResponse,
    ScoreCalculateRequest, ScoreUpdateResponse, ScoreListResponse
)
from schemas.admin import StudentInfo, StudentListResponse, OperationResponse
from schemas.response import BaseResponse
from services.teacher_service import teacher_service
from services.user_management_service import user_management_service
from services.auth_dependency import get_current_teacher, get_current_user, get_current_admin

teacher_router = APIRouter(prefix="/teacher", tags=["教师"])

def get_teacher_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """获取教师或管理员用户（教师和管理员都可以访问教师接口）"""
    if current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要教师或管理员权限"
        )
    return current_user

@teacher_router.get("/profile", response_model=TeacherProfileResponse, summary="获取教师个人信息")
async def get_teacher_profile(
    current_user: dict = Depends(get_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    获取当前登录教师的基本信息
    
    需要教师身份的JWT认证令牌
    
    返回教师的基本信息包括：
    - 教职工号
    - 姓名
    - 学期名称
    """
    try:
        # 获取教师信息
        teacher_info = teacher_service.get_teacher_profile(
            teacher_id=current_user["id"],
            db=db
        )
        
        if not teacher_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到教师信息或教师未分配课程"
            )
        
        return teacher_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教师信息失败: {str(e)}"
        )

@teacher_router.get("/courses", response_model=TeacherCourseListResponse, summary="获取教师课程列表")
async def get_teacher_courses(
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    获取当前教师的所有课程列表
    
    需要教师身份的JWT认证令牌
    
    返回：
    - courses: 课程列表
    - total: 总课程数
    """
    try:
        # 获取教师课程列表
        courses = teacher_service.get_teacher_courses(
            teacher_id=current_user["id"],
            db=db
        )
        
        return courses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教师课程列表失败: {str(e)}"
        )

@teacher_router.get("/courses/{course_id}/grades", response_model=CourseGradeResponse, summary="获取课程成绩")
async def get_course_grades(
    course_id: str,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    获取指定课程的学生成绩
    
    需要教师身份的JWT认证令牌
    
    路径参数：
    - course_id: 课程ID
    
    返回：
    - course_id: 课程ID
    - course_name: 课程名称
    - students: 学生成绩列表
    - total_students: 总学生数
    """
    try:
        # 获取课程成绩
        grades = teacher_service.get_course_grades(
            teacher_id=current_user["id"],
            course_id=course_id,
            db=db
        )
        
        if not grades:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在或您没有权限查看该课程"
            )
        
        return grades
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取课程成绩失败: {str(e)}"
        )

@teacher_router.get("/courses/{course_id}/export", summary="导出课程成绩")
async def export_course_grades(
    course_id: str,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    导出指定课程的学生成绩
    
    需要教师身份的JWT认证令牌
    
    路径参数：
    - course_id: 课程ID
    
    返回可用于生成Excel文件的数据
    """
    try:
        # 导出课程成绩
        export_data = teacher_service.export_course_grades(
            teacher_id=current_user["id"],
            course_id=course_id,
            db=db
        )
        
        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在或您没有权限导出该课程成绩"
            )
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出课程成绩失败: {str(e)}"
        )

# 学生管理接口
@teacher_router.post("/students", response_model=StudentCreateResponse, summary="创建学生")
async def create_student(
    student_data: StudentCreateRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    教师创建学生

    需要教师身份的JWT认证令牌

    请求参数：
    - student_id: 学生ID（学号）
    - student_name: 学生姓名
    - class_: 班级
    - student_password: 学生密码

    返回创建的学生信息
    """
    try:
        success, message, student_info = teacher_service.create_student(
            teacher_id=current_user["id"],
            student_data=student_data,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return student_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建学生失败: {str(e)}"
        )

@teacher_router.post("/students/import", response_model=StudentImportResponse, summary="批量导入学生")
async def import_students(
    file: UploadFile = File(..., description="Excel文件，包含学号、姓名、班级、密码列"),
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    从Excel文件批量导入学生

    需要教师身份的JWT认证令牌

    文件要求：
    - 格式：Excel文件（.xlsx 或 .xls）
    - 必需列：学号、姓名、班级、密码
    - 第一行为表头

    返回：
    - code: 状态码
    - msg: 消息
    - success_count: 成功导入数量
    - fail_count: 失败数量
    - fail_details: 失败详情列表
    """
    try:
        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件格式不正确，请上传Excel文件（.xlsx或.xls）"
            )

        # 读取文件内容
        file_content = await file.read()

        # 调用服务层处理导入
        result = teacher_service.import_students_from_excel(
            teacher_id=current_user["id"],
            file_content=file_content,
            db=db
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入学生失败: {str(e)}"
        )

# 学生管理接口（复用AdminService）
@teacher_router.get("/students", response_model=StudentListResponse, summary="获取学生列表")
async def get_students(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（学生ID或姓名）"),
    class_filter: Optional[str] = Query(None, description="班级过滤"),
    current_user: dict = Depends(get_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    分页获取学生列表，支持搜索和班级过滤

    需要教师或管理员身份的JWT认证令牌

    查询参数：
    - page: 页码（默认1）
    - limit: 每页数量（默认20，最大100）
    - search: 搜索关键词（学生ID或姓名）
    - class_filter: 班级过滤

    返回学生列表和分页信息
    """
    try:
        students = user_management_service.get_students(
            page=page,
            limit=limit,
            search=search,
            class_filter=class_filter,
            current_user=current_user,
            db=db
        )

        return students

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学生列表失败: {str(e)}"
        )

@teacher_router.get("/students/{student_id}", response_model=StudentInfo, summary="获取学生信息")
async def get_student(
    student_id: str,
    current_user: dict = Depends(get_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    获取指定学生的详细信息

    需要教师或管理员身份的JWT认证令牌

    路径参数：
    - student_id: 学生ID

    返回学生的详细信息
    """
    try:
        student_info = user_management_service.get_student_by_id(
            student_id=student_id,
            current_user=current_user,
            db=db
        )

        if not student_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学生不存在"
            )

        return student_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学生信息失败: {str(e)}"
        )

@teacher_router.put("/students/{student_id}", response_model=StudentInfo, summary="更新学生信息")
async def update_student(
    student_id: str,
    student_data: StudentCreateRequest,
    current_user: dict = Depends(get_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    更新学生信息

    需要教师或管理员身份的JWT认证令牌

    路径参数：
    - student_id: 学生ID

    请求参数：
    - student_name: 学生姓名
    - class_: 班级
    - student_password: 学生密码

    返回更新后的学生信息，格式与管理员接口一致：
    {
      "id": 1,
      "student_id": "20232251177",
      "student_name": "张三",
      "class_": "计算机科学与技术1班"
    }
    """
    try:
        success, message, student_info = user_management_service.update_student(
            student_id=student_id,
            student_name=student_data.student_name,
            class_=student_data.class_,
            student_password=student_data.student_password,
            current_user=current_user,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return student_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新学生信息失败: {str(e)}"
        )

@teacher_router.delete("/students/{student_id}", response_model=OperationResponse, summary="删除学生")
async def delete_student(
    student_id: str,
    current_user: dict = Depends(get_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    删除学生（如果有关联记录则无法删除）

    需要教师或管理员身份的JWT认证令牌

    路径参数：
    - student_id: 学生ID

    返回标准操作响应格式：
    {
      "success": true,
      "message": "学生删除成功"
    }

    注意：如果学生有关联的答题记录，将无法删除
    """
    try:
        success, message = user_management_service.delete_student(
            student_id=student_id,
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
            detail=f"删除学生失败: {str(e)}"
        )

# 分数核算接口
@teacher_router.put("/score/calculate", response_model=ScoreUpdateResponse, summary="教师核算分数")
async def calculate_scores(
    score_request: ScoreCalculateRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    根据所选题目ID列表，计算学生答题的总分数并更新到数据库

    需要教师身份的JWT认证令牌

    请求参数：
    - problem_ids: 题目ID列表，例如 [5, 6, 7, 8]

    处理逻辑：
    1. 调用/public/currentSemester获取学期号
    2. 根据学期号，获取所有课程号
    3. 在选课表里找到所有学生
    4. 根据答题记录表计算每个学生的分数，一道题10分
    5. 把分数更新到CourseSelection表的score字段

    返回：
    - code: 状态码（200表示成功）
    - msg: 消息（"更新分数成功"）
    """
    try:
        result = teacher_service.calculate_scores(
            teacher_id=current_user["id"],
            problem_ids=score_request.problem_ids,
            db=db
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"核算分数失败: {str(e)}"
        )

@teacher_router.get("/score", response_model=ScoreListResponse, summary="获取学生分数")
async def get_student_scores(
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    获取当前学期所有课程下学生的总分数

    需要教师身份的JWT认证令牌

    处理逻辑：
    1. 获取当前学期
    2. 查询教师在当前学期的所有课程
    3. 从CourseSelection表中获取学生分数

    返回：
    - code: 状态码
    - msg: 消息
    - scorelist: 学生分数列表
    """
    try:
        result = teacher_service.get_student_scores(
            teacher_id=current_user["id"],
            db=db
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学生分数失败: {str(e)}"
        )

@teacher_router.get("/currentSemester", summary="获取当前学期")
async def get_current_semester(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据日期，获取当前学期

    需要登录认证（所有角色可访问）

    返回：
    - semester_id: 学期ID
    - semester_name: 学期名称

    描述：可直接调用公共服务，减少重复
    """
    try:
        from services.public_service import public_service
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

@teacher_router.get("/score/export", summary="导出核算分数结果")
async def export_scores(
    course_id: str = Query(..., description="课程号（如 '03'）"),
    class_id: Optional[str] = Query(None, description="班级ID（可选）"),
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    将已核算的学生分数结果导出为Excel文件

    需要教师身份的JWT认证令牌

    查询参数：
    - course_id: 课程号（必需）
    - class_id: 班级ID（可选，用于过滤特定班级）

    返回：Excel文件流
    文件名示例：2025年春季-三班.xlsx

    描述：使用ECharts实现表格功能
    """
    try:
        # 获取导出数据
        export_data = teacher_service.export_scores(
            teacher_id=current_user["id"],
            course_id=course_id,
            class_id=class_id,
            db=db
        )

        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在或您没有权限导出该课程成绩"
            )

        # 返回可用于前端ECharts表格展示的数据
        # 实际项目中这里应该生成Excel文件并返回文件流
        return {
            "message": "导出数据准备完成，请使用ECharts表格展示",
            "filename": f"{export_data['course_info']['semester_name']}-{export_data['course_info']['class_filter']}.xlsx",
            "data": export_data,
            "echarts_config": {
                "title": {
                    "text": f"课程成绩统计 - {export_data['course_info']['course_name']}",
                    "subtext": f"学期：{export_data['course_info']['semester_name']} | 班级：{export_data['course_info']['class_filter']}"
                },
                "tooltip": {
                    "trigger": "axis"
                },
                "legend": {
                    "data": ["总分"]
                },
                "xAxis": {
                    "type": "category",
                    "data": [student["学号"] for student in export_data["students"]]
                },
                "yAxis": {
                    "type": "value",
                    "name": "分数"
                },
                "series": [{
                    "name": "总分",
                    "type": "bar",
                    "data": [student["总分"] for student in export_data["students"]],
                    "itemStyle": {
                        "color": "#5470c6"
                    }
                }]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出分数失败: {str(e)}"
        )
