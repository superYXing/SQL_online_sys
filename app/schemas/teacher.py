from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TeacherProfileResponse(BaseModel):
    """教师个人信息响应模型"""
    teacher_id: str
    teacher_name: str
    semester_name: str


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "teacher_id": "201992012",
                "teacher_name": "刘晓",
                "semester_name": "2025年春季",
            }
        }

class CourseInfo(BaseModel):
    """课程信息模型"""
    course_id: str
    course_name: str
    semester_name: str
    student_count: int
    
    class Config:
        from_attributes = True

class TeacherCourseListResponse(BaseModel):
    """教师课程列表响应模型"""
    courses: List[CourseInfo]
    total: int
    
    class Config:
        from_attributes = True

class StudentGradeInfo(BaseModel):
    """学生成绩信息模型"""
    student_id: str
    student_name: str
    class_name: str
    total_problems: int
    correct_problems: int
    score: float
    
    class Config:
        from_attributes = True

class CourseGradeResponse(BaseModel):
    """课程成绩响应模型"""
    course_id: str
    course_name: str
    students: List[StudentGradeInfo]
    total_students: int

    class Config:
        from_attributes = True

# 学生管理相关模型
class StudentCreateRequest(BaseModel):
    """教师创建学生请求模型"""
    student_id: str
    student_name: str
    class_: str
    student_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "20232251177",
                "student_name": "张三",
                "class_": "计算机科学与技术1班",
                "student_password": "123456"
            }
        }

class StudentCreateResponse(BaseModel):
    """学生创建响应模型"""
    id: int
    student_id: str
    student_name: str
    class_: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": "20232251177",
                "student_name": "张三",
                "class_": "计算机科学与技术1班"
            }
        }

class ImportFailDetail(BaseModel):
    """导入失败详情模型"""
    row: int
    reason: str

    class Config:
        from_attributes = True

class StudentImportResponse(BaseModel):
    """学生批量导入响应模型"""
    code: int = 200
    msg: str
    success_count: int
    fail_count: int
    fail_details: List[ImportFailDetail]

    class Config:
        from_attributes = True

# 分数核算相关模型
class ScoreCalculateRequest(BaseModel):
    """分数核算请求模型"""
    problem_ids: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "problem_ids": [5, 6, 7, 8]
            }
        }

class StudentScoreInfo(BaseModel):
    """学生分数信息模型"""
    course_id: str
    student_id: str
    student_name: str
    class_: str = ""
    total_score: int

    class Config:
        from_attributes = True

class ScoreUpdateResponse(BaseModel):
    """分数更新响应模型"""
    code: int = 200
    msg: str = "更新分数成功"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "更新分数成功"
            }
        }

class ScoreListResponse(BaseModel):
    """学生分数列表响应模型"""
    code: int = 200
    msg: str = ""
    scorelist: List[StudentScoreInfo]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "",
                "scorelist": [
                    {
                        "course_id": "03",
                        "student_id": "1",
                        "student_name": "王欧式",
                        "class": "软件2211班",
                        "total_score": 85
                    }
                ]
            }
        }
