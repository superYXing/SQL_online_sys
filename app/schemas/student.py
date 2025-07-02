from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StudentProfileResponse(BaseModel):
    """学生个人信息响应模型"""
    学号: str
    姓名: str
    班级: Optional[str]
    当前学期: str
    课序号: str
    任课教师: str
    
    class Config:
        from_attributes = True

class StudentRankItem(BaseModel):
    """学生排名项模型"""
    名次: int
    姓名: str
    题目数: int
    方法数: int
    
    class Config:
        from_attributes = True

# 直接使用 List[StudentRankItem] 作为响应类型，不需要单独的 RootModel
StudentRankResponse = List[StudentRankItem]

class StudentDashboardItem(BaseModel):
    """学生数据面板项模型"""
    problem_id: int
    submit_count: int  # 总提交次数
    correct_count: int  # 正确次数
    wrong_count: int  # 错误次数
    correct_method_count: int  # 方法数量（不同答案内容的数量）
    repeat_method_count: int  # 重复方法数（每个方法重复次数之和）
    syntax_error_count: int  # 语法错误数
    result_error_count: int  # 结果错误数

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "problem_id": 5,
                "submit_count": 10,
                "correct_count": 3,
                "wrong_count": 7,
                "correct_method_count": 4,
                "repeat_method_count": 6,
                "syntax_error_count": 2,
                "result_error_count": 5
            }
        }

class StudentDashboardResponse(BaseModel):
    """学生数据面板响应模型"""
    problems: List[StudentDashboardItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "problems": [
                    {
                        "problem_id": 5,
                        "submit_count": 10,
                        "correct_count": 3,
                        "wrong_count": 7,
                        "correct_method_count": 4,
                        "repeat_method_count": 6,
                        "syntax_error_count": 2,
                        "result_error_count": 5
                    }
                ]
            }
        }

class AnswerSubmitRequest(BaseModel):
    """答题提交请求模型"""
    problem_id: int
    answer_content: str
    engine_type: Optional[str] = "mysql"  # 可选，包括mysql/postgresql/opengauss

    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": 5,
                "answer_content": "SELECT * FROM employees;",
                "engine_type": "mysql"
            }
        }

class AnswerSubmitResponse(BaseModel):
    """答题提交响应模型"""
    is_correct: bool
    message: str
    answer_id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "is_correct": True,
                "message": "结果正确",
                "answer_id": 123
            }
        }

class AnswerRecordItem(BaseModel):
    """答题记录项模型"""
    answer_id: int
    problem_id: int
    answer_content: str
    is_correct: int
    submit_time: datetime

    class Config:
        from_attributes = True

class AnswerRecordsResponse(BaseModel):
    """答题记录响应模型"""
    records: List[AnswerRecordItem]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True

class ProblemItem(BaseModel):
    """题目项模型"""
    problem_id: int
    problem_content: str
    is_required: int
    schema_id: int

    class Config:
        from_attributes = True

class ProblemListResponse(BaseModel):
    """题目列表响应模型"""
    problems: List[ProblemItem]
    total: int
    schema_id: Optional[int] = None

    class Config:
        from_attributes = True

class DatabaseSchemaItem(BaseModel):
    """数据库模式项模型"""
    schema_id: int
    schema_name: Optional[str]
    schema_description: Optional[str]

    class Config:
        from_attributes = True

class DatabaseSchemaListResponse(BaseModel):
    """数据库模式列表响应模型"""
    schemas: List[DatabaseSchemaItem]
    total: int

    class Config:
        from_attributes = True

class AIAnalyzeRequest(BaseModel):
    """AI分析请求模型"""
    problem_id: int
    answer_content: str

    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": 5,
                "answer_content": "SELECT * FROM employees;"
            }
        }

class AIAnalyzeResponse(BaseModel):
    """AI分析响应模型"""
    code: int
    message: str
    ai_content: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "请求成功！",
                "ai_content": "您的SQL语句语法正确，能够查询出所有员工的信息。建议可以尝试使用WHERE子句来筛选特定条件的员工，或者使用ORDER BY来排序结果。"
            }
        }