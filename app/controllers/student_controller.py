from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from models.base import get_db
import schemas.student
from schemas.student import (
    StudentProfileResponse, StudentRankItem, AnswerSubmitRequest,
    AnswerSubmitResponse, AnswerRecordsResponse, ProblemListResponse,
    DatabaseSchemaListResponse, DatabaseSchemaItem, AIAnalyzeRequest, AIAnalyzeResponse,
    StudentAnswerRecordsResponse
)
from schemas.response import BaseResponse
from services.student_service import student_service
from services.auth_dependency import get_current_student, get_current_user

student_router = APIRouter(prefix="/student", tags=["学生"])

@student_router.get("/profile", response_model=StudentProfileResponse, summary="获取学生个人信息")
async def get_student_profile(
    current_user: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    获取当前登录学生的基本信息
    
    需要学生身份的JWT认证令牌
    
    返回学生的基本信息包括：
    - 学号
    - 姓名  
    - 班级
    - 当前学期
    - 课序号
    - 任课教师
    """
    try:
        # 获取学生信息
        student_info = student_service.get_student_profile(
            student_id=current_user["id"],
            db=db
        )

        # 服务层已经处理了空数据情况，直接返回结果
        return student_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学生信息失败: {str(e)}"
        )

@student_router.get("/rank", response_model=List[StudentRankItem], summary="获取排行榜")
async def get_student_rank(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取学生的题目完成数与方法数排名前十名

    需要登录认证（所有角色都可访问）

    传入参数：无

    返回前10名学生的排名信息：
    - 名次: 排名位次
    - 姓名: 学生姓名（格式：班级 姓名）
    - 题目数: 答对的题目数量
    - 方法数: 不同答案的数量

    流程：
    1. 调用public接口获取当前学期号
    2. 根据学期号确认课程号范围
    3. 在选课表里根据课程号范围来确定学生名单
    4. 用这些学生进行排序

    排序规则：
    1. 按答对题目数降序
    2. 按方法数降序
    """
    try:
        # 获取排行榜
        rank_list = student_service.get_student_rank(db=db, limit=10)
        
        return rank_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取排行榜失败: {str(e)}"
        ) 

@student_router.get("/dashboard", response_model=schemas.student.StudentDashboardResponse, summary="学生数据面板")
async def get_student_dashboard(
    problem_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取学生对某一道题目的答题情况

    需要登录认证（所有角色都可访问）

    参数：
    - problem_id: 题目ID

    返回学生对该题目的答题情况：
    - submit_count: 总提交次数
    - correct_count: 正确次数
    - wrong_count: 错误次数
    - correct_method_count: 方法数量（不同答案内容的数量）
    - repeat_method_count: 重复方法数（每个方法重复次数之和）
    - syntax_error_count: 语法错误数
    - result_error_count: 结果错误数

    注意：如果当前用户是学生，则查询自己的数据；如果是教师或管理员，需要额外指定学生ID
    """
    try:
        # 根据用户角色确定要查询的学生ID
        if current_user.get("role") == "student":
            # 学生查询自己的数据
            target_student_id = current_user["id"]
        else:
            # 教师或管理员需要指定学生ID（这里暂时使用当前用户ID，实际应该从请求参数获取）
            target_student_id = current_user["id"]

        # 获取学生数据面板
        dashboard = student_service.get_student_dashboard(
            student_id=target_student_id,
            problem_id=problem_id,
            db=db
        )

        return dashboard

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学生数据面板失败: {str(e)}"
        )

@student_router.post("/answer/submit", response_model=AnswerSubmitResponse, summary="提交答题结果")
async def submit_answer(
    answer_data: AnswerSubmitRequest,
    current_user: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    学生提交答题结果

    需要学生身份的JWT认证令牌

    请求参数：
    - problem_id: 题目ID
    - answer_content: 学生提交的SQL答案
    - engine_type: 数据库引擎类型（可选，包括mysql/postgresql/opengauss，默认mysql）

    注意：提交时间戳由服务器自动生成

    返回：
    - is_correct: 答案是否正确
    - message: 提示信息
    - answer_id: 答题记录ID
    """
    try:
        # 提交答案
        result_type, message, answer_id = student_service.submit_answer(
            student_id=current_user["id"],
            problem_id=answer_data.problem_id,
            answer_content=answer_data.answer_content,
            db=db,
            engine_type=answer_data.engine_type or "mysql"
        )

        if answer_id is None or result_type == -1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return AnswerSubmitResponse(
            result_type=result_type,
            message=message,
            answer_id=answer_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交答案失败: {str(e)}"
        )

@student_router.get("/answers", response_model=StudentAnswerRecordsResponse, summary="查询学生答题记录")
async def get_student_answer_records(
    problem_id: int,
    current_user: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    根据题目ID查询当前学生提交的答题记录

    需要学生身份的JWT认证令牌

    参数：
    - problem_id: 题目ID

    返回当前学生对该题目的所有答题记录：
    - student_id: 学生ID
    - problem_id: 题目ID
    - records: 答题记录列表（按提交时间倒序排列）
      - answer_record_id: 答题记录ID
      - result_type: 结果类型（0:正确 1:语法错误 2:结果错误）
      - answer_content: 答题内容
      - timestep: 提交时间
    """
    try:
        # 获取学生答题记录
        records = student_service.get_student_answer_records(
            student_id=current_user["id"],
            problem_id=problem_id,
            db=db
        )

        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到答题记录"
            )

        return records

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取答题记录失败: {str(e)}"
        )

# 已删除: 获取答题记录列表接口 - 功能已整合到其他接口

# 题目列表接口已移至 /public 路径
# 请使用 GET /public/problem/list 替代此接口

@student_router.get("/schema/list", response_model=List[DatabaseSchemaItem], summary="获取所有数据库模式（学生版）")
async def get_database_schemas_for_student(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有数据库模式（学生版）
    
    需要登录认证（所有角色都可访问）
    
    根据database_schema.status来获得数据库模式，0则不获得，1为获得
    
    返回启用状态的数据库模式列表：
    - schema_id: 模式ID
    - schema_name: 模式名称
    - schema_description: 模式描述
    - schema_author: 模式作者
    """
    try:
        # 获取启用状态的数据库模式列表
        schemas_response = student_service.get_active_database_schemas(db=db)
        
        # 直接返回schemas数组，符合用户要求的响应格式
        return schemas_response.schemas
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库模式列表失败: {str(e)}"
        )

@student_router.post("/answer/ai-analyze", summary="AI分析SQL语句（流式输出）")
async def ai_analyze_sql(
    request: AIAnalyzeRequest,
    current_user: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    AI智能分析题目解答情况（流式输出）

    需要用户身份的JWT认证令牌

    请求参数：
    - problem_id: 题目ID
    - answer_content: 学生提交的答案内容（SQL或其他文字）

    返回：
    流式响应，每个数据块格式为：
    data: {"type": "content", "content": "分析内容片段"}
    data: {"type": "done"}
    """

    async def generate_ai_response():
        """生成AI分析的流式响应"""
        try:
            from services.ai_service import ai_service

            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'message': '开始AI分析...'}, ensure_ascii=False)}\n\n"

            # 调用AI服务进行流式分析
            async for chunk in ai_service.analyze_sql_answer_stream(
                problem_id=request.problem_id,
                answer_content=request.answer_content,
                student_id=current_user["id"],
                db=db
            ):
                if chunk:
                    # 发送内容块
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

        except Exception as e:
            # 发送错误信息
            error_msg = f"AI分析失败: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_ai_response(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )