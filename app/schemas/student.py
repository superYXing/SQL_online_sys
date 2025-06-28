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
    correct_method_count: int  # 方法次数
    wrong_count: int  # 错误次数
    correct_count: int  # 正确次数
    repeat_method_count: int = 0  # 默认返回0，暂不添加sql查询逻辑
    syntax_error_count: int = 0  # 默认返回0，暂不添加sql查询逻辑
    result_error_count: int = 0  # 默认返回0，暂不添加sql查询逻辑
    
    class Config:
        from_attributes = True

class StudentDashboardResponse(BaseModel):
    """学生数据面板响应模型"""
    problems: List[StudentDashboardItem]

    class Config:
        from_attributes = True

class AnswerSubmitRequest(BaseModel):
    """答题提交请求模型"""
    problem_id: int
    answer_content: str

    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": 5,
                "answer_content": "SELECT * FROM employees;"
            }
        }

class AnswerSubmitResponse(BaseModel):
    """答题提交响应模型"""
    is_correct: bool
    message: str
    answer_id: int

    class Config:
        from_attributes = True

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