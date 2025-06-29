from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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
    course_id: int
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

# 教师端题目和模式相关响应模型
class TeacherProblemItem(BaseModel):
    """教师端题目项模型"""
    problem_id: int
    is_required: int
    problem_content: str

    class Config:
        from_attributes = True

class TeacherProblemListResponse(BaseModel):
    """教师端题目列表响应模型"""
    schema_name: str
    problems: List[TeacherProblemItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_name": "ORACLE_HR",
                "problems": [
                    {
                        "problem_id": 5,
                        "is_required": 1,
                        "problem_content": "查询所有员工信息"
                    },
                    {
                        "problem_id": 6,
                        "is_required": 0,
                        "problem_content": "查询部门平均薪资"
                    }
                ]
            }
        }

class TeacherSchemaItem(BaseModel):
    """教师端数据库模式项模型"""
    schema_id: int
    schema_name: str

    class Config:
        from_attributes = True

class TeacherSchemaListResponse(BaseModel):
    """教师端数据库模式列表响应模型"""
    schemas: List[TeacherSchemaItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": [
                {
                    "schema_id": 1,
                    "schema_name": "ORACLE_HR"
                },
                {
                    "schema_id": 2,
                    "schema_name": "DATABASE_HR"
                }
            ]
        }

# SQL查询相关模型
class SQLQueryRequest(BaseModel):
    """SQL查询请求模型"""
    sql: str
    schema_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "sql": "SELECT * FROM employees LIMIT 10",
                "schema_id": 1
            }
        }

class SQLQueryResponse(BaseModel):
    """SQL查询响应模型"""
    success: bool
    data: Optional[List[Dict]] = None
    columns: Optional[List[str]] = None
    row_count: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {"id": 1, "name": "张三", "department": "技术部"},
                    {"id": 2, "name": "李四", "department": "市场部"}
                ],
                "columns": ["id", "name", "department"],
                "row_count": 2,
                "error_message": None
            }
        }

# 学期相关模型
class SemesterItem(BaseModel):
    """学期项模型"""
    semester_id: int
    semester_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    class Config:
        from_attributes = True

class SemesterListResponse(BaseModel):
    """学期列表响应模型"""
    semesters: List[SemesterItem]
    total: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "semesters": [
                    {
                        "semester_id": 1,
                        "semester_name": "2024年春季学期",
                        "start_date": "2024-02-26",
                        "end_date": "2024-07-15"
                    }
                ],
                "total": 1
            }
        }

# 态势矩阵相关模型
class SchemaStats(BaseModel):
    """数据库模式统计模型"""
    student_count: int
    problem_count: int
    submission_count: int

    class Config:
        from_attributes = True

class SemesterMatrix(BaseModel):
    """学期矩阵模型"""
    semester: str
    schemas: Dict[str, SchemaStats]

    class Config:
        from_attributes = True

class DashboardMatrixResponse(BaseModel):
    """态势矩阵响应模型"""
    code: int = 200
    msg: str = "查询成功"
    matrix: List[SemesterMatrix]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "matrix": [
                    {
                        "semester": "2025春季",
                        "schemas": {
                            "test": {
                                "student_count": 50,
                                "problem_count": 120,
                                "submission_count": 300
                            },
                            "ORACLE_HR": {
                                "student_count": 45,
                                "problem_count": 110,
                                "submission_count": 280
                            }
                        }
                    }
                ]
            }
        }

# 学生题目提交情况相关模型
class StudentProblemStatsRequest(BaseModel):
    """学生题目提交情况查询请求模型"""
    student_ids: List[str]
    problem_ids: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "student_ids": ["20222241236", "20212261879", "202362618852"],
                "problem_ids": ["1", "2", "3"]
            }
        }

class StudentProblemStat(BaseModel):
    """学生题目统计模型"""
    student_id: str
    problem_id: str
    submit_count: int
    correct_count: int

    class Config:
        from_attributes = True

class StudentProblemStatsResponse(BaseModel):
    """学生题目提交情况响应模型"""
    data: List[StudentProblemStat]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "student_id": "20222241236",
                        "problem_id": "2",
                        "submit_count": 1,
                        "correct_count": 1
                    },
                    {
                        "student_id": "20212261879",
                        "problem_id": "2",
                        "submit_count": 1,
                        "correct_count": 1
                    }
                ]
            }
        }

# 提交记录模型（保留用于其他接口）
class SubmissionRecord(BaseModel):
    """提交记录模型"""
    submission_time: str
    sql_content: str
    is_correct: bool
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# 学生答题概况相关模型
class StudentProfileResponse(BaseModel):
    """学生答题概况响应模型"""
    student_id: str
    student_name: str
    class_name: str
    total_problems: int
    completed_problems: int
    correct_problems: int
    completion_rate: float
    accuracy_rate: float
    last_submission_time: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": "20232251177",
                "student_name": "张三",
                "class_name": "计算机科学与技术1班",
                "total_problems": 10,
                "completed_problems": 8,
                "correct_problems": 6,
                "completion_rate": 80.0,
                "accuracy_rate": 75.0,
                "last_submission_time": "2024-03-15 14:30:00"
            }
        }

# 题目统计相关模型
class ProblemStatItem(BaseModel):
    """题目统计项模型"""
    problem_id: int
    problem_content: str
    total_submissions: int
    correct_submissions: int
    unique_students: int
    accuracy_rate: float

    class Config:
        from_attributes = True

class ProblemStatisticsResponse(BaseModel):
    """题目统计响应模型"""
    schema_id: int
    schema_name: str
    problems: List[ProblemStatItem]
    total_problems: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_id": 1,
                "schema_name": "ORACLE_HR",
                "problems": [
                    {
                        "problem_id": 5,
                        "problem_content": "查询所有员工信息",
                        "total_submissions": 150,
                        "correct_submissions": 120,
                        "unique_students": 50,
                        "accuracy_rate": 80.0
                    }
                ],
                "total_problems": 1
            }
        }

# 题目完成情况统计相关模型
class ProblemSummaryItem(BaseModel):
    """题目完成情况统计项模型"""
    problem_id: int
    problem_content: str
    completed_count: int
    total_submissions: int

    class Config:
        from_attributes = True

class ProblemSummaryResponse(BaseModel):
    """题目完成情况统计响应模型"""
    problems: List[ProblemSummaryItem]
    total_problems: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "problems": [
                    {
                        "problem_id": 5,
                        "problem_content": "查询所有员工信息",
                        "completed_count": 35,
                        "total_submissions": 150
                    }
                ],
                "total_problems": 1
            }
        }

# 数据导出相关模型
class DatasetExportResponse(BaseModel):
    """数据导出响应模型"""
    schema_id: int
    schema_name: str
    export_data: Dict
    filename: str
    export_time: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_id": 1,
                "schema_name": "ORACLE_HR",
                "export_data": {
                    "tables": ["employees", "departments"],
                    "problems": 10,
                    "students": 50
                },
                "filename": "ORACLE_HR_export_20240315.json",
                "export_time": "2024-03-15 14:30:00"
            }
        }

# 题目详情和编辑相关模型
class ProblemDetailResponse(BaseModel):
    """题目详情响应模型"""
    problem_id: int
    problem_content: str
    is_required: int
    schema_id: int
    schema_name: str
    example_sql: Optional[str] = None
    created_time: Optional[str] = None
    updated_time: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "problem_id": 5,
                "problem_content": "查询所有员工信息",
                "is_required": 1,
                "schema_id": 1,
                "schema_name": "ORACLE_HR",
                "example_sql": "SELECT * FROM employees",
                "created_time": "2024-01-01 00:00:00",
                "updated_time": "2024-03-15 14:30:00"
            }
        }

class ProblemEditRequest(BaseModel):
    """题目编辑请求模型"""
    problem_content: Optional[str] = None
    is_required: Optional[int] = None
    example_sql: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "problem_content": "查询所有员工的姓名和部门信息",
                "is_required": 1,
                "example_sql": "SELECT name, department FROM employees"
            }
        }

class ProblemEditResponse(BaseModel):
    """题目编辑响应模型"""
    success: bool
    message: str
    problem: Optional[ProblemDetailResponse] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "题目更新成功",
                "problem": {
                    "problem_id": 5,
                    "problem_content": "查询所有员工的姓名和部门信息",
                    "is_required": 1,
                    "schema_id": 1,
                    "schema_name": "ORACLE_HR"
                }
            }
        }

# 教师端学生列表相关模型
class TeacherStudentInfo(BaseModel):
    """教师端学生信息模型"""
    student_id: str
    student_name: str
    class_: str
    teacher_name: str
    semester_name: str
    course_id: str

    class Config:
        from_attributes = True

class TeacherStudentListResponse(BaseModel):
    """教师端学生列表响应模型"""
    students: List[TeacherStudentInfo]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "students": [
                    {
                        "student_id": "20232251177",
                        "student_name": "张三",
                        "class_": "计算机科学与技术1班",
                        "teacher_name": "赵欧式",
                        "semester_name": "2025年春季",
                        "course_id": "1"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 20
            }
        }

# 导出分数相关模型
class ExportStudentInfo(BaseModel):
    """导出学生信息模型"""
    student_id: str
    student_name: str
    class_: str = Field(..., alias="class")
    course_id: str
    total_score: int
    status: str

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "student_id": "20232241177",
                "student_name": "张三",
                "class": "软件2301",
                "course_id": "03",
                "total_score": 85,
                "status": "正常"
            }
        }

class ScoreExportRequest(BaseModel):
    """分数导出请求模型"""
    students: List[ExportStudentInfo]

    class Config:
        json_schema_extra = {
            "example": {
                "students": [
                    {
                        "student_id": "20232241177",
                        "student_name": "张三",
                        "class": "软件2301",
                        "course_id": "03",
                        "total_score": 85,
                        "status": "正常"
                    },
                    {
                        "student_id": "20232241178",
                        "student_name": "李四",
                        "class": "软件2302",
                        "course_id": "03",
                        "total_score": 100,
                        "status": "正常"
                    }
                ]
            }
        }
