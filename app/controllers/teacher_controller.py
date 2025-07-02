import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import io
from models.base import get_db
from schemas.teacher import (
    TeacherProfileResponse, TeacherCourseListResponse, CourseGradeResponse,
    StudentCreateRequest, StudentCreateResponse, StudentImportResponse,
    ScoreCalculateRequest, ScoreUpdateResponse, ScoreListResponse,
    TeacherProblemListResponse, TeacherSchemaListResponse,
    SQLQueryRequest, SQLQueryResponse, SemesterListResponse,
    DashboardMatrixResponse, StudentProblemStatsRequest, StudentProblemStatsResponse,
    StudentProfileResponse, ProblemStatisticsResponse, ProblemSummaryResponse,
    DatasetExportResponse, ProblemDetailResponse, ProblemEditRequest, ProblemEditResponse,
    TeacherStudentListResponse, ScoreExportRequest, ExportStudentInfo,
    StudentProblemStatisticsResponse, StudentInfoResponse, StudentProfileNewResponse,
    StudentProfileDocResponse, StudentDetailResponse, StudentScoreExportRequest,
    ProblemDeleteResponse
)
from schemas.admin import StudentInfo, StudentListResponse, OperationResponse
from schemas.response import BaseResponse
from services.teacher_service import teacher_service
from services.user_management_service import user_management_service
from services.student_service import student_service
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

# @teacher_router.get("/courses", response_model=TeacherCourseListResponse, summary="获取教师课程列表")
# async def get_teacher_courses(
#     current_user: dict = Depends(get_current_teacher),
#     db: Session = Depends(get_db)
# ):
#     """
#     获取当前教师的所有课程列表
#
#     需要教师身份的JWT认证令牌
#
#     返回：
#     - courses: 课程列表
#     - total: 总课程数
#     """
#     try:
#         # 获取教师课程列表
#         courses = teacher_service.get_teacher_courses(
#             teacher_id=current_user["id"],
#             db=db
#         )
#
#         return courses
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"获取教师课程列表失败: {str(e)}"
#         )
#
# @teacher_router.get("/courses/{course_id}/grades", response_model=CourseGradeResponse, summary="获取课程成绩")
# async def get_course_grades(
#     course_id: str,
#     current_user: dict = Depends(get_current_teacher),
#     db: Session = Depends(get_db)
# ):
#     """
#     获取指定课程的学生成绩
#
#     需要教师身份的JWT认证令牌
#
#     路径参数：
#     - course_id: 课程ID
#
#     返回：
#     - course_id: 课程ID
#     - course_name: 课程名称
#     - students: 学生成绩列表
#     - total_students: 总学生数
#     """
#     try:
#         # 获取课程成绩
#         grades = teacher_service.get_course_grades(
#             teacher_id=current_user["id"],
#             course_id=course_id,
#             db=db
#         )
#
#         if not grades:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="课程不存在或您没有权限查看该课程"
#             )
#
#         return grades
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"获取课程成绩失败: {str(e)}"
#         )
#
# @teacher_router.get("/courses/{course_id}/export", summary="导出课程成绩")
# async def export_course_grades(
#     course_id: str,
#     current_user: dict = Depends(get_current_teacher),
#     db: Session = Depends(get_db)
# ):
#     """
#     导出指定课程的学生成绩
#
#     需要教师身份的JWT认证令牌
#
#     路径参数：
#     - course_id: 课程ID
#
#     返回可用于生成Excel文件的数据
#     """
#     try:
#         # 导出课程成绩
#         export_data = teacher_service.export_course_grades(
#             teacher_id=current_user["id"],
#             course_id=course_id,
#             db=db
#         )
#
#         if not export_data:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="课程不存在或您没有权限导出该课程成绩"
#             )
#
#         return export_data
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"导出课程成绩失败: {str(e)}"
#         )

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

# 学生管理接口
@teacher_router.get("/students", response_model=TeacherStudentListResponse, summary="获取学生列表")
async def get_students(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（学生ID或姓名）"),
    class_filter: Optional[str] = Query(None, description="班级过滤"),
    semester_id: Optional[int] = Query(None, description="学期ID（可选，否则查看所有学期）"),
    current_user: dict = Depends(get_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    分页获取学生列表，支持搜索和班级过滤

    根据学期id确认所有课程，在课程范围内查找所有学生信息，最后在选课记录表根据学号和课程号

    需要教师或管理员身份的JWT认证令牌

    查询参数：
    - page: 页码（默认1）
    - limit: 每页数量（默认20，最大100）
    - search: 搜索关键词（学生ID或姓名）
    - class_filter: 班级过滤
    - semester_id: 学期ID（可选，否则查看所有学期）

    返回数据：
    - students: 学生列表，包含学生ID、姓名、班级、教师姓名、学期名称、课程ID
    - total: 总数
    - page: 页码
    - limit: 每页数量
    """
    try:
        students = teacher_service.get_students_by_semester(
            page=page,
            limit=limit,
            search=search,
            class_filter=class_filter,
            semester_id=semester_id,
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

# 当前学期接口已移至 /public 路径
# 请使用 GET /public/currentSemester 替代此接口

@teacher_router.post("/score/export", summary="导出核算分数结果")
async def export_scores(
    export_request: ScoreExportRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    将前端传入的学生分数信息列表生成 Excel 文件并返回

    需要教师身份的JWT认证令牌

    请求参数：
    - students: 学生信息列表，包含学生详细分数数据

    返回：Excel 文件流
    文件名示例：2025年春季-三班-成绩表.xlsx

    文件生成逻辑：
    - 根据前端提交的 students 列表逐条写入 Excel
    - 文件名可根据学期、班级、时间自动拼接
    - 文件生成后直接返回文件流，前端可选择下载

    Excel 文件列：学号、姓名、班级、课序号、状态、总分数
    """
    try:
        if not export_request.students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学生信息列表不能为空"
            )

        # 生成Excel文件
        excel_data = teacher_service.export_scores_to_excel(export_request.students)

        # 生成文件名
        filename = teacher_service.generate_export_filename(export_request.students)

        # 创建文件流
        excel_stream = io.BytesIO(excel_data)

        # 返回Excel文件流
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出分数失败: {str(e)}"
        )

# 题目和数据库模式相关接口已移至 /public 路径
# 请使用 GET /public/problem/list 替代此接口

# 数据库模式列表接口已移至 /public 路径
# 请使用 GET /public/schemas 替代此接口

# SQL查询接口
@teacher_router.post("/schema/query", response_model=SQLQueryResponse, summary="执行SQL查询")
async def execute_sql_query(
    query_request: SQLQueryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    执行SQL查询并返回结果

    需要登录认证（只有教师可访问）

    请求参数：
    - sql: SQL查询语句
    - schema_id: 数据库模式ID

    返回：
    - success: 是否成功
    - data: 查询结果数据
    - columns: 列名列表
    - row_count: 行数
    - error_message: 错误信息（如果有）
    """
    try:
        # 调用服务层方法
        result = teacher_service.execute_sql_query(
            sql=query_request.sql,
            schema_id=query_request.schema_id,
            db=db
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        return SQLQueryResponse(
            success=False,
            data=None,
            columns=None,
            row_count=0,
            error_message=f"SQL执行失败: {str(e)}"
        )



# 态势矩阵接口
@teacher_router.get("/dashboard/matrix", response_model=DashboardMatrixResponse, summary="查看态势矩阵接口")
async def get_dashboard_matrix(
    year_term: Optional[str] = Query(None, description="学期（如 '2025春季'），不传则返回所有学期的汇总数据"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    返回态势矩阵数据，列为数据库模式（schema_name），学期

    需要登录认证（教师角色可访问）

    查询逻辑：
    1. 在学期表里根据学期名找到学期号
    2. 在课程表里根据学期号找到所有课程号
    3. 在选课表里根据课程号找到所有学生号
    4. 在答题表里根据学号找到题目数量，提交数量

    参数：
    - year_term: 学期筛选（可选），如 "2025春季"

    返回：
    - code: 状态码
    - msg: 消息
    - matrix: 按学期分组的统计矩阵数据
    """
    try:
        # 调用服务层方法
        result = teacher_service.get_dashboard_matrix(
            year_term=year_term,
            db=db
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取态势矩阵失败: {str(e)}"
        )

# 学生题目提交情况查询接口
@teacher_router.post("/student/problem-stats", response_model=StudentProblemStatsResponse, summary="查询学生题目提交情况")
async def get_student_problem_stats(
    stats_request: StudentProblemStatsRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    根据传入的学生 ID 和题目 ID，返回每个学生在每个题目上的提交次数和正确次数

    需要教师身份的JWT认证令牌

    请求参数：
    - student_ids: 学生ID列表（学号）
    - problem_ids: 题目编号列表

    返回：
    - data: 学生题目统计数据列表，包含每个学生在每个题目上的提交次数和正确次数
    """
    try:
        from models import Student, Problem, AnswerRecord
        from sqlalchemy import func

        # 验证输入参数
        if not stats_request.student_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学生ID列表不能为空"
            )

        if not stats_request.problem_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="题目ID列表不能为空"
            )

        # 转换problem_ids为整数（如果需要）
        try:
            problem_ids_int = [int(pid) for pid in stats_request.problem_ids]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="题目ID格式错误，必须为数字"
            )

        # 构建结果列表
        result_data = []

        # 遍历每个学生和每个题目的组合
        for student_id in stats_request.student_ids:
            for problem_id_str, problem_id_int in zip(stats_request.problem_ids, problem_ids_int):
                # 查询该学生在该题目上的所有提交记录，关联Student表
                submissions = db.query(AnswerRecord).join(
                    Student, AnswerRecord.student_id == Student.id
                ).filter(
                    Student.student_id == student_id,
                    AnswerRecord.problem_id == problem_id_int
                ).all()

                # 统计提交次数和正确次数
                submit_count = len(submissions)
                correct_count = sum(1 for s in submissions if s.is_correct)

                # 只有当有提交记录时才添加到结果中
                if submit_count > 0:
                    result_data.append({
                        "student_id": student_id,
                        "problem_id": problem_id_str,
                        "submit_count": submit_count,
                        "correct_count": correct_count
                    })

        return StudentProblemStatsResponse(data=result_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询学生题目提交情况失败: {str(e)}"
        )

# 获取学生信息接口
# @teacher_router.get("/student/info", response_model=StudentInfoResponse, summary="获取学生信息")
# async def get_student_info(
#     student_id: str = Query(..., description="学生ID"),
#     current_user: dict = Depends(get_current_teacher),
#     db: Session = Depends(get_db)
# ):
#     """
#     根据学生ID获取学生基本信息
#
#     需要教师身份的JWT认证令牌
#
#     查询参数：
#     - student_id: 学生ID（学号）
#
#     返回：
#     - code: 状态码
#     - msg: 消息
#     - data: 学生基本信息
#     """
#     try:
#         from models import Student
#
#         # 查询学生信息
#         student = db.query(Student).filter(Student.student_id == student_id).first()
#         if not student:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="学生不存在"
#             )
#
#         # 构建响应数据
#         student_data = {
#             "student_id": student.student_id,
#             "student_name": student.student_name or "",
#             "class": student.class_ or ""
#         }
#
#         return StudentInfoResponse(
#             code=200,
#             msg="查询成功",
#             data=student_data
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"获取学生信息失败: {str(e)}"
#         )

# 获取学生详细信息接口
@teacher_router.get("/students/{student_id}", response_model=StudentDetailResponse, summary="获取学生详细信息")
async def get_student_detail(
    student_id: str = Path(..., description="学生ID"),
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    获取指定学生的详细信息

    需要教师身份的JWT认证令牌

    路径参数：
    - student_id: 学生ID（学号）

    返回：
    - id: 学生内部ID
    - student_id: 学号
    - student_name: 姓名
    - class: 班级
    - course_id: 课程ID
    """
    try:
        from models import Student, CourseSelection, Course, Semester

        # 获取学生信息
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学生不存在"
            )

        # 获取当前学期
        current_semester = db.query(Semester).order_by(Semester.semester_id.desc()).first()
        if not current_semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到当前学期"
            )

        # 获取学生在当前学期的课程
        course_selection = db.query(CourseSelection).join(
            Course, CourseSelection.course_id == Course.course_id
        ).filter(
            CourseSelection.student_id == student.id,
            Course.semester_id == current_semester.semester_id
        ).first()

        course_id = course_selection.course_id if course_selection else 0

        return StudentDetailResponse(
            id=student.id,
            student_id=student.student_id,
            student_name=student.student_name,
            class_=student.class_,
            course_id=course_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学生详细信息失败: {str(e)}"
        )

# 学生答题概况接口
@teacher_router.get("/student-profile", response_model=StudentProfileDocResponse, summary="查询学生答题概况")
async def get_student_profile(
    student_id: str = Query(..., description="学生学号"),
    schema_id: int = Query(..., description="数据库模式ID"),
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    根据传入的student_id查询该学生的基本信息与答题概况

    需要教师身份的JWT认证令牌

    查询参数：
    - student_id: 学生学号（如：202322410112）
    - schema_id: 数据库模式ID

    返回：
    - student_id: 学号
    - student_name: 姓名
    - class_name: 所在班级
    - course_id: 课程ID
    - correct_count: 题目正确数量
    - submit_count: 总提交数
    """
    try:
        # 调用服务层方法
        result = teacher_service.get_student_profile_doc(
            student_id=student_id,
            db=db
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学生不存在或未找到相关数据"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学生答题概况失败: {str(e)}"
        )

# 学生题目统计汇总接口
# @teacher_router.get("/problem/statistics", response_model=StudentProblemStatisticsResponse, summary="学生题目统计汇总")
# async def get_problem_statistics(
#     schema_id: int = Query(..., description="数据库模式ID"),
#     semester_id: int = Query(..., description="学期ID"),
#     course_id: Optional[int] = Query(None, description="课程ID（可选，如传则筛选该课程）"),
#     current_user: dict = Depends(get_current_teacher),
#     db: Session = Depends(get_db)
# ):
#     """
#     根据数据库模式、学期，统计每个学生在每道题目的提交及正确情况
#
#     需要教师身份的JWT认证令牌
#
#     查询参数：
#     - schema_id: 数据库模式ID（必填）
#     - semester_id: 学期ID（必填）
#     - course_id: 课程ID（可选，如传则筛选该课程）
#
#     返回：
#     - code: 状态码
#     - msg: 消息
#     - data: 学生题目统计数据列表
#     """
#     try:
#         from models import DatabaseSchema, Problem, AnswerRecord, Student, CourseSelection, Course
#
#         # 验证数据库模式是否存在
#         schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_id == schema_id).first()
#         if not schema:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="数据库模式不存在"
#             )
#
#         # 获取该模式下的所有题目
#         problems = db.query(Problem).filter(Problem.schema_id == schema_id).all()
#         if not problems:
#             return StudentProblemStatisticsResponse(
#                 code=200,
#                 msg="查询成功",
#                 data=[]
#             )
#
#         # 构建学生查询条件
#         student_query = db.query(Student).join(
#             CourseSelection, Student.id == CourseSelection.student_id
#         ).join(
#             Course, CourseSelection.course_id == Course.course_id
#         ).filter(
#             Course.semester_id == semester_id
#         )
#
#         # 如果指定了课程ID，则进一步筛选
#         if course_id is not None:
#             student_query = student_query.filter(Course.course_id == course_id)
#
#         students = student_query.all()
#
#         result_data = []
#         for student in students:
#             for problem in problems:
#                 # 查询该学生在该题目上的所有提交记录
#                 submissions = db.query(AnswerRecord).filter(
#                     AnswerRecord.student_id == student.id,
#                     AnswerRecord.problem_id == problem.problem_id
#                 ).all()
#
#                 # 只有当有提交记录时才添加到结果中
#                 if submissions:
#                     submit_count = len(submissions)
#                     correct_count = sum(1 for s in submissions if s.is_correct)
#
#                     result_data.append({
#                         "student_name": student.student_name or "未知",
#                         "class": student.class_name or "未知班级",
#                         "problem_id": problem.problem_id,
#                         "correct_count": correct_count,
#                         "submit_count": submit_count
#                     })
#
#         return StudentProblemStatisticsResponse(
#             code=200,
#             msg="查询成功",
#             data=result_data
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"获取学生题目统计失败: {str(e)}"
#         )

# 题目完成情况统计接口
@teacher_router.get("/problem/summary", response_model=ProblemSummaryResponse, summary="获取题目完成情况统计")
async def get_problem_summary(
    schema_id: Optional[int] = Query(None, description="数据库模式ID，不指定则返回所有题目"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    返回题目的完成人数和总提交次数

    需要登录认证（只有教师可访问）

    查询参数：
    - schema_id: 数据库模式ID（可选）

    返回：
    - 题目完成情况统计
    """
    try:
        from models import Problem, AnswerRecord
        from sqlalchemy import func, distinct

        # 构建查询
        query = db.query(Problem)
        if schema_id is not None:
            query = query.filter(Problem.schema_id == schema_id)

        problems = query.all()

        problem_summaries = []
        for problem in problems:
            # 统计完成该题目的人数（至少有一次正确提交）
            completed_count = db.query(distinct(AnswerRecord.student_id)).filter(
                AnswerRecord.problem_id == problem.problem_id,
                AnswerRecord.is_correct == True
            ).count()

            # 统计总提交次数
            total_submissions = db.query(AnswerRecord).filter(
                AnswerRecord.problem_id == problem.problem_id
            ).count()

            problem_summaries.append({
                "problem_id": problem.problem_id,
                "problem_content": problem.problem_content or "",
                "completed_count": completed_count,
                "total_submissions": total_submissions
            })

        return ProblemSummaryResponse(
            problems=problem_summaries,
            total_problems=len(problem_summaries)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题目完成情况统计失败: {str(e)}"
        )

# 导出数据接口
@teacher_router.get("/dataset/export", summary="导出数据库模式相关数据")
async def export_dataset(
    schema_name: str = Query(..., description="数据库模式名称"),
    format: str = Query("XLSX", description="导出格式：XLSX、JSON、XML"),
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    导出数据库模式相关数据

    需要教师身份的JWT认证令牌

    查询参数：
    - schema_name: 数据库模式名称
    - format: 导出格式（XLSX、JSON、XML）

    返回：
    - 文件流
    """
    try:
        # 调用服务层方法
        file_data, error_message, media_type = teacher_service.export_dataset(
            schema_name=schema_name,
            format=format,
            db=db
        )

        if file_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # 生成文件名
        from datetime import datetime
        current_year = datetime.now().year
        filename = f"{current_year}-{schema_name}-dataset"

        # 根据格式添加扩展名
        if format.upper() == "XLSX":
            filename += ".xlsx"
        elif format.upper() == "JSON":
            filename += ".json"
        elif format.upper() == "XML":
            filename += ".xml"

        return StreamingResponse(
            file_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出数据失败: {str(e)}"
        )

# 导出指定学生成绩数据接口
@teacher_router.post("/dataset/export-custom", summary="导出指定学生成绩数据")
async def export_custom_student_scores(
    request: StudentScoreExportRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    传入的学生数据导出为表格文件（XLSX）

    需要教师身份的JWT认证令牌

    请求体：
    - students: 学生信息数组，包含学号、姓名、班级、课程ID、分数

    返回：
    - Excel文件流
    """
    try:
        import pandas as pd
        from io import BytesIO
        from datetime import datetime

        # 验证请求数据
        if not request.students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学生数据不能为空"
            )

        # 构建导出数据
        export_data = []
        for student in request.students:
            export_data.append({
                "student_id": student.student_id,
                "student_name": student.student_name,
                "class": student.class_,
                "course_id": student.course_id,
                "score": student.score
            })

        # 生成文件名
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"score-export-{current_date}.xlsx"

        # 创建DataFrame
        df = pd.DataFrame(export_data)

        # 重命名列名
        df.columns = ['学号', '姓名', '班级', '课程号', '分数']

        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='学生成绩')

        output.seek(0)

        return StreamingResponse(
            BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="缺少pandas或openpyxl依赖，无法导出Excel格式"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出学生成绩数据失败: {str(e)}"
        )

# 导出辅助函数已移至 teacher_service.py
# 控制器现在通过服务层处理导出逻辑

# JSON和XML导出函数也已移至服务层

# 查询题目信息接口
@teacher_router.get("/problem/detail", response_model=ProblemDetailResponse, summary="获取题目详情")
async def get_problem_detail(
    problem_id: int = Query(..., description="题目ID"),
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    根据problem_id获取题目详情信息

    需要教师身份的JWT认证令牌

    查询参数：
    - problem_id: 题目ID

    返回：
    - 题目详细信息（包含code、msg、data结构）
    """
    try:
        from models import Problem
        from schemas.teacher import ProblemDetailData

        # 获取题目信息
        problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
        if not problem:
            return ProblemDetailResponse(
                code=404,
                msg="题目不存在",
                data=ProblemDetailData(
                    problem_id=problem_id,
                    title="",
                    problem_content="",
                    example_sql="",
                    is_required=0
                )
            )

        # 生成题目标题（格式：NO.x）
        title = f"NO.{problem.problem_id}"

        # 构建响应数据
        problem_data = ProblemDetailData(
            problem_id=problem.problem_id,
            title=title,
            problem_content=problem.problem_content or "",
            example_sql=problem.example_sql or "",
            is_required=problem.is_required or 0
        )

        return ProblemDetailResponse(
            code=200,
            msg="查询成功",
            data=problem_data
        )

    except Exception as e:
        return ProblemDetailResponse(
            code=500,
            msg=f"获取题目详情失败: {str(e)}",
            data=ProblemDetailData(
                problem_id=problem_id,
                title="",
                problem_content="",
                example_sql="",
                is_required=0
            )
        )

# 编辑题目接口
@teacher_router.put("/problem/edit", response_model=ProblemEditResponse, summary="编辑题目")
async def edit_problem(
    edit_request: ProblemEditRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    根据problem_id更新题目详情信息

    需要教师身份的JWT认证令牌

    请求体：
    - problem_id: 题目ID（必填）
    - problem_content: 题目内容（可选）
    - is_required: 是否必做（可选）
    - example_sql: 示例SQL（可选）

    返回：
    - code: 状态码
    - msg: 消息
    """
    try:
        from models import Problem

        # 获取题目信息
        problem = db.query(Problem).filter(Problem.problem_id == edit_request.problem_id).first()
        if not problem:
            return ProblemEditResponse(
                code=404,
                msg="题目不存在"
            )

        # 更新题目信息
        if edit_request.problem_content is not None:
            problem.problem_content = edit_request.problem_content
        if edit_request.is_required is not None:
            problem.is_required = edit_request.is_required
        if edit_request.example_sql is not None:
            problem.example_sql = edit_request.example_sql

        # 提交更改
        db.commit()
        db.refresh(problem)

        return ProblemEditResponse(
            code=200,
            msg="题目更新成功"
        )

    except Exception as e:
        db.rollback()
        return ProblemEditResponse(
            code=500,
            msg=f"编辑题目失败: {str(e)}"
        )

# 删除题目接口
@teacher_router.delete("/problem/delete", response_model=ProblemDeleteResponse, summary="删除题目")
async def delete_problem(
    problem_id: int = Query(..., description="题目ID"),
    current_user: dict = Depends(get_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    根据problem_id删除题目

    需要管理员身份的JWT认证令牌

    查询参数：
    - problem_id: 题目ID

    返回：
    - code: 状态码
    - msg: 消息
    """
    try:
        from models import Problem, AnswerRecord

        # 获取题目信息
        problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
        if not problem:
            return ProblemDeleteResponse(
                code=404,
                msg="题目不存在"
            )

        # 检查是否有关联的答题记录
        answer_count = db.query(AnswerRecord).filter(AnswerRecord.problem_id == problem_id).count()
        if answer_count > 0:
            return ProblemDeleteResponse(
                code=400,
                msg=f"无法删除题目，存在 {answer_count} 条相关答题记录"
            )

        # 删除题目
        db.delete(problem)
        db.commit()

        return ProblemDeleteResponse(
            code=200,
            msg="题目删除成功"
        )

    except Exception as e:
        db.rollback()
        return ProblemDeleteResponse(
            code=500,
            msg=f"删除题目失败: {str(e)}"
        )
