import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File
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
    StudentProblemStatsRequest, StudentProblemStatsResponse,
    StudentProfileResponse, ProblemStatisticsResponse, ProblemSummaryResponse, ProblemSummaryDocResponse, ProblemSummaryData,
    DatasetExportResponse, ProblemDetailResponse, ProblemEditRequest, ProblemEditResponse,
    TeacherStudentListResponse, ScoreExportRequest, ExportStudentInfo,
    StudentProblemStatisticsResponse, StudentInfoResponse, StudentProfileNewResponse,
    StudentProfileDocResponse, StudentDetailResponse, StudentScoreExportRequest,
    ProblemDeleteResponse, StudentCourseAddRequest, StudentCourseAddResponse,
    SchemaCreateRequest, SchemaCreateResponse, SQLQueryRequest, SQLQueryResponse
)
from schemas.admin import StudentInfo, StudentListResponse, OperationResponse
from schemas.response import BaseResponse
from services.teacher_service import teacher_service
from services.user_management_service import user_management_service
from services.student_service import student_service
from services.auth_dependency import get_current_teacher, get_current_user, get_current_admin, get_current_teacher_or_admin

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

# 已删除: 获取教师课程列表接口 - 功能已整合到其他接口
# 已删除: 获取课程成绩接口 - 功能已整合到其他接口
# 已删除: 导出课程成绩接口 - 功能已整合到其他接口

# 学生管理接口
@teacher_router.post("/students/addcourse", response_model=StudentCourseAddResponse, summary="添加学生选课信息")
async def add_student_course(
    course_data: StudentCourseAddRequest,
    current_user: dict = Depends(get_current_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    创建新的学生选课信息

    需要教师或管理员身份的JWT认证令牌

    请求参数：
    - student_id: 学生ID（学号）
    - student_name: 学生姓名
    - class_: 班级
    - status: 状态（0为重修，1为正常）
    - course_id: 课程ID

    逻辑：
    - 先在学生表里创建一条学生信息，包括学号，姓名，班级，默认密码为"default@password"
    - 之后在选课表里增加信息，包括学生id（学生表外键），课程id（课程表外键），
      状态（0为重修，1为正常），学期id（学期表外键），分数（默认0）
    - 注意学期id用public接口获取当前学期id

    返回：
    - code: 状态码
    - msg: 消息
    """
    try:
        success, message, response = teacher_service.add_student_course(
            teacher_id=current_user["id"],
            course_data=course_data,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加学生选课信息失败: {str(e)}"
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

# SQL查询接口已移至文件末尾，避免重复定义



# 已删除: 态势矩阵接口 - 接口已废弃

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
    - data: 学生题目统计数据列表，包含每个学生在每个题目上的：
      - submit_count: 提交次数
      - correct_count: 正确次数
      - syntax_error_count: 语法错误次数
      - result_error_count: 结果错误次数
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

                # 统计各种类型的提交次数
                submit_count = len(submissions)
                correct_count = sum(1 for s in submissions if s.result_type == 0)  # 使用result_type字段
                syntax_error_count = sum(1 for s in submissions if s.result_type == 1)  # 语法错误
                result_error_count = sum(1 for s in submissions if s.result_type == 2)  # 结果错误

                # 只有当有提交记录时才添加到结果中
                if submit_count > 0:
                    result_data.append({
                        "student_id": student_id,
                        "problem_id": problem_id_str,
                        "submit_count": submit_count,
                        "correct_count": correct_count,
                        "syntax_error_count": syntax_error_count,
                        "result_error_count": result_error_count
                    })

        return StudentProblemStatsResponse(data=result_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询学生题目提交情况失败: {str(e)}"
        )

# 已删除: 获取学生信息接口 - 功能已整合到其他接口

# 已删除: 获取学生详细信息接口 - 功能已整合到其他接口

# 学生答题概况接口
@teacher_router.get("/student-profile", response_model=StudentProfileDocResponse, summary="查询学生答题概况")
async def get_student_profile(
    student_id: str = Query(..., description="学生学号"),
    schema_id: int = Query(..., description="数据库模式ID"),
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    根据传入的student_id和schema_id查询该学生的基本信息与答题概况

    需要教师身份的JWT认证令牌

    查询参数：
    - student_id: 学生学号（如：202322410112）
    - schema_id: 数据库模式ID

    返回：
    - student_id: 学号
    - student_name: 姓名
    - class_name: 所在班级
    - course_id: 课程ID
    - status: 选课状态，0为重修，1为正常
    - correct_count: 题目正确数量
    - submit_count: 总提交数

    执行流程：
    1. 调用public接口获取当前学期号
    2. 根据学期号确认课程号范围
    3. 根据学号在课程号范围里确认课程号(使用.first())
    4. 根据数据库模式id得到题目id范围
    5. 到答题记录表里根据学号和课程的时间范围和题目的范围确认答题的正确数量和总提交数
    """
    try:
        # 调用服务层方法
        result = teacher_service.get_student_profile_doc(
            student_id=student_id,
            schema_id=schema_id,
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

# 已删除: 学生题目统计汇总接口 - 功能已整合到其他接口

# 题目完成情况统计接口
@teacher_router.get("/problem/summary", response_model=ProblemSummaryDocResponse, summary="获取题目完成情况统计")
async def get_problem_summary(
    problem_id: int = Query(..., description="题目ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据题目ID返回该题目的完成人数和总提交次数

    权限要求：需登录，仅教师角色可访问
    认证方式：必须附带JWT令牌

    请求参数：
    - problem_id: 题目ID（必须）

    返回：
    - code: 状态码（200表示成功）
    - msg: 消息（"查询成功"）
    - data: 题目统计数据
      - problem_id: 题目ID
      - completed_student_count: 完成此题目的学生人数
      - total_submission_count: 此题目的总提交次数
    """
    try:
        from models import Problem, AnswerRecord
        from sqlalchemy import func, distinct

        # 检查题目是否存在
        problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
        if not problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题目不存在"
            )

        # 统计完成该题目的学生人数（至少有一次正确提交）
        # 使用result_type == 0 表示正确
        completed_student_count = db.query(distinct(AnswerRecord.student_id)).filter(
            AnswerRecord.problem_id == problem_id,
            AnswerRecord.result_type == 0
        ).count()

        # 统计该题目的总提交次数
        total_submission_count = db.query(AnswerRecord).filter(
            AnswerRecord.problem_id == problem_id
        ).count()

        # 构建响应数据
        data = ProblemSummaryData(
            problem_id=problem_id,
            completed_student_count=completed_student_count,
            total_submission_count=total_submission_count
        )

        return ProblemSummaryDocResponse(
            code=200,
            msg="查询成功",
            data=data
        )

    except HTTPException:
        raise
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
                    is_required=0,
                    is_ordered=0,
                    problem_content="",
                    example_sql=""
                )
            )

        # 构建响应数据
        problem_data = ProblemDetailData(
            problem_id=problem.problem_id,
            is_required=problem.is_required or 0,
            is_ordered=problem.is_orderd or 0,  # 注意数据库字段名的拼写
            problem_content=problem.problem_content or "",
            example_sql=problem.example_sql or ""
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
                is_required=0,
                is_ordered=0,
                problem_content="",
                example_sql=""
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
    - is_required: 是否必做（可选）
    - is_ordered: 是否有序（可选）
    - problem_content: 题目内容（可选）
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
        if edit_request.is_required is not None:
            problem.is_required = edit_request.is_required
        if edit_request.is_ordered is not None:
            problem.is_orderd = edit_request.is_ordered  # 注意数据库字段名的拼写
        if edit_request.problem_content is not None:
            problem.problem_content = edit_request.problem_content
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

    需要教师或管理员身份的JWT认证令牌

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

# 数据库模式管理接口
@teacher_router.post("/schema/create", response_model=SchemaCreateResponse, summary="创建数据库模式")
async def create_database_schema(
    schema_data: SchemaCreateRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    根据HTML格式文本、数据库模式名称、SQL引擎和SQL文本创建数据库模式

    需要教师身份的JWT认证令牌

    请求参数（JSON格式）：
    - html_content: HTML格式文本（必须）
    - schema_name: 数据库模式名称（必须）
    - sql_engine: SQL引擎类型（必须，如：mysql, postgresql, opengauss）
    - sql_schema: 创建数据库模式时的名称（必须）
    - sql_file_content: SQL建表语句文本（必须）

    返回：
    - code: 状态码（200表示成功）
    - msg: 消息（"创建数据库模式成功"）

    执行流程：
    1. 判断此模式是否已经存在，如果存在则结束流程
    2. 如果不存在，连接指定的SQL引擎
    3. 执行SQL文本中的建表语句
    4. 执行成功后将数据插入到database_schema表中
    """
    try:
        # 验证SQL文本内容
        if not schema_data.sql_file_content or not schema_data.sql_file_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL文本内容不能为空"
            )

        success, message, response = teacher_service.create_database_schema(
            teacher_id=current_user["id"],
            schema_data=schema_data,
            db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建数据库模式失败: {str(e)}"
        )

@teacher_router.post("/schema/query", response_model=SQLQueryResponse, summary="执行SQL查询")
async def execute_sql_query(
    query_data: SQLQueryRequest,
    current_user: dict = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    接收前端输入的SQL语句，由后端执行并返回查询结果

    需要教师身份的JWT认证令牌

    请求参数：
    - schema_id: 数据库模式ID
    - sql: 前端输入的SQL语句

    返回：
    - code: 状态码（200表示成功）
    - msg: 消息（"查询成功"）
    - columns: 列名数组
    - rows: 数据行数组（二维数组）

    执行流程：
    1. 根据schema_id获取sql_schema字段
    2. 连接PostgreSQL引擎
    3. 执行USE {sql_schema}语句（如果sql_schema存在）
    4. 执行用户的SQL语句
    5. 返回查询结果
    """
    try:
        result = teacher_service.execute_sql_query(
            teacher_id=current_user["id"],
            query_data=query_data,
            db=db
        )

        return result

    except Exception as e:
        return SQLQueryResponse(
            code=500,
            msg=f"执行SQL查询失败: {str(e)}",
            columns=[],
            rows=[]
        )
