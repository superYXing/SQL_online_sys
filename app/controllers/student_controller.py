from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.base import get_db
import schemas.student
from schemas.student import (
    StudentProfileResponse, StudentRankItem, AnswerSubmitRequest,
    AnswerSubmitResponse, AnswerRecordsResponse
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
        
        if not student_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到学生信息或学生未选课"
            )
        
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
    获取所有学生的题目完成数与方法数排名
    
    需要登录认证（任何角色都可访问）
    
    返回前10名学生的排名信息：
    - 名次
    - 姓名（包含班级信息）
    - 题目数（答对的题目数量）
    - 方法数（不同答案的数量）
    
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
    current_user: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    获取学生对某一道题目的答题情况
    
    需要学生身份的JWT认证令牌
    
    参数：
    - problem_id: 题目ID
    
    返回学生对该题目的答题情况：
    - submit_count: 总提交次数
    - correct_count: 正确次数
    - wrong_count: 错误次数
    - correct_method_count: 方法次数
    - repeat_method_count: 重复方法数（默认0）
    - syntax_error_count: 语法错误数（默认0）
    - result_error_count: 结果错误数（默认0）
    """
    try:
        # 获取学生数据面板
        dashboard = student_service.get_student_dashboard(
            student_id=current_user["id"],
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

    注意：提交时间戳由服务器自动生成

    返回：
    - is_correct: 答案是否正确
    - message: 提示信息
    - answer_id: 答题记录ID
    """
    try:
        # 提交答案
        is_correct, message, answer_id = student_service.submit_answer(
            student_id=current_user["id"],
            problem_id=answer_data.problem_id,
            answer_content=answer_data.answer_content,
            db=db
        )

        if answer_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return AnswerSubmitResponse(
            is_correct=is_correct,
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

@student_router.get("/answers", response_model=AnswerRecordsResponse, summary="获取答题记录")
async def get_answer_records(
    student_id: Optional[str] = Query(None, description="学生ID（可选）"),
    problem_id: Optional[int] = Query(None, description="题目ID（可选）"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取答题记录

    需要登录认证（任何角色都可访问）

    查询参数：
    - student_id: 学生ID（可选，如果不提供则查询所有学生）
    - problem_id: 题目ID（可选，如果不提供则查询所有题目）
    - page: 页码（默认1）
    - limit: 每页数量（默认20，最大100）

    返回：
    - records: 答题记录列表
    - total: 总记录数
    - page: 当前页码
    - limit: 每页数量

    记录按提交时间倒序排列
    """
    try:
        # 如果是学生角色且没有指定student_id，则只查询自己的记录
        if current_user.get("role") == "student" and not student_id:
            student_id = current_user["id"]

        # 获取答题记录
        records = student_service.get_answer_records(
            student_id=student_id,
            problem_id=problem_id,
            page=page,
            limit=limit,
            db=db
        )

        return records

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取答题记录失败: {str(e)}"
        )